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
        self.app = create_app(config)
        
    def test_param_add_filters(self):
        sp = solr.SolrParams()
        sp.setdefault('fq', [])
        sp['fq'].append('foo')
        sp.append('fq', 'bar')
        return
        
    def test_parse_query_fields(self):
        self.assertEqual(['foo'], solr.SolrRequest.parse_query_fields("foo:bar"))
        self.assertEqual(['foo','foe'], solr.SolrRequest.parse_query_fields("foo:bar foe:baz"))
        
    def test_response_content(self):
        
        fixture = self.useFixture(SolrRawQueryFixture())
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            req = solr.SolrRequest("foo")
            resp = req.get_response()
            self.assertIn('results', resp.search_response())
        
        
if __name__ == '__main__':
    unittest2.main()