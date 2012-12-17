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
from adsabs.modules.api import AdsApiUser
from adsabs.modules.api import ApiSearchRequest
from adsabs.modules.api import user
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
        
    def test_dev_user(self):
        
        self.insert_user("a")
        
        user = AdsApiUser.from_dev_key("b_dev_key")
        self.assertIsNone(user)
        
        self.insert_user("b")
        user = AdsApiUser.from_dev_key("b_dev_key")
        self.assertIsNone(user)
        
        self.insert_user("c", developer=True)
        user = AdsApiUser.from_dev_key("c_dev_key")
        self.assertIsNotNone(user)
        self.assertTrue(user.is_developer())
        self.assertEqual("c_name", user.name)
        
        self.insert_user("d", developer=True, dev_perms={"foo": 1})
        user = AdsApiUser.from_dev_key("d_dev_key")
        self.assertIsNotNone(user)
        self.assertIn("foo", user.get_dev_perms())
        
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
        self.assertNotIn('facets', resp_data['results'])
        rv = self.client.get('/api/search/?q=black+holes&dev_key=bar_dev_key&facet=author')
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
            req = ApiSearchRequest(request.values) #@UndefinedVariable
            solr_req = req._create_solr_request()
            self.assertEquals(solr_req.params.q, 'black holes')
        
    def test_validation(self):
        
        self.insert_user("foo", developer=True)
        
        def validate(qstring, errors=None):
            with self.app.test_request_context('/api/search/?dev_key=foo_dev_key&%s' % qstring):
                form = ApiQueryForm(request.values, csrf_enabled=False) #@UndefinedVariable
                valid = form.validate()
                if errors:
                    for field, msg in errors.items():
                        self.assertIn(field, form.errors)
                        self.assertIn(msg, form.errors[field][0])
                return valid
            
        def is_valid(qstring):
            self.assertTrue(validate(qstring))
            
        def not_valid(qstring, errors=None):
            self.assertFalse(validate(qstring, errors))
        
        is_valid('q=black+holes')
        not_valid('q=a', {'q': 'input must be at least'})
        not_valid('q=%s' % ("foobar" * 1000), {'q': 'input must be at no more'})
        
        for f in config.API_SOLR_FIELDS:
            is_valid('fl=%s' % f)
        is_valid('fl=%s' % ','.join(config.API_SOLR_FIELDS))
        is_valid('fl=id,bibcode')
        not_valid('fl=foobar', {'fl': 'not a selectable field'})
        not_valid('fl=id, bibcode', {'fl': 'no whitespace'})
        not_valid('fl=id+bibcode', {'fl': 'comma-separated'})
        
        from adsabs.modules.api.renderers import VALID_FORMATS
        for fmt in VALID_FORMATS:
            is_valid('fmt=%s' % fmt)
        not_valid('fmt=foobar', {'fmt': 'Invalid format'})
        
        is_valid('hl=abstract')
        is_valid('hl=title:3')
        for f in config.API_SOLR_FIELDS:
            is_valid('hl=%s' % f)
        is_valid('hl=abstract&hl=full')
        not_valid('hl=title-3', {'hl': 'Invalid highlight input'})
        not_valid('hl=foobar', {'hl': 'not a selectable field'})
        not_valid('hl=title:3:4', {'hl': 'Too many options'})
        not_valid('hl=abstract&hl=full:3:4', {'hl': 'Too many options'})
        not_valid('hl=abstract-3&hl=full:3:4', {'hl': 'Invalid highlight input'})
        
        is_valid('sort=DATE asc')
        is_valid('sort=DATE desc')
        not_valid('sort=year', {'sort': 'you must specify'})
        not_valid('sort=foo asc', {'sort': 'Invalid sort type'})
        not_valid('sort=DATE foo', {'sort': 'Invalid sort direction'})
        for f in config.SOLR_SORT_OPTIONS.keys():
            is_valid('sort=%s asc' % f)
            
        is_valid('facet=author')
        is_valid('facet=author&facet=year')
        for f in config.API_SOLR_FACET_FIELDS.keys():
            is_valid('facet=%s' % f)
        is_valid('facet=author:5')
        is_valid('facet=author:5:10')
        not_valid('facet=author:5:10:20', {'facet': 'Too many options'})
        not_valid('facet=foo', {'facet': 'Invalid facet selection'})
        not_valid('facet=author-5', {'facet': 'Invalid facet input'})
        not_valid('facet=author:foo', {'facet': 'Values for limit and min must be integers'})
        not_valid('facet=year&facet=author-5', {'facet': 'Invalid facet input'})
        not_valid('facet=foo&facet=author-5', {'facet': 'Invalid facet selection'})
        
        is_valid('filter=author:"John, D"')
        is_valid('filter=property:REFEREED')
        is_valid('filter=author:"John, D"&filter=property:REFEREED')
        not_valid('filter=property', {'filter': 'Format should be'})
        not_valid('filter=property-bar', {'filter': 'Format should be'})
        not_valid('filter=foo:bar', {'filter': 'Invalid filter field selection'})
        not_valid('filter=author:%s' % ("foobar" * 1000), {'filter': 'input must be at no more than'})
        
class ApiUserTest(unittest2.TestCase):
    
    def setUp(self):
        config.TESTING = True
        config.MONGOALCHEMY_DATABASE = 'test'
        self.app = create_app(config)
        
        from adsabs.extensions import mongodb
        mongodb.session.db.connection.drop_database('test') #@UndefinedVariable
        
        self.insert_user = user_creator()
        
    def test_permissions(self):
        
        self.insert_user("foo", developer=True)
        
        def DP(perms):
            u = AdsApiUser.from_dev_key("foo_dev_key")
            u.perms = perms
            return u
        
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
    
    def test_dev_key_creation(self):
        
        new_dev_key = user._create_dev_key()
        self.assertEquals(len(new_dev_key), user.DEV_KEY_LENGTH)
        
        new_dev_key, dev_key_hash = user.generate_dev_key_hash()
        self.assertEquals(len(new_dev_key), user.DEV_KEY_LENGTH)
        hash_components = dev_key_hash.split(user.HASH_SECTION_DELIMITER)
        self.assertEquals(len(hash_components), 3)
        self.assertTrue(user.validate_dev_key(new_dev_key, dev_key_hash))
        
    def test_create_api_user(self):
        self.insert_user("foo", developer=False)
        ads_user = AdsUser.from_id("foo_cookie_id")
        self.assertTrue(ads_user.user_rec.developer_key in [None, ""])
        api_user = user.create_api_user(ads_user, "basic")
        self.assertTrue(api_user.is_developer())
        self.assertEqual(api_user.user_rec.developer_perms, user.PERMISSION_LEVELS["basic"])
        dev_key = api_user.get_dev_key()
        api_user2 = AdsApiUser.from_dev_key(dev_key)
        self.assertEqual(api_user.get_dev_key(), api_user2.get_dev_key())
        
    def test_set_perms(self):
        self.insert_user("foo", developer=True, level="basic")
        api_user = AdsApiUser.from_dev_key("foo_dev_key")
        self.assertTrue(api_user.is_developer())
        self.assertEqual(api_user.user_rec.developer_perms, user.PERMISSION_LEVELS["basic"])
        api_user.set_perms("devel")
        api_user = AdsApiUser.from_dev_key("foo_dev_key")
        self.assertEqual(api_user.user_rec.developer_perms, user.PERMISSION_LEVELS["devel"])
        api_user.set_perms(new_perms={'bar': 'baz'})
        api_user = AdsApiUser.from_dev_key("foo_dev_key")
        self.assertEqual(api_user.user_rec.developer_perms, {'bar': 'baz'})
        
        
    
if __name__ == '__main__':
    unittest2.main()