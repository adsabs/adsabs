'''
Created on Nov 5, 2012

@author: jluker
'''

import os
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #@UndefinedVariable

import fixtures
import unittest2

from adsabs.app import create_app
from adsabs.core import solr
from config import config
from test.utils import SolrRawQueryFixture

class SolrTestCase(unittest2.TestCase, fixtures.TestWithFixtures):

    def setUp(self):
        config.TESTING = True
        config.SOLR_MISC_DEFAULT_PARAMS = []
        self.app = create_app(config)
        
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
        req.set_rows(100)
        self.assertEqual(req.params.rows, 100)
        req.set_start(10)
        self.assertEqual(req.params.start, 10)
        req.set_sort("bar")
        self.assertEqual(req.params.sort, "bar desc")
        req.set_sort("baz", "asc")
        self.assertEqual(req.params.sort, "baz asc")
    
    def test_solr_request_add_sort(self):
        req = solr.SolrRequest("foo")
        self.assertEqual(req.params.sort, None)
        req.add_sort("bar")
        self.assertEqual(req.params.sort, "bar desc")
        req.add_sort("baz", "asc")
        self.assertEqual(req.params.sort, "bar desc,baz asc")
        
    def test_solr_request_add_facet(self):
        req = solr.SolrRequest("foo")   
        self.assertNotIn('facet', req.params)
        req.add_facet('author')
        self.assertEqual(req.params['facet'], 'true')
        self.assertEqual(req.params['facet.field'], ['author'])
        req.add_facet('bibstem')
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem'])
        req.add_facet('keyword', 10)
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem', 'keyword'])
        self.assertIn('f.keyword.facet.limit', req.params)
        self.assertEqual(req.params['f.keyword.facet.limit'], 10)
        req.add_facet('author', 10, 5)
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
        
    def test_solr_request_add_filter(self):
        req = solr.SolrRequest("foo")   
        req.add_filter("bibstem:ApJ")
        self.assertEqual(req.params.fq, ['bibstem:ApJ'])
        req.add_filter("author:Kurtz,M")
        self.assertEqual(req.params.fq, ['bibstem:ApJ', 'author:Kurtz,M'])
        
    def test_solr_request_add_highlight(self):
        req = solr.SolrRequest("foo")
        self.assertNotIn('hl', req.params)
        req.add_highlight("abstract")
        self.assertEqual(req.params['hl'], 'true')
        self.assertEqual(req.params['hl.fl'], 'abstract')
        req.add_highlight("full")
        self.assertEqual(req.params['hl.fl'], 'abstract,full')
        req.add_highlight(['foo','bar'])
        self.assertEqual(req.params['hl.fl'], 'abstract,full,foo,bar')
        req.add_highlight(['baz', 'fez'], 3)
        self.assertEqual(req.params['f.baz.hl.snippets'], 3)
        self.assertEqual(req.params['f.fez.hl.snippets'], 3)
        
    def test_response_content(self):
        fixture = self.useFixture(SolrRawQueryFixture())
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            resp = req.get_response()
            self.assertIn('results', resp.search_response())
        
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
        
        
if __name__ == '__main__':
    unittest2.main()