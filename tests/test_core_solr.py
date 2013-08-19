'''
Created on Nov 5, 2012

@author: jluker
'''
import os
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

#import fixtures
import unittest2

#from adsabs.app import create_app
from adsabs.core import solr
from config import config
from test_utils import (AdsabsBaseTestCase, SolrRawQueryFixture)

import requests
SOLR_AVAILABLE = False
try:
    r = requests.get(config.SOLR_URL + '/select?q=id:0')
    assert r.status_code == 200
    SOLR_AVAILABLE = True
except:
    pass
        
class SolrTestCase(AdsabsBaseTestCase):

    def setUp(self):
        super(SolrTestCase, self).setUp()
        config.SOLR_MISC_DEFAULT_PARAMS = []
        
    def test_solr_request_defaults(self):
        req = solr.SolrRequest("foo")
        self.assertIn('q', req.params)
        self.assertEqual(req.params['q'], "foo")
        self.assertEqual(req.params['wt'], config.SOLR_DEFAULT_FORMAT)
        
    def test_solr_request_constructor_overrides(self):
        req = solr.SolrRequest("foo", wt='xml', bar="baz")
        self.assertEqual(req.params['wt'], 'xml')
        self.assertEqual(req.params['bar'], 'baz')
        
    def test_solr_request_setters(self):
        req = solr.SolrRequest("foo")   
        req.set_fields(['foo','bar'])
        expected = ['foo','bar']
        expected.extend(config.SOLR_SEARCH_REQUIRED_FIELDS)
        self.assertEqual(req.params.fl, ','.join(expected))
        self.assertEqual(req.get_fields(), expected)
        req.set_rows(100)
        self.assertEqual(req.params.rows, 100)
        req.set_start(10)
        self.assertEqual(req.params.start, 10)
        req.set_sort("bar")
        self.assertEqual(req.params.sort, "bar desc")
        self.assertEqual(req.get_sort(), [('bar','desc')])
        req.set_sort("baz", "asc")
        self.assertEqual(req.params.sort, "baz asc")
        self.assertEqual(req.get_sort(), [('baz','asc')])
        
    def test_solr_request_set_query_fields(self):
        req = solr.SolrRequest("foo")
        self.assertIsNone(req.params.qf)
        req.set_query_fields("bar baz^1.2")
        self.assertEqual(req.params.qf, "bar baz^1.2")
    
    def test_solr_request_add_sort(self):
        req = solr.SolrRequest("foo")
        self.assertEqual(req.params.sort, None)
        req.add_sort("bar")
        self.assertEqual(req.params.sort, "bar desc")
        req.add_sort("baz", "asc")
        self.assertEqual(req.params.sort, "bar desc,baz asc")
        
    def test_solr_request_add_facet(self):
        req = solr.SolrRequest("foo")   
        self.assertFalse(req.facets_on())
        self.assertNotIn('facet', req.params)
        req.add_facet('author')
        self.assertTrue(req.facets_on())
        self.assertEqual(req.get_facets(), [('author', None, None, None, None)])
        self.assertEqual(req.params['facet'], 'true')
        self.assertEqual(req.params['facet.field'], ['author'])
        req.add_facet('bibstem')
        self.assertEqual(req.get_facets(), [('author', None, None, None, None), ('bibstem', None, None, None, None)])
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem'])
        req.add_facet('keyword', 10)
        self.assertEqual(req.get_facets(), [('author', None, None, None, None), ('bibstem', None, None, None, None), ('keyword', 10, None, None, None)])
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem', 'keyword'])
        self.assertIn('f.keyword.facet.limit', req.params)
        self.assertEqual(req.params['f.keyword.facet.limit'], 10)
        req.add_facet('author', 10, 5)
        self.assertEqual(req.get_facets(), [('author', 10, 5, None, None), ('bibstem', None, None, None, None), ('keyword', 10, None, None, None)])
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem', 'keyword'])
        self.assertIn('f.author.facet.limit', req.params)
        self.assertIn('f.author.facet.mincount', req.params)
        self.assertEqual(req.params['f.author.facet.limit'], 10)
        self.assertEqual(req.params['f.author.facet.mincount'], 5)
        
    def test_solr_request_add_facet_query(self):
        req = solr.SolrRequest('foo')
        req.add_facet_query('year:[2000 TO 2003]')
        self.assertTrue(req.facets_on())
        self.assertEqual(req.get_facet_queries(), ['year:[2000 TO 2003]'])
        
    def test_solr_request_add_facet_output_key(self):
        
        req = solr.SolrRequest("foo")
        req.add_facet("author", output_key="authorz")
        self.assertEqual(req.params['facet.field'], ["{!ex=dt key=authorz}author"])
        
        req = solr.SolrRequest("foo")
        req.add_facet("title", limit=10, output_key="titlez")
        self.assertEqual(req.params['facet.field'], ["{!ex=dt key=titlez}title"])
        self.assertEqual(req.params['f.title.facet.limit'], 10)
        
    def test_solr_request_add_filter(self):
        req = solr.SolrRequest("foo")   
        req.add_filter("bibstem:ApJ")
        fqp = '{!%s}' % config.SOLR_FILTER_QUERY_PARSER
        self.assertEqual(req.params.fq, [fqp + 'bibstem:ApJ'])
        req.add_filter("author:Kurtz,M")
        self.assertEqual(req.params.fq, [fqp + 'bibstem:ApJ', fqp + 'author:Kurtz,M'])
        self.assertIn(fqp + 'bibstem:ApJ', req.get_filters())
        self.assertIn(fqp + 'author:Kurtz,M', req.get_filters())
        self.assertEqual(req.get_filters(exclude_defaults=True), [fqp + 'bibstem:ApJ', fqp + 'author:Kurtz,M'])
        
    def test_solr_request_add_highlight(self):
        req = solr.SolrRequest("foo")
        self.assertNotIn('hl', req.params)
        self.assertFalse(req.highlights_on())
        req.add_highlight("abstract")
        self.assertTrue(req.highlights_on())
        self.assertEqual(req.params['hl'], 'true')
        self.assertEqual(req.params['hl.fl'], 'abstract')
        self.assertEqual(req.get_highlights(), [('abstract', None, None)])
        req.add_highlight("full")
        self.assertEqual(req.params['hl.fl'], 'abstract,full')
        self.assertEqual(req.get_highlights(), [('abstract', None, None), ('full', None, None)])
        req.add_highlight('full', 2)
        self.assertEqual(req.get_highlights(), [('abstract', None, None), ('full', 2, None)])
        req.add_highlight(['foo','bar'])
        self.assertEqual(req.params['hl.fl'], 'abstract,full,foo,bar')
        req.add_highlight(['baz', 'fez'], 3)
        self.assertEqual(req.params['f.baz.hl.snippets'], 3)
        self.assertEqual(req.params['f.fez.hl.snippets'], 3)
        self.assertNotIn('f.baz.hl.fragsize', req.params)
        req.add_highlight("blah", 3, 5000)
        self.assertEqual(req.params['f.blah.hl.fragsize'], 5000)
    
    def test_solr_request_add_facet_prefix(self):
        req = solr.SolrRequest("foo")
        req.add_facet_prefix("author", "bar")
        self.assertIn("f.author.facet.prefix", req.params)
        self.assertEqual(req.params['f.author.facet.prefix'], "bar")
        
    def get_resp(self, req):
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            resp = req.get_response()
            return resp.search_response()
        
    def test_response_content(self):
        fixture = self.useFixture(SolrRawQueryFixture())
        
        self.assertIn('results', self.get_resp(solr.SolrRequest("foo")))
        self.assertNotIn('facets', self.get_resp(solr.SolrRequest("foo"))['results'])
        self.assertIn('facets', self.get_resp(solr.SolrRequest("foo").add_facet("bar"))['results'])
        
    def test_highlight_inclusion(self):
        fixture = self.useFixture(SolrRawQueryFixture())
        resp = self.get_resp(solr.SolrRequest("foo").add_highlight("abstract"))
        self.assertIn('lorem <em>ipsum</em> lorem', resp['results']['docs'][0]['highlights']['abstract'])
        
    def test_query(self):
        from adsabs.core.solr import query
        fixture = self.useFixture(SolrRawQueryFixture())
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            resp = query("foo")
            self.assertEquals(resp.request.params.q, "foo")
            resp = query("foo", rows=22)
            self.assertEquals(resp.request.params.rows, 22)
            resp = query("foo", start=11)
            self.assertEquals(resp.request.params.start, 11)
        
    def test_facet_request(self):
        from adsabs.core.solr import facet_request
        
        req = facet_request("foo")
        self.assertEquals(req.params.rows, 0)
        
        req = facet_request("foo", facet_fields=[("bar", None, None, None, "baz")])
        self.assertTrue(req.facets_on())
        self.assertEqual(req.get_facets(), [('bar', None, None, None, "baz")])
        self.assertEqual(req.params['facet'], 'true')
        self.assertEqual(req.params['facet.field'], ['bar'])
        self.assertIn("f.bar.facet.prefix", req.params)
        self.assertEqual(req.params["f.bar.facet.prefix"], "baz")
    
    def test_facet_content(self):
        fixture = self.useFixture(SolrRawQueryFixture())
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            req.params.facet = True
            resp = req.get_response()
            self.assertEqual(resp.get_all_facet_queries(), {'year:[2000 TO 2003]': 13})
            self.assertEqual(resp.get_all_facet_fields(), {'bibstem_facet': ['ApJ', 10, 'ArXiv', 8], 'year': ['2009', 3, '2008', 5]})
    
    def test_search_signal(self):
        from adsabs.core.solr import signals
        fixture = self.useFixture(SolrRawQueryFixture())
        
        @signals.search_signal.connect
        def catch_search(request, **kwargs):
            self._signal_test = request.q
            
        self.get_resp(solr.SolrRequest("foo"))
        self.assertEqual(self._signal_test, "foo") 
        
    def test_error_signal(self):
        from adsabs.core.solr import signals
        
        def reset_config(url, timeout):
            config.SOLR_URL = url
            config.SOLR_TIMEOUT = timeout
        self.addCleanup(reset_config, config.SOLR_URL, config.SOLR_TIMEOUT)
        config.SOLR_TIMEOUT = 1
        config.SOLR_URL = 'http://httpbin.org/delay/3?' # see http://httpbin.org
        
        @signals.error_signal.connect
        def catch_error(request, **kwargs):
            self._signal_error = kwargs['error_msg']
            
        try:
            self.get_resp(solr.SolrRequest("foo"))
        except:
            pass
        self.assertTrue(hasattr(self, '_signal_error'))
        self.assertTrue(self._signal_error.startswith("Something blew up"))
        
class SolrHAProxyTest(AdsabsBaseTestCase):
    
    def test_haproxy_cookie(self):
        """
        Uses the http://httpbin.org/ service to check that 
        the haproxy "sticky session" cookie is included in solr requests
        """
        from flask import g
        
        def reset_solr_url(url):
            config.SOLR_URL = url
        self.addCleanup(reset_solr_url, config.SOLR_URL)
        config.SOLR_URL = 'http://httpbin.org/cookies?' # bit of a hack adding the '?' at the end but otherwise the '/select' added later messes things up
        
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            resp = solr.SolrRequest("foo").get_response()
            expected = { config.SOLR_HAPROXY_SESSION_COOKIE_NAME: g.user_cookie_id }
            self.assertDictContainsSubset(expected, resp.raw['cookies'])

class SolrResponseCaseAdv(AdsabsBaseTestCase):

    def setUp(self):
        super(SolrResponseCaseAdv, self).setUp()
        config.SOLR_MISC_DEFAULT_PARAMS = []
        config.SEARCH_DEFAULT_ROWS = '5'
        
    def test_get_pag_funcs_with_response_1(self):
        """Tests the pagination function with many results"""
        solr_response = {'facet_counts': {'facet_fields': {'bibstem_facet': ['ApJ', 10, 'ArXiv', 8],
                           'year': ['2009', 3, '2008', 5]},
                          'facet_queries': {'year:[2000 TO 2003]': 13}},
                         'highlighting': {'1234': {'abstract': ['lorem <em>ipsum</em> lorem']}},
                         'response': {'docs': [{'abstract': 'lorem ipsum %s' % x, 'bibcode': 'xyz_%s' % x ,'id': '1234%s' % x } for x in xrange(int(config.SEARCH_DEFAULT_ROWS))],
                          'numFound': 46,
                          'start': 0},
                         'responseHeader': {'QTime': 100, 'params': {'q': 'abc'}, 'status': 0}}
        fixture = self.useFixture(SolrRawQueryFixture(data=solr_response))
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            req.params.facet = True
            resp = req.get_response()
            
            self.assertEqual(resp.get_count(), 5)
            self.assertEqual(resp.get_hits(), 46)
            self.assertEqual(resp.get_start_count(), 0)
            
            #pagination dictionary
            pag_dict = {
                   'max_pagination_len': 5 ,
                   'num_total_pages': 10,
                   'current_page': 1,
                   'pages_before': [],
                   'pages_after': [2, 3, 4, 5],       
            }
            self.assertEqual(resp.get_pagination(), pag_dict)
            
    def test_get_pag_funcs_with_response_2(self):
        """Tests the pagination function with few results"""
        solr_response = {'facet_counts': {'facet_fields': {'bibstem_facet': ['ApJ', 10, 'ArXiv', 8],
                           'year': ['2009', 3, '2008', 5]},
                          'facet_queries': {'year:[2000 TO 2003]': 13}},
                         'highlighting': {'1234': {'abstract': ['lorem <em>ipsum</em> lorem']}},
                         'response': {'docs': [{'abstract': 'lorem ipsum %s' % x, 'bibcode': 'xyz_%s' % x ,'id': '1234%s' % x } for x in xrange(int(config.SEARCH_DEFAULT_ROWS))],
                          'numFound': 8,
                          'start': 0},
                         'responseHeader': {'QTime': 100, 'params': {'q': 'abc'}, 'status': 0}}
        fixture = self.useFixture(SolrRawQueryFixture(data=solr_response))
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            req.params.facet = True
            resp = req.get_response()
            
            self.assertEqual(resp.get_count(), 5)
            self.assertEqual(resp.get_hits(), 8)
            self.assertEqual(resp.get_start_count(), 0)
            
            #pagination dictionary
            pag_dict = {
                   'max_pagination_len': 5,
                   'num_total_pages': 2,
                   'current_page': 1,
                   'pages_before': [],
                   'pages_after': [2],       
            }
            self.assertEqual(resp.get_pagination(), pag_dict)
            
    def test_get_pag_funcs_with_response_3(self):
        """Tests the pagination function with few results starting from second page"""
        solr_response = {'facet_counts': {'facet_fields': {'bibstem_facet': ['ApJ', 10, 'ArXiv', 8],
                           'year': ['2009', 3, '2008', 5]},
                          'facet_queries': {'year:[2000 TO 2003]': 13}},
                         'highlighting': {'1234': {'abstract': ['lorem <em>ipsum</em> lorem']}},
                         'response': {'docs': [{'abstract': 'lorem ipsum %s' % x, 'bibcode': 'xyz_%s' % x ,'id': '1234%s' % x } for x in xrange(8 - int(config.SEARCH_DEFAULT_ROWS))],
                          'numFound': 8,
                          'start': 6},
                         'responseHeader': {'QTime': 100, 'params': {'q': 'abc'}, 'status': 0}}
        fixture = self.useFixture(SolrRawQueryFixture(data=solr_response))
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            req.params.facet = True
            resp = req.get_response()
            
            self.assertEqual(resp.get_count(), 3)
            self.assertEqual(resp.get_hits(), 8)
            self.assertEqual(resp.get_start_count(), 6)
            
            #pagination dictionary
            pag_dict = {
                   'max_pagination_len': 5,
                   'num_total_pages': 2,
                   'current_page': 2,
                   'pages_before': [1],
                   'pages_after': [],       
            }
            self.assertEqual(resp.get_pagination(), pag_dict)
    
    def test_get_pag_funcs_with_response_4(self):
        """Tests the pagination function with many results starting from following page"""
        solr_response = {'facet_counts': {'facet_fields': {'bibstem_facet': ['ApJ', 10, 'ArXiv', 8],
                           'year': ['2009', 3, '2008', 5]},
                          'facet_queries': {'year:[2000 TO 2003]': 13}},
                         'highlighting': {'1234': {'abstract': ['lorem <em>ipsum</em> lorem']}},
                         'response': {'docs': [{'abstract': 'lorem ipsum %s' % x, 'bibcode': 'xyz_%s' % x ,'id': '1234%s' % x } for x in xrange(int(config.SEARCH_DEFAULT_ROWS))],
                          'numFound': 46,
                          'start': 16},
                         'responseHeader': {'QTime': 100, 'params': {'q': 'abc'}, 'status': 0}}
        fixture = self.useFixture(SolrRawQueryFixture(data=solr_response))
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            req.params.facet = True
            resp = req.get_response()
            
            self.assertEqual(resp.get_count(), 5)
            self.assertEqual(resp.get_hits(), 46)
            self.assertEqual(resp.get_start_count(), 16)
            
            #pagination dictionary
            pag_dict = {
                   'max_pagination_len': 5 ,
                   'num_total_pages': 10,
                   'current_page': 4,
                   'pages_before': [2, 3],
                   'pages_after': [5, 6],       
            }
            self.assertEqual(resp.get_pagination(), pag_dict)
    
    def test_get_pag_funcs_with_response_5(self):
        """Tests the get functions in case of an error coming from SOLR"""
        solr_response = {"responseHeader":{
                            "status":400,
                            "QTime":1,},
                          "error":{
                            "msg":"org.apache.lucene.queryparser.classic.ParseException: undefined field authsorfsd",
                            "code":400}}
        
        fixture = self.useFixture(SolrRawQueryFixture(data=solr_response))
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            req.params.facet = True
            resp = req.get_response()
            
            self.assertEqual(resp.get_count(), 0)
            self.assertEqual(resp.get_hits(), 0)
            self.assertEqual(resp.get_start_count(), 0)
            
            #pagination dictionary
            pag_dict = {
                   'max_pagination_len': 5 ,
                   'num_total_pages': 0,
                   'current_page': 1,
                   'pages_before': [],
                   'pages_after': [],       
            }
            self.assertEqual(resp.get_pagination(), pag_dict)
      
    def test_get_err_funcs_with_response_1(self):
        """Tests the get functions in case of an error coming from SOLR"""
        #error coming from query parser on SOLR
        solr_response = {"responseHeader":{
                            "status":400,
                            "QTime":1,},
                          "error":{"msg":"org.apache.lucene.queryparser.classic.ParseException: undefined field authsorfsd",
                            "code":400}}
        fixture = self.useFixture(SolrRawQueryFixture(data=solr_response))
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            req.params.facet = True
            resp = req.get_response()  
    
            self.assertTrue(resp.is_error())
            self.assertEqual(resp.get_error_components(), {"msg":"org.apache.lucene.queryparser.classic.ParseException: undefined field authsorfsd", "code":400})
            self.assertEqual(resp.get_error(), "org.apache.lucene.queryparser.classic.ParseException: undefined field authsorfsd")
            self.assertEqual(resp.get_error_message(), "undefined field authsorfsd")
        
        #case of possible error string not containg solr class exception    
        solr_response = {"responseHeader":{
                            "status":500,
                            "QTime":1,},
                          "error":{"msg":"random string here",
                            "code":500}}
        fixture = self.useFixture(SolrRawQueryFixture(data=solr_response))
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            req.params.facet = True
            resp = req.get_response()  
    
            self.assertTrue(resp.is_error())
            self.assertEqual(resp.get_error_components(), {"msg":"random string here", "code":500})
            self.assertEqual(resp.get_error(), "random string here")
            self.assertEqual(resp.get_error_message(), "random string here")

    def test_get_err_funcs_with_response_2(self):
        """Tests the get functions in case of a normal response coming from SOLR"""
        solr_response = {'facet_counts': {'facet_fields': {'bibstem_facet': ['ApJ', 10, 'ArXiv', 8],
                           'year': ['2009', 3, '2008', 5]},
                          'facet_queries': {'year:[2000 TO 2003]': 13}},
                         'highlighting': {'1234': {'abstract': ['lorem <em>ipsum</em> lorem']}},
                         'response': {'docs': [{'abstract': 'lorem ipsum', 'bibcode': 'xyz','id': '1234'}],
                          'numFound': 1,
                          'start': 1},
                         'responseHeader': {'QTime': 100, 'params': {'q': 'abc'}, 'status': 0}}
        fixture = self.useFixture(SolrRawQueryFixture(data=solr_response))
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            req.params.facet = True
            resp = req.get_response()
            
            self.assertFalse(resp.is_error())
            self.assertEqual(resp.get_error_components(), {})
            self.assertIsNone(resp.get_error())
            self.assertIsNone(resp.get_error_message())
            
            
if __name__ == '__main__':
    unittest2.main()