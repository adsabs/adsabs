'''
Created on July 22, 2013

@author: ehenneken
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

#from adsabs.app import create_app
#from adsabs.core import solr
from config import config
from test_utils import (AdsabsBaseTestCase)

import adsabs.modules.bibutils.biblio_functions as bf
import adsabs.modules.bibutils.utils as utils

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
            cits = utils.get_citations(bibcodes=['1996ApJ...469..437S'])
            self.assertEqual(type(cits),types.DictType)
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

if __name__ == '__main__':
    unittest.main()
        
