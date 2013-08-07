'''
Created on July 22, 2013

@author: ehenneken
'''
import os
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

#import fixtures
import unittest2

#from adsabs.app import create_app
#from adsabs.core import solr
from config import config
from test_utils import (AdsabsBaseTestCase)

import adsabs.modules.bibutils.biblio_functions as bf

import requests

class TestCitationHelper(AdsabsBaseTestCase):
    def setUp(self):
        super(TestCitationHelper, self).setUp()
        config.SOLR_MISC_DEFAULT_PARAMS = []

    def test_empty_input(self):
        with self.app.test_request_context('/bibutils'):
            self.app.preprocess_request()
            self.assertEqual(bf.get_suggestions(), [])

    def test_citation_list(self):
        import types
        with self.app.test_request_context('/bibutils'):
            self.app.preprocess_request()
            cits = bf.get_citations(bibcodes=['1996ApJ...469..437S'])
            self.assertEqual(type(cits),types.ListType)
            self.assertTrue(len(cits)>0)

    def test_reference_list(self):
        import types
        with self.app.test_request_context('/bibutils'):
            self.app.preprocess_request()
            refs = bf.get_references(bibcodes=['1996ApJ...469..437S'])
            self.assertEqual(type(refs),types.ListType)
            self.assertTrue(len(refs)>0)

    def test_meta_data(self):
        with self.app.test_request_context('/bibutils'):
            self.app.preprocess_request()
            data = {'2314ADS..4305...27Q':{'title':u"An Artist's View of the Next Generation ADS Digital Library System",
                'author':u'Quest,+'}}
            self.assertEqual(bf.get_meta_data(results=[('2314ADS..4305...27Q',1)]),data)

    def _get_citations(*args, **kwargs):
        return ['a','b','c','d']

    def _get_references(*args, **kwargs):
        return ['c','c','c','d','e']

    def _get_meta_data(*args, **kwargs):
        d = {}
        for x in ['a','b','c','d','e']:
            d[x] = {'title':x.upper(),'author':x.upper()}
        return d

    def test_suggestions(self):
        bf.get_references = self._get_references
        bf.get_citations  = self._get_citations
        bf.get_meta_data  = self._get_meta_data
        data = [{'author': 'C', 'bibcode': 'c', 'score': 4, 'title': 'C'}, {'author': 'D', 'bibcode': 'd', 'score': 2, 'title': 'D'}]
        self.assertEqual(bf.get_suggestions(bibcodes=['foo']),data)

if __name__ == '__main__':
    unittest2.main()
        