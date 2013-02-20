'''
Created on Feb 20, 2013

@author: dimilia
'''
import os
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

import unittest2

from config import config
from test_utils import *

import adsabs.core.invenio as inv
from adsabs.core.invenio.inveniodoc import InvenioDoc

class InvenioDocTestCase(AdsabsBaseTestCase):
    
    def test_basic_obj_functionality(self):
        input = {'foo':'bar'}
        self.assertEqual(InvenioDoc(input).foo, 'bar')
        

class InvenioFuncsTestCase(AdsabsBaseTestCase):
    
    def test_get_invenio_metadata(self):
        data_out = {'author': ({'affiliations': [],
                    'emails': [],
                    'name': u'Quest, Cosmo',
                    'native_name': None,
                    'normalized_name': u'Quest, C',
                    'type': 'regular'},),
                    'bibcode': '2314ADS..4305...27Q',
                    'keyword': {'controlled': {}, 'free': []},
                    'title': u"An Artist's View of the Next Generation ADS Digital Library System"}
        self.assertEqual(inv.get_invenio_metadata('2314ADS..4305...27Q').data, data_out)
    
    #not sure if it's worth to test all the other functions since everything is dependent from the invenio DB content... 

if __name__ == '__main__':
    unittest2.main()