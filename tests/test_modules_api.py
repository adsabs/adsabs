'''
Created on Nov 5, 2012

@author: jluker
'''

import os
import sys
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest
    
import simplejson as json

from werkzeug import Headers #@UnresolvedImport

from flask import request, g
from flask.ext.pushrod.renderers import RendererNotFound #@UnresolvedImport
from flask.ext.solrquery import solr #@UnresolvedImport

from adsabs.modules.user import AdsUser
from adsabs.modules.api import AdsApiUser
from adsabs.modules.api import ApiSearchRequest
from adsabs.modules.api import api_user
from adsabs.modules.api import api_errors
from adsabs.modules.api.forms import ApiQueryForm
from adsabs.core.solr import SolrResponse
from config import config
from test_utils import AdsabsBaseTestCase, \
                        canned_solr_response_data, \
                        CannedSolrResponse, \
                        global_api_user

import requests
SOLR_AVAILABLE = False
try:
    r = requests.get(config.SOLRQUERY_URL, params={'q':'id:0'})
    assert r.status_code == 200
    SOLR_AVAILABLE = True
except:
    pass
        
class APITests(AdsabsBaseTestCase):

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
        self.assertIn("API authentication failed: unknown dev_key", rv.data)
        
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
        
        with canned_solr_response_data():
            rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key')
            self.assertEqual(rv.status_code, 200)
            rv = self.client.get('/api/record/1234?dev_key=foo_dev_key')
            self.assertEqual(rv.status_code, 200)
    
    def test_empty_dev_key(self):
        """ensure that a user record with a dev_key of "" doesn't allow access to empty dev_key input"""
        
        self.insert_user("foo", developer=True)
        with canned_solr_response_data():
            user = AdsApiUser.from_dev_key("foo_dev_key")
            user.set_dev_key("")
            rv = self.client.get('/api/search/?q=black+holes&dev_key=')
            self.assertEqual(rv.status_code, 401)
        
    def test_api_version_header(self):
        
        self.insert_user("foo", developer=True)
        
        with canned_solr_response_data():
            rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key')
            self.assertIn('X-API-Version', rv.headers)
            self.assertEqual(config.API_CURRENT_VERSION, rv.headers['X-API-Version'])
            resp_data = json.loads(rv.data)
            self.assertEqual(config.API_CURRENT_VERSION, resp_data['meta']['api-version'])
            
            rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key', headers=[('X-API-Version','0.2')])
            self.assertEqual('0.2', rv.headers['X-API-Version'])
            resp_data = json.loads(rv.data)
            self.assertEqual('0.2', resp_data['meta']['api-version'])
        
    def test_search_output(self):
        
        self.insert_user("foo", developer=True)
        with canned_solr_response_data():
            rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key')
            resp_data = json.loads(rv.data)
            self.assertIn('meta', resp_data)
            self.assertIn('results', resp_data)
            self.assertTrue(resp_data['meta']['count'] >= 1)
            self.assertIsInstance(resp_data['results']['docs'], list)
            
            self.insert_user("bar", developer=True, dev_perms={'facets': True, 'allowed_fields': ['author']})
            rv = self.client.get('/api/search/?q=black+holes&dev_key=bar_dev_key')
            resp_data = json.loads(rv.data)
            self.assertNotIn('facets', resp_data['results'])
            rv = self.client.get('/api/search/?q=black+holes&dev_key=bar_dev_key&facet=author')
            resp_data = json.loads(rv.data)
            self.assertIn('facets', resp_data['results'])
    
    def test_record_output_01(self):
        
        self.insert_user("foo", developer=True)
        
        canned_data = CannedSolrResponse.DEFAULT_DATA
        canned_data['response']['docs'][0]['title'] = 'Foo Bar Polarization'

        with canned_solr_response_data(canned_data):
            rv = self.client.get('/api/record/2012ApJ...751...88M?dev_key=foo_dev_key')
            resp_data = json.loads(rv.data)
            self.assertIn("Polarization", resp_data['title'])
        
    def test_record_output_02(self):

        self.insert_user("foo", developer=True)

        canned_data = CannedSolrResponse.DEFAULT_DATA
        canned_data['response']['numFound'] = 0

        with canned_solr_response_data(canned_data):
            rv = self.client.get('/api/record/2012ApJ...751...88M?dev_key=foo_dev_key')
            self.assertEqual(rv.status_code, 404)
            self.assertIn("No record found with identifier 2012ApJ...751...88M", rv.data)
        
    def test_content_types(self):
         
        self.insert_user("foo", developer=True)
         
        with canned_solr_response_data(): 
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
            rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key&fmt=xml')
            self.assertIn('text/xml', rv.content_type)
             
            try:
                rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key&fmt=blah')
            except Exception, e:
                self.assertIsInstance(e, RendererNotFound)
             
            rv = self.client.get('/api/settings/?dev_key=foo_dev_key&fmt=xml')
            self.assertIn('<settings>', rv.data)
             
            rv = self.client.get('/api/record/xyz?dev_key=foo_dev_key&fmt=xml')
            self.assertIn('<bibcode type="str">xyz</bibcode', rv.data)
             
            rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key', headers=Headers({'Accept': 'application/xml'}))
            self.assertIn('<hits type="int">1</hits>', rv.data)
    #         
    def test_request_creation_01(self):
         
        self.insert_user("foo", developer=True)
         
        with self.app.test_request_context('/api/search/?dev_key=foo_dev_key&q=black+holes'):
            self.app.preprocess_request()
            with global_api_user("foo_dev_key"):
                req = ApiSearchRequest(request.values) #@UndefinedVariable
                solr_req = req._create_search_request()
                self.assertEquals(solr_req.params.q, 'black holes')
    
    def test_request_creation_02(self):
        
        self.insert_user("foo", developer=True)
         
        with self.app.test_request_context('/api/search/?dev_key=foo_dev_key&q=black+holes&filter=pubdate:[2000-01-00 TO *]'):
            self.app.preprocess_request()
            with global_api_user("foo_dev_key"):
                req = ApiSearchRequest(request.values) #@UndefinedVariable
                solr_req = req._create_search_request()
                self.assertEquals(solr_req.params.fq, ['pubdate:[2000-01-00 TO *]'])
         
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
         
        for f in config.API_SOLR_DEFAULT_FIELDS:
            is_valid('fl=%s' % f)
        is_valid('fl=%s' % ','.join(config.API_SOLR_DEFAULT_FIELDS))
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
        for f in config.API_SOLR_HIGHLIGHT_FIELDS:
            is_valid('hl=%s' % f)
        is_valid('hl=abstract&hl=full')
        not_valid('hl=title-3', {'hl': 'Invalid highlight input'})
        not_valid('hl=foobar', {'hl': 'not a selectable field'})
        not_valid('hl=title:3:4', {'hl': 'Too many options'})
        not_valid('hl=abstract&hl=full:3:4', {'hl': 'Too many options'})
        not_valid('hl=abstract-3&hl=full:3:4', {'hl': 'Invalid highlight input'})
         
        is_valid('sort=DATE asc')
        is_valid('sort=DATE desc')
        not_valid('sort=year', {'sort': 'must be a comma-separated list'})
        not_valid('sort=foo asc', {'sort': 'Invalid sort type'})
        not_valid('sort=DATE foo', {'sort': 'Invalid sort direction'})
        for f in config.SEARCH_SORT_OPTIONS_MAP.keys():
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
        is_valid('filter=foo')
        not_valid('filter=%s' % ("foobar" * 1000), {'filter': 'input must be at no more than'})
        not_valid('filter=foo:bar', {'filter': 'Invalid filter field selection'})
        not_valid('filter=author:%s' % ("foobar" * 1000), {'filter': 'input must be at no more than'})
         
class ApiUserTest(AdsabsBaseTestCase):
     
    def test_permission_checks(self):
         
        self.insert_user("foo", developer=True)
         
        def DP(perms):
            u = AdsApiUser.from_dev_key("foo_dev_key")
            u.set_perms(perms=perms)
            return u
         
        u = DP({})
        self.assertRaises(AssertionError, u._facets_ok, ["author"])
         
        u = DP({'facets': True})
        self.assertIsNone(u._facets_ok(["author"]))
        self.assertRaisesRegexp(AssertionError, 'disallowed facet', u._facets_ok, ["foo"])
         
        u = DP({'facets': True, 'facet_limit_max': 10})
        self.assertIsNone(u._facets_ok(["author:9"]))
        self.assertIsNone(u._facets_ok(["author:10"]))
        self.assertIsNone(u._facets_ok(["author:10:100"]))
        self.assertRaisesRegexp(AssertionError, 'facet limit value 11 exceeds max', u._facets_ok, ["author:11"])
         
        u = DP({})
        self.assertRaises(AssertionError, u._max_rows_ok, 10)
         
        u = DP({'max_rows': 10})
        self.assertIsNone(u._max_rows_ok(9))
        self.assertIsNone(u._max_rows_ok(10))
        self.assertRaises(AssertionError, u._max_rows_ok, 11)
        self.assertRaisesRegexp(AssertionError, 'rows=11 exceeds max allowed value: 10', u._max_rows_ok, 11)
         
        u = DP({})
        self.assertRaises(AssertionError, u._max_start_ok, 100)
         
        u = DP({'max_start': 200})
        self.assertIsNone(u._max_start_ok(100))
        self.assertIsNone(u._max_start_ok(200))
        self.assertRaises(AssertionError, u._max_start_ok, 300)
        self.assertRaisesRegexp(AssertionError, 'start=300 exceeds max allowed value: 200', u._max_start_ok, 300)
         
        u = DP({})
        self.assertRaisesRegexp(AssertionError, 'disallowed field: full', u._fields_ok, 'full')
        self.assertIsNone(u._fields_ok('bibcode'))
        self.assertIsNone(u._fields_ok('bibcode,title'))
        self.assertRaisesRegexp(AssertionError, 'disallowed field: full', u._fields_ok, 'bibcode,title,full')
         
        allowed_fields = []
        for f in config.API_SOLR_DEFAULT_FIELDS:
            allowed_fields.append(f)
            u = DP({'allowed_fields': allowed_fields})
            self.assertIsNone(u._fields_ok(f))
         
        u = DP({})
        self.assertRaises(AssertionError, u._highlight_ok, ["abstract"])
         
        u = DP({'highlight': True})
        self.assertRaisesRegexp(AssertionError, 'disallowed highlight field: abstract', u._highlight_ok, ["abstract"])
         
        u = DP({'highlight': True, 'highlight_fields': ['abstract']})
        self.assertIsNone(u._highlight_ok(['abstract']))
         
        u = DP({'highlight_fields': ['foobar']})
        self.assertRaisesRegexp(AssertionError, 'highlighting disabled', u._highlight_ok, ["foobar"])
         
        u = DP({'highlight': True, 'highlight_fields': ['foobar']})
        self.assertIsNone(u._highlight_ok(['foobar']))
         
        u = DP({'highlight': True, 'highlight_fields': ['abstract'], 'highlight_limit_max': 3})
        self.assertIsNone(u._highlight_ok(["abstract:2"]))
        self.assertIsNone(u._highlight_ok(["abstract:3"]))
        self.assertRaisesRegexp(AssertionError, 'highlight count 4 exceeds max allowed value: 3', u._highlight_ok, ["abstract:4"])
     
    def test_default_perm_levels(self):
         
        self.insert_user("foo", developer=True, level="basic")
        u = AdsApiUser.from_dev_key("foo_dev_key")
         
        self.assertIsNone(u._max_rows_ok(99))
        self.assertIsNone(u._max_rows_ok(100))
        self.assertRaisesRegexp(AssertionError, 'rows=101 exceeds max allowed value: 100', u._max_rows_ok, 101)
         
        self.assertIsNone(u._max_start_ok(300))
        self.assertRaisesRegexp(AssertionError, 'start=10001 exceeds max allowed value: 10000', u._max_start_ok, 10001)
         
        self.assertRaisesRegexp(AssertionError, 'facets disabled', u._facets_ok, ["author"])
        self.assertRaisesRegexp(AssertionError, 'highlighting disabled', u._highlight_ok, ["title"])
        for f in config.API_SOLR_DEFAULT_FIELDS:
            self.assertIsNone(u._fields_ok(f))
        for f in config.API_SOLR_EXTRA_FIELDS:
            self.assertRaisesRegexp(AssertionError, 'disallowed field: %s' % f, u._fields_ok, f)
             
        self.insert_user("bar", developer=True, level="devel")
        u = AdsApiUser.from_dev_key("bar_dev_key")
             
        self.assertIsNone(u._max_rows_ok(200))
        self.assertRaisesRegexp(AssertionError, 'rows=201 exceeds max allowed value: 200', u._max_rows_ok, 201)
         
        self.assertIsNone(u._max_start_ok(50000))
        self.assertRaisesRegexp(AssertionError, 'start=50001 exceeds max allowed value: 50000', u._max_start_ok, 50001)
         
        self.assertIsNone(u._facets_ok(['author']))
        self.assertIsNone(u._highlight_ok(['abstract']))
         
        for f in config.API_SOLR_DEFAULT_FIELDS:
            self.assertIsNone(u._fields_ok(f))
             
        for f in config.API_SOLR_EXTRA_FIELDS:
            self.assertRaisesRegexp(AssertionError, 'disallowed field: %s' % f, u._fields_ok, f)
             
        for f in config.API_SOLR_HIGHLIGHT_FIELDS:
            self.assertIsNone(u._highlight_ok([f]))
            self.assertIsNone(u._highlight_ok(["%s:4" % f]))
            self.assertRaisesRegexp(AssertionError, 'highlight count 5 exceeds', u._highlight_ok, ["%s:5" % f])
             
        for f in config.API_SOLR_FACET_FIELDS.keys():
            self.assertIsNone(u._facets_ok([f]))
         
         
    def test_dev_key_creation(self):
         
        new_dev_key = api_user._create_dev_key()
        self.assertEquals(len(new_dev_key), api_user.DEV_KEY_LENGTH)
         
        new_dev_key, dev_key_hash = api_user.generate_dev_key_hash()
        self.assertEquals(len(new_dev_key), api_user.DEV_KEY_LENGTH)
        hash_components = dev_key_hash.split(api_user.HASH_SECTION_DELIMITER)
        self.assertEquals(len(hash_components), 3)
        self.assertTrue(api_user.validate_dev_key(new_dev_key, dev_key_hash))
         
    def test_set_perms(self):
        self.insert_user("foo", developer=True, level="basic")
        user = AdsApiUser.from_dev_key("foo_dev_key")
        self.assertTrue(user.is_developer())
        self.assertEqual(user.user_rec.developer_perms, api_user.PERMISSION_LEVELS["basic"])
        user.set_perms("devel")
        user = AdsApiUser.from_dev_key("foo_dev_key")
        self.assertEqual(user.user_rec.developer_perms, api_user.PERMISSION_LEVELS["devel"])
        user.set_perms(perms={'bar': 'baz'})
        user = AdsApiUser.from_dev_key("foo_dev_key")
        self.assertEqual(user.user_rec.developer_perms, {'bar': 'baz'})
         
    def test_allowed_ips_1(self):
        """
        ip_allowed() should always be true if no 'allowed_ips' set in dev perms
        """
        self.insert_user("foo", developer=True, level='basic')
        user = AdsApiUser.from_dev_key("foo_dev_key")
        with self.app.test_request_context('/'):
            self.assertTrue(user.ip_allowed('192.168.0.1'))
         
    def test_allowed_ips_2(self):
        dev_perms = api_user.PERMISSION_LEVELS['basic']
        dev_perms['allowed_ips'] = ['192.168.0.1']
        self.insert_user("foo", developer=True, dev_perms=dev_perms.copy())
        user = AdsApiUser.from_dev_key("foo_dev_key")
        with self.app.test_request_context('/'):
            self.assertTrue(user.ip_allowed('192.168.0.1'))
            self.assertFalse(user.ip_allowed('199.111.99.11'))
         
    def test_allowed_ips_3(self):
        """
        test some allowed networks
        """
        dev_perms = api_user.PERMISSION_LEVELS['basic']
        dev_perms['allowed_ips'] = ['192.168.0.0/0.0.0.255']
        self.insert_user("foo", developer=True, dev_perms=dev_perms.copy())
        user = AdsApiUser.from_dev_key("foo_dev_key")
        with self.app.test_request_context('/'):
            self.assertTrue(user.ip_allowed('192.168.0.1'))
            self.assertFalse(user.ip_allowed('192.168.1.1'))
            self.assertFalse(user.ip_allowed('199.111.99.11'))
 
    def test_allowed_ips_4(self):
        """
        once more with an real ip value use case
        """
        dev_perms = api_user.PERMISSION_LEVELS['collab']
        dev_perms['allowed_ips'] = ['131.142.184.0/24','131.142.185.0/24']
        self.insert_user("foo", developer=True, dev_perms=dev_perms.copy())
        user = AdsApiUser.from_dev_key("foo_dev_key")
        with self.app.test_request_context('/'):
            self.assertTrue(user.ip_allowed('131.142.184.21'))
            self.assertTrue(user.ip_allowed('131.142.185.101'))
            self.assertFalse(user.ip_allowed('131.142.186.190'))
 
class ApiLiveSolrTests(AdsabsBaseTestCase):
    """
    Tests that rely on a live solr instance rather than canned responses
    """
     
    @unittest.skipUnless(SOLR_AVAILABLE, 'solr unavailable')
    def test_returned_fields(self):
        self.insert_user("foo", developer=True, level="basic")
        api_user = AdsApiUser.from_dev_key("foo_dev_key")
         
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key')
        resp = json.loads(rv.data)
        allowed_fields = api_user.get_allowed_fields()
        for f in resp['results']['docs'][0].keys():
            self.assertIn(f, allowed_fields)
             
        rv = self.client.get('/api/search/?q=black+holes+AND+year:2012&sort=CITED+desc&dev_key=foo_dev_key&fl=abstract,title')
        resp = json.loads(rv.data)
        expected_fields = ['abstract','title'] + config.SOLR_SEARCH_REQUIRED_FIELDS
        self.assertEqual(set(resp['results']['docs'][0].keys()), set(expected_fields))
         
    @unittest.skipUnless(SOLR_AVAILABLE, 'solr unavailable')
    def test_record_requests(self):
        self.insert_user("foo", developer=True, level="basic")
        rv = self.client.get('/api/record/2000A&AS..143...85A?dev_key=foo_dev_key')
        resp = json.loads(rv.data)
        self.assertIn('id', resp)
        rv = self.client.get('/api/record/1005.1529?dev_key=foo_dev_key')
        resp = json.loads(rv.data)
        self.assertIn('id', resp)
        rv = self.client.get('/api/record/10.1126/science.1.19.520?dev_key=foo_dev_key')
        resp = json.loads(rv.data)
        self.assertIn('id', resp)
             
         
     
if __name__ == '__main__':
    unittest.main()
