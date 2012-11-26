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
        self.assertEqual(req.params['sort'], config.SOLR_DEFAULT_SORT)
        
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
        req.set_sort("DATE")
        self.assertEqual(req.params.sort, "DATE asc")
        req.set_sort("DATE", "desc")
        self.assertEqual(req.params.sort, "DATE desc")
        
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
        self.assertIn('f.keyword.limit', req.params)
        self.assertEqual(req.params['f.keyword.limit'], 10)
        req.add_facet('author', 10, 5)
        self.assertEqual(req.params['facet.field'], ['author', 'bibstem', 'keyword'])
        self.assertIn('f.author.limit', req.params)
        self.assertIn('f.author.mincount', req.params)
        self.assertEqual(req.params['f.author.limit'], 10)
        self.assertEqual(req.params['f.author.mincount'], 5)
        
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
        
    def test_response_content(self):
        
        fixture = self.useFixture(SolrRawQueryFixture())
        
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            
            req = solr.SolrRequest("foo")
            resp = req.get_response()
            self.assertIn('results', resp.search_response())
        
        
if __name__ == '__main__':
    unittest2.main()