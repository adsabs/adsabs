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
from test_utils import (AdsabsBaseTestCase, ReferenceDataFixture, CitationDataFixture, MetaDataFixture)

from adsabs.modules.bibutils import biblio_functions

import requests

class TestCitationHelper(AdsabsBaseTestCase):
    def setUp(self):
        super(TestCitationHelper, self).setUp()
        config.SOLR_MISC_DEFAULT_PARAMS = []

    def test_empty_input(self):
        with self.app.test_request_context('/bibutils'):
            self.app.preprocess_request()
            self.assertEqual(biblio_functions.get_suggestions(), [])

    def test_reference_list(self):
        import types
        with self.app.test_request_context('/bibutils'):
            self.app.preprocess_request()
            refs = biblio_functions.get_references(bibcodes=['1996ApJ...469..437S'])
            self.assertEqual(type(refs),types.ListType)
            self.assertTrue(len(refs)>0)

    def test_meta_data(self):
        with self.app.test_request_context('/bibutils'):
            self.app.preprocess_request()
            data = {'2314ADS..4305...27Q':{'title':u"An Artist's View of the Next Generation ADS Digital Library System",
                'author':u'Quest,+'}}
            self.assertEqual(biblio_functions.get_meta_data(results=[('2314ADS..4305...27Q',1)]),data)

    def test_citation_helper(self):
        with self.app.test_request_context('/bibutils'):
            expected = [{'author': 'x_author', 'bibcode': 'x', 'score': 2, 'title': 'x_title'}, 
                        {'author': 'z_author', 'bibcode': 'z', 'score': 2, 'title': 'z_title'}]
            self.useFixture(ReferenceDataFixture())
            self.useFixture(CitationDataFixture())
            self.useFixture(MetaDataFixture())
            self.assertEqual(biblio_functions.get_suggestions(bibcodes=['a','b','c']),expected)

if __name__ == '__main__':
    unittest.main()
        
