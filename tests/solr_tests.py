'''
Created on Nov 5, 2012

@author: jluker
'''
import os
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

import fixtures
import unittest2

from adsabs.app import create_app
from adsabs.core import solr
from config import config
from test_utils import *

import solr as solrpy
SOLR_AVAILABLE = False
try:
    s = solrpy.SolrConnection(config.SOLR_URL, timeout=3)
    rv = s.query("*", rows=0)
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
        req.set_fields("bar,baz")
        self.assertEqual(req.params.fl, 'bar,baz')
        self.assertEqual(req.get_fields(), ['bar','baz'])
        req.set_fields(['foo','bar'])
        self.assertEqual(req.params.fl, 'foo,bar')
        self.assertEqual(req.get_fields(), ['foo','bar'])
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
        self.assertEqual(req.get_facets(), [('author', None, None)])
        self.assertEqual(req.params['facet'], 'true')
        self.assertEqual(req.params['facet.field'], ['author'])
        req.add_facet('bibstem')
        self.assertEqual(req.get_facets(), [('author', None, None), ('bibstem', None, None)])
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem'])
        req.add_facet('keyword', 10)
        self.assertEqual(req.get_facets(), [('author', None, None), ('bibstem', None, None), ('keyword', 10, None)])
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem', 'keyword'])
        self.assertIn('f.keyword.facet.limit', req.params)
        self.assertEqual(req.params['f.keyword.facet.limit'], 10)
        req.add_facet('author', 10, 5)
        self.assertEqual(req.get_facets(), [('author', 10, 5), ('bibstem', None, None), ('keyword', 10, None)])
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem', 'keyword'])
        self.assertIn('f.author.facet.limit', req.params)
        self.assertIn('f.author.facet.mincount', req.params)
        self.assertEqual(req.params['f.author.facet.limit'], 10)
        self.assertEqual(req.params['f.author.facet.mincount'], 5)
        req.add_facet(['foo','bar'])
        self.assertEqual(req.params['facet.field'], ['author','bibstem','keyword','foo','bar'])
        req.add_facet(['baz', 'fez'], 3)
        self.assertEqual(req.params['f.baz.facet.limit'], 3)
        self.assertEqual(req.params['f.fez.facet.limit'], 3)
        
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
        self.assertEqual(req.params.fq, ['bibstem:ApJ'])
        req.add_filter("author:Kurtz,M")
        self.assertEqual(req.params.fq, ['bibstem:ApJ', 'author:Kurtz,M'])
        self.assertIn('bibstem:ApJ', req.get_filters())
        self.assertIn('author:Kurtz,M', req.get_filters())
        self.assertEqual(req.get_filters(exclude_defaults=True), ['bibstem:ApJ','author:Kurtz,M'])
        
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
        
    def test_facet_arg_separator(self):
        """
        tests that our config.SOLR_ARG_SEPARATOR successfully works around
        solrpy's replacing of '_' with '.' in our field-specific params
        """ 
        self._solr_request_params = None
        
        class MockResp(object):
            """callback needs to return an object with a read() method"""
            def read(self):
                return '{}'
            
        def post_callback(*args):
            self._solr_request_params = args[2]
            return MockResp()
        fixture = self.useFixture(SolrRequestPostMP(post_callback))
        
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            req.add_facet("bar_baz", 1, 1);
            resp = req.get_response()
            
        self.assertIn("f.bar_baz.facet.mincount=1", self._solr_request_params)
        
    @unittest2.skipUnless(SOLR_AVAILABLE, 'solr unavailable')
    def test_cannot_send_request_errors(self):
        from adsabs.core.solr import query
        from random import choice
        import string
        chars = string.letters + string.digits
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            failures = []
            for i in range(100):
                try:
                    resp = query(''.join(choice(chars) for _ in range(10)), rows=0)
                    print resp.get_count()
                except Exception, e:
                    failures.append(e)
            self.assertEquals(len(failures), 0)
        
        
if __name__ == '__main__':
    unittest2.main()