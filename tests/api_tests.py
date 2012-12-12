'''
Created on Nov 5, 2012

@author: jluker
'''

import os
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #@UndefinedVariable

import fixtures
import unittest2
from simplejson import loads
from werkzeug import Headers #@UnresolvedImport
from simplejson import loads

from flask import request, g
from adsabs.app import create_app
from adsabs.modules.user import AdsUser
from adsabs.modules.api import ApiSearchRequest
from adsabs.modules.api.permissions import DevPermissions as DP
from adsabs.modules.api.forms import ApiQueryForm
from adsabs.core.solr import SolrResponse
from config import config
from tests.utils import *
        
class APITests(unittest2.TestCase, fixtures.TestWithFixtures):

    def setUp(self):
        config.TESTING = True
        config.MONGOALCHEMY_DATABASE = 'test'
        self.app = create_app(config)
        
        from adsabs.extensions import mongodb
        mongodb.session.db.connection.drop_database('test') #@UndefinedVariable
        
        self.insert_user = user_creator()
            
        self.client = self.app.test_client()
        
        
    def test_empty_requests(self):
        
        rv = self.client.get('/api/')
        self.assertEqual(rv.status_code, 404)
        
        rv = self.client.get('/api/search')
        self.assertEqual(rv.status_code, 301)
    
        rv = self.client.get('/api/search/')
        self.assertEqual(rv.status_code, 401)
        
        rv = self.client.get('/api/record/')
        self.assertEqual(rv.status_code, 404)
        
        
    def test_unauthorized_request(self):
        
        rv = self.client.get('/api/search/?q=black+holes')
        self.assertEqual(rv.status_code, 401)
        self.assertIn("API authentication failed: no developer token provided", rv.data)
        
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo')
        self.assertEqual(rv.status_code, 401)
        self.assertIn("API authentication failed: unknown user", rv.data)
        
        rv = self.client.get('/api/record/1234')
        self.assertEqual(rv.status_code, 401)
        
    def test_authorized_request(self):
        
        self.insert_user("foo", developer=True)
        
        fixture = self.useFixture(SolrRawQueryFixture())
        
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key')
        self.assertEqual(rv.status_code, 200)
        
        rv = self.client.get('/api/record/1234?dev_key=foo_dev_key')
        self.assertEqual(rv.status_code, 200)
        
    def test_search_output(self):
        
        self.insert_user("foo", developer=True)
        fixture = self.useFixture(SolrRawQueryFixture())
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key')
        resp_data = loads(rv.data)
        self.assertIn('meta', resp_data)
        self.assertIn('results', resp_data)
        self.assertTrue(resp_data['meta']['count'] >= 1)
        self.assertIsInstance(resp_data['results']['docs'], list)
        
        self.insert_user("bar", developer=True, dev_perms={'facets': True})
        rv = self.client.get('/api/search/?q=black+holes&dev_key=bar_dev_key')
        resp_data = loads(rv.data)
        self.assertIn('facets', resp_data['results'])
    
    def test_record_output(self):
        
        self.insert_user("foo", developer=True)
        
        fixture_data = SolrRawQueryFixture.default_response()
        fixture_data['response']['docs'][0]['title'] = 'Foo Bar Polarization'
        fixture = self.useFixture(SolrRawQueryFixture(fixture_data))
        rv = self.client.get('/api/record/2012ApJ...751...88M?dev_key=foo_dev_key')
        resp_data = loads(rv.data)
        self.assertIn("Polarization", resp_data['title'])
        
        fixture_data['response']['numFound'] = 0
        fixture = self.useFixture(SolrRawQueryFixture(fixture_data))
        rv = self.client.get('/api/record/2012ApJ...751...88M?dev_key=foo_dev_key')
        self.assertEqual(rv.status_code, 404)
        self.assertIn("No record found with identifier 2012ApJ...751...88M", rv.data)
        
        
        return
    
    def test_content_types(self):
        
        self.insert_user("foo", developer=True)
        
        fixture = self.useFixture(SolrRawQueryFixture())
        
        # default should be json
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key')
        self.assertIn('application/json', rv.content_type)
        
        rv = self.client.get('/api/record/2012ApJ...751...88M?dev_key=foo_dev_key')
        self.assertIn('application/json', rv.content_type)
    
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key', headers=Headers({'Accept': 'application/json'}))
        self.assertIn('application/json', rv.content_type)
    
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key', headers=Headers({'Accept': 'application/xml'}))
        self.assertIn('text/xml', rv.content_type)
    
        rv = self.client.get('/api/record/2012ApJ...751...88M?dev_key=foo_dev_key', headers=Headers({'Accept': 'application/xml'}))
        self.assertIn('text/xml', rv.content_type)
    
        rv = self.client.get('/api/record/2012ApJ...751...88M?dev_key=foo_dev_key')
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key&format=xml')
        self.assertIn('text/xml', rv.content_type)
        
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key&format=blah')
        self.assertEqual(rv.status_code, 406)
        self.assertIn('renderer does not exist', rv.data)
        
    def test_request_creation(self):
        
        self.insert_user("foo", developer=True)
        fixture = self.useFixture(GlobalApiUserFixture("foo_dev_key"))
        
        with self.app.test_request_context('/api/search/?dev_key=foo_dev_key&q=black+holes'):
            self.app.preprocess_request()
            fixture.set_api_user()
            req = ApiSearchRequest(request.values)
            solr_req = req.create_solr_request()
            self.assertEquals(solr_req.params.q, 'black holes')
        
    def test_validation(self):
        
        self.insert_user("foo", developer=True)
        fixture = self.useFixture(GlobalApiUserFixture("foo_dev_key"))
        
        def validate(qstring, errors=None):
            with self.app.test_request_context('/api/search/?dev_key=foo_dev_key&%s' % qstring):
                form = ApiQueryForm(request.values, csrf_enabled=False)
                valid = form.validate()
                return valid
            
        not_valid = lambda x: self.assertFalse(validate(x))
        is_valid = lambda x: self.assertTrue(validate(x))
        
        is_valid('q=black+holes')
        not_valid('q=a')
        not_valid('q=%s' % ("foobar" * 1000))
        for f in config.API_SOLR_FIELDS:
            is_valid('fields=%s' % f)
        is_valid('fields=%s' % ','.join(config.API_SOLR_FIELDS))
        not_valid('fields=foobar')
        not_valid('fields=id, bibcode')
        
class PermissionsTest(unittest2.TestCase):
    
    def test_permissions(self):
        
        p = DP({})
        self.assertRaises(AssertionError, p._facets_ok, ["author"])
        p = DP({'facets': True})
        self.assertIsNone(p._facets_ok(["author"]))
        p = DP({'ex_fields': ['author']})
        self.assertRaisesRegexp(AssertionError, 'facets disabled', p._facets_ok, ["author"])
        p = DP({'facets': True, 'ex_fields': ['author']})
        self.assertRaisesRegexp(AssertionError, 'disallowed facet', p._facets_ok, ["author"])
        p = DP({'facets': True, 'facet_limit_max': 10})
        self.assertIsNone(p._facets_ok(["author:9"]))
        self.assertIsNone(p._facets_ok(["author:10"]))
        self.assertIsNone(p._facets_ok(["author:10:100"]))
        self.assertRaisesRegexp(AssertionError, 'facet limit value 11 exceeds max', p._facets_ok, ["author:11"])
        
        p = DP({})
        self.assertRaises(AssertionError, p._max_rows_ok, 10)
        p = DP({'max_rows': 10})
        self.assertIsNone(p._max_rows_ok(9))
        self.assertIsNone(p._max_rows_ok(10))
        self.assertRaises(AssertionError, p._max_rows_ok, 11)
        self.assertRaisesRegexp(AssertionError, 'rows=11 exceeds max allowed value: 10', p._max_rows_ok, 11)
        
        p = DP({})
        self.assertRaises(AssertionError, p._max_start_ok, 100)
        p = DP({'max_start': 200})
        self.assertIsNone(p._max_start_ok(100))
        self.assertIsNone(p._max_start_ok(200))
        self.assertRaises(AssertionError, p._max_start_ok, 300)
        self.assertRaisesRegexp(AssertionError, 'start=300 exceeds max allowed value: 200', p._max_start_ok, 300)
        
        p = DP({})
        self.assertIsNone(p._fields_ok('bibcode,title'))
        p = DP({'ex_fields': ['full']})
        self.assertIsNone(p._fields_ok('bibcode,title'))
        self.assertRaises(AssertionError, p._fields_ok, 'bibcode,title,full')
        self.assertRaisesRegexp(AssertionError, 'disallowed fields: full', p._fields_ok, 'bibcode,title,full')
        
        p = DP({})
        self.assertRaises(AssertionError, p._highlight_ok, ["abstract"])
        p = DP({'highlight': True})
        self.assertIsNone(p._highlight_ok(['abstract']))
        p = DP({'ex_highlight_fields': ['abstract']})
        self.assertRaisesRegexp(AssertionError, 'highlighting disabled', p._highlight_ok, ["abstract"])
        p = DP({'ex_highlight_fields': ['abstract'], 'highlight': True})
        self.assertRaisesRegexp(AssertionError, 'disallowed highlight field: abstract', p._highlight_ok, ["abstract"])
        p = DP({'highlight': True, 'highlight_max': 3})
        self.assertIsNone(p._highlight_ok(["abstract:2"]))
        self.assertIsNone(p._highlight_ok(["abstract:3"]))
        self.assertRaisesRegexp(AssertionError, 'highlight count 4 exceeds max allowed value: 3', p._highlight_ok, ["abstract:4"])
    
if __name__ == '__main__':
    unittest2.main()