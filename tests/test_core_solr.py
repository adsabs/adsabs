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

from adsabs.core.solr import SolrDocument, denormalize_solr_doc
from config import config
from test_utils import AdsabsBaseTestCase, canned_solr_response_data

from flask.ext.solrquery import solr 

import requests
NETWORK_AVAILABLE = False
try:
    r = requests.get('http://httpbin.org/')
    assert r.status_code == 200
    NETWORK_AVAILABLE = True
except:
    pass
        
class TestSolrResponse(AdsabsBaseTestCase):

    def setUp(self):
        super(TestSolrResponse, self).setUp()
        config.SOLR_MISC_DEFAULT_PARAMS = []
        
#     def get_resp(self, req):
#         with self.app.test_request_context('/'):
#             self.app.preprocess_request()
#             resp = req.get_response()
#             return resp.search_response()
        
    def test_response_content(self):
        with canned_solr_response_data():
            with self.app.test_request_context():
                resp = solr.query("foo")
                self.assertEqual(resp.get_http_status(), 200)
                self.assertFalse(resp.is_error())

                resp_data = resp.search_response()
                self.assertIn('results', resp_data)
                self.assertNotIn('facets', resp_data['results'])
            
    def test_response_content_with_facets(self):
        with canned_solr_response_data():
            with self.app.test_request_context():
                resp = solr.query("foo", facets=[('year',)])
                resp_data = resp.search_response()
                self.assertIn('facets', resp_data['results'])
                self.assertEqual(resp.get_all_facet_queries(), {'year:[2000 TO 2003]': 13})
                self.assertEqual(resp.get_all_facet_fields(), {'bibstem_facet': ['ApJ', 10, 'ArXiv', 8], 'year': ['2009', 3, '2008', 5]})

    def test_highlight_inclusion(self):
        with canned_solr_response_data():
            with self.app.test_request_context():
                resp = solr.query("foo")
                doc = resp.get_doc(0)
                self.assertNotIn('highlights',doc)
                resp = solr.query("foo", highlights=[('abstract',)])
                doc = resp.get_doc(0)
                self.assertIn('highlights',doc)

class TestSolrDoc(unittest.TestCase):
    
    def test_attribute_access(self):
        data = {'foo': 1, 'bar': 3, 'baz': [1,2,3], 'none': None}
        doc = SolrDocument(data)
        self.assertEquals(doc.foo, 1)
        self.assertEquals(doc.bar, 3)
        self.assertEquals(doc.baz, [1,2,3])
        self.assertEquals(doc.none, None)
        self.assertEquals(doc.bleh, None)
        
    def test_has_similar(self):
        data = {'foo': 1, 'bar': [1,2]}
        doc = SolrDocument(data)
        self.assertTrue(doc.has_similar(mlt_fields=['foo']))
        self.assertTrue(doc.has_similar(mlt_fields=['bar']))
        self.assertTrue(doc.has_similar(mlt_fields=['foo','bar']))
        self.assertTrue(doc.has_similar(mlt_fields=['foo','baz']))
        self.assertFalse(doc.has_similar(mlt_fields=['baz']))
        
    def test_has_coreads(self):
        self.assertTrue(SolrDocument({'reader': ['foo']}).has_coreads())
        self.assertFalse(SolrDocument({'reader': []}).has_coreads())
        self.assertFalse(SolrDocument({}).has_coreads())
        
    def test_has_references(self):
        self.assertTrue(SolrDocument({'[citations]': {'num_citations':2, 'num_references':2}}).has_references())
        self.assertFalse(SolrDocument({'[citations]': {'num_citations':2, 'num_references':0}}).has_references())
        self.assertFalse(SolrDocument({}).has_references())

    def test_has_toc(self):
        self.assertTrue(SolrDocument({'property': ['TOC']}).has_toc())
        self.assertFalse(SolrDocument({'property': ['FOO']}).has_toc())
        self.assertFalse(SolrDocument({}).has_toc())

    def test_has_citations(self):
        self.assertTrue(SolrDocument({'[citations]': {'num_citations':2, 'num_references':0}}).has_citations())
        self.assertFalse(SolrDocument({'[citations]': {'num_citations':0, 'num_references':0}}).has_citations())
        self.assertFalse(SolrDocument({}).has_citations())
    
    def test_counts(self):
        doc = SolrDocument({'[citations]': {'num_citations':3, 'num_references':2}})
        self.assertEqual(doc.get_citation_count(), 3)
        self.assertEqual(doc.get_references_count(), 2)
        
    def test_highlights(self):
        data = {'highlights': {'foo': ['bar','baz']}}
        doc = SolrDocument(data)
        self.assertTrue(doc.has_highlights())
        self.assertTrue(doc.has_highlights('foo'))
        self.assertFalse(doc.has_highlights('blah'))
        self.assertEqual(doc.get_highlights('foo'), ['bar','baz'])
        self.assertEqual(doc.get_highlights('blah'), None)
        
    def test_denormalize(self):
        
        data = {
                "author":["Quest, Cosmo", 
                          "Schlegel, David J.",
                          "Finkbeiner, Douglas P.",
                          "Davis, Marc"],
                "keyword":["cosmology diffuse radiation",
                      "cosmology cosmic microwave background",
                      "ism dust extinction",
                      "interplanetary medium",
                      "astronomy infrared",
                      "Astrophysics"],
                "keyword_norm":["cosmology diffuse radiation",
                      "cosmology cosmic microwave background",
                      "ism dust extinction",
                      "interplanetary medium",
                      "astronomy infrared",
                      "astrophysics"],
                'keyword_schema': ['ADS',
                            'ADS',
                            'ADS',
                            'ADS',
                            '-',
                            'foo'],
                "aff":["aff1",
                       "aff2;aff2b",
                       "aff3",
                       "-" 
                       ],
                "email":["krticka@physics.muni.cz",
                         "krticka@physics.muni.cz mysicka@physics.muni.cz",
                         "-",
                         "-" ],
                "bibcode":"1907PASP...19..240K",
                "title": ["An Artist's View of the Next Generation ADS Digital Library System"],
            }
        solrdoc = SolrDocument(data)
        newdoc = denormalize_solr_doc(solrdoc)
        expected = {'author': [{'affiliation': 'aff1',
                     'email': 'krticka@physics.muni.cz',
                     'name': 'Quest, Cosmo'},
                    {'affiliation': 'aff2;aff2b',
                     'email': 'krticka@physics.muni.cz mysicka@physics.muni.cz',
                     'name': 'Schlegel, David J.'},
                    {'affiliation': 'aff3', 
                     'name': 'Finkbeiner, Douglas P.'},
                    {'name': 'Davis, Marc'}],
         'bibcode': '1907PASP...19..240K',
         'keyword': {'ADS': ['cosmology cosmic microwave background',
                             'cosmology diffuse radiation',
                             'interplanetary medium',
                             'ism dust extinction'],
                     'Free Keywords': ['astronomy infrared'],
                     'foo': ['Astrophysics']},
         "keyword_norm":["cosmology diffuse radiation",
                      "cosmology cosmic microwave background",
                      "ism dust extinction",
                      "interplanetary medium",
                      "astronomy infrared",
                      "astrophysics"],
         'title': "An Artist's View of the Next Generation ADS Digital Library System",
         'afflen': 3}
        self.maxDiff = None
        self.assertEqual(expected, newdoc.data)

class TestSolrHAProxyCookie(AdsabsBaseTestCase):
     
    @unittest.skipUnless(NETWORK_AVAILABLE, 'network unavailable')
    def test_haproxy_cookie(self):
        """
        Uses the http://httpbin.org/ service to check that 
        the haproxy "sticky session" cookie is included in solr requests
        """
        from flask import g
         
        with self.app.test_request_context():

            # the httpbin thing will only work with GET requests
            orig_method = solr.request_http_method
            solr.request_http_method = 'GET'
        
            self.app.preprocess_request()
            req = solr.create_request("foo")
            solr.set_defaults(req, query_url='http://httpbin.org/cookies')
            resp = solr.get_response(req)
            expected = { config.SOLR_HAPROXY_SESSION_COOKIE_NAME: g.user_cookie_id }
            self.assertDictContainsSubset(expected, resp.raw['cookies'])

            solr.request_http_method = orig_method

class TestSolrErrorResponse(AdsabsBaseTestCase):
 
    def test_error_response_pagination(self):
        """Tests the get functions in case of an error coming from SOLR"""
        error_response = {"responseHeader":{
                            "status":400,
                            "QTime":1,},
                          "error":{
                            "msg":"org.apache.lucene.queryparser.classic.ParseException: undefined field authsorfsd",
                            "code":400}}
         
        with canned_solr_response_data(error_response):
            with self.app.test_request_context():
                resp = solr.query("foo")
                 
                self.assertEqual(resp.get_count(), 0)
                self.assertEqual(resp.get_hits(), 0)
                self.assertEqual(resp.get_start_count(), 0)
                 
                #pagination dictionar.y
                pag_dict = {
                       'max_pagination_len': 5 ,
                       'num_total_pages': 0,
                       'current_page': 1,
                       'pages_before': [],
                       'pages_after': [],       
                }
                self.assertEqual(resp.get_pagination(), pag_dict)
       
    def test_error_response_parsing_01(self):
        """Tests the get functions in case of an error coming from SOLR"""
        #error coming from query parser on SOLR
        error_response = {"responseHeader":{
                            "status":400,
                            "QTime":1,},
                          "error":{"msg":"org.apache.lucene.queryparser.classic.ParseException: undefined field authsorfsd",
                            "code":400}}
        with canned_solr_response_data(error_response, 400):
            with self.app.test_request_context():
                resp = solr.query("foo")
         
                self.assertEqual(resp.get_http_status(), 400)
                self.assertTrue(resp.is_error())
                self.assertEqual(resp.get_error(), "org.apache.lucene.queryparser.classic.ParseException: undefined field authsorfsd")
                self.assertEqual(resp.get_error_message(), "undefined field authsorfsd")
         
    def test_error_response_parsing_02(self):
        #case of possible error string not containg solr class exception    
        error_response = {"responseHeader":{
                            "status":500,
                            "QTime":1,},
                          "error":{"msg":"random string here",
                            "code":500}}
        with canned_solr_response_data(error_response, 500):
            with self.app.test_request_context('/'):
                resp = solr.query("foo")
         
                self.assertEqual(resp.get_http_status(), 500)
                self.assertTrue(resp.is_error())
                self.assertEqual(resp.get_error(), "random string here")
                self.assertEqual(resp.get_error_message(), "random string here")
 
if __name__ == '__main__':
    unittest.main()
