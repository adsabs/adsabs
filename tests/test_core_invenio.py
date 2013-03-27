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
from adsabs.core.invenio import get_metadata
from adsabs.core.invenio.inveniodoc import InvenioDoc

class InvenioDocTestCase(AdsabsBaseTestCase):
    
    def test_basic_obj_functionality(self):
        input = {'foo':'bar'}
        self.assertEqual(InvenioDoc(input).foo, 'bar')
        

class InvenioFuncsTestCase(AdsabsBaseTestCase):
    def setUp(self):
        """
        Monkey patch to avoid a real connection to the database
        """
        super(InvenioFuncsTestCase, self).setUp()
        def cust_get_invenio_metadata(ads_id):
            metadata = get_metadata([9405997L])
            return InvenioDoc(metadata.get(9405997L))
        def cust_get_records(invenio_record_id_list):
            out = {'995': [([('a', '{"abs":[{"p":"/proj/ads/abstracts/gen/text/J48/J48-49620.abs","primary":1,"t":"1359646069"}],\
                "links":{"data":[{"u":"http://adsabs.harvard.edu/NOTES/2314ADS..4305...27Q.tiff"}]}}'), ('7', 'ADS metadata')], ' ', ' ', '', 18)], 
                   '856': [([('u', 'http://adsabs.harvard.edu/NOTES/2314ADS..4305...27Q.tiff'), ('y', ''), ('3', 'data'), ('7', 'ADS metadata')], '4', ' ', '', 11), 
                           ([('u', 'http://adsabs.harvard.edu/abs/2314ADS..4305...27Q'), ('y', ''), ('3', 'ADSlink'), ('7', 'ADS metadata')], '4', ' ', '', 12)], 
                   '773': [([('p', 'Atomic Data'), ('v', '4305'), ('i', '27'), ('y', '2314'), ('z', 'Astrophysics Data System, e-report 4305, #27'), ('7', 'ADS')], ' ', ' ', '', 10)], 
                   '694': [([('a', 'SN2314A, SN 2314B'), ('7', 'ADS')], ' ', ' ', '', 9)], '970': [([('a', '2314ADS..4305...27Q'), ('7', 'ADS metadata')], ' ', ' ', '', 14)], 
                   '980': [([('a', 'GENERAL'), ('7', 'ADS metadata')], ' ', ' ', '', 15), ([('p', 'NOT REFEREED'), ('7', 'ADS metadata')], ' ', ' ', '', 16), 
                           ([('p', 'MISC'), ('7', 'ADS metadata')], ' ', ' ', '', 17)], 
                   '245': [([('a', "An Artist's View of the Next Generation ADS Digital Library System"), ('7', 'ADS')], ' ', ' ', '', 5)], 
                   '001': [([], ' ', ' ', '9405997', 1)], 
                   '260': [([('c', '2314-01-00'), ('t', 'date-published'), ('7', 'ADS')], ' ', ' ', '', 6), ([('c', '2314-01-00'), ('t', 'main-date'), ('7', 'ADS metadata')], ' ', ' ', '', 7)], 
                   '520': [([('a', 'Congratulations on reaching NASA\'s <A href="http://ads.harvard.edu">Astrophysics Data System</A>. \
                                   This cartoon features artwork by team member Elizabeth Bohlen who pictures a future astronomer using the ADS on her handheld device to track \
                                   an object hurtling towards earth.In the present, the ADS is widely used by astronomers and physicists to assist in their literature research by \
                                   providing access to 8 million abstracts and 39 million citations (as of 01/2010), by providing scans of over 4 million pages of astronomical \
                                   literature, and by allowing customized search and retrieval based on a user\'s individual interest.'), ('7', 'ADS')], ' ', ' ', '', 8)], 
                   '005': [([], ' ', ' ', '20130210063810.0', 2)], '961': [([('c', '2013-01-31T10:27:49'), ('x', '2013-01-31T10:27:49'), ('7', 'ADS')], ' ', ' ', '', 13)], 
                   '100': [([('a', 'Fake Quest, Cosmo'), ('b', 'Quest, C'), ('e', 'regular'), ('7', 'ADS')], ' ', ' ', '', 4)], 
                   '035': [([('a', '2314ADS..4305...27Q'), ('2', 'ADS bibcode'), ('7', 'ADS metadata')], ' ', ' ', '', 3)]}
            return [out]
        inv.get_invenio_metadata = cust_get_invenio_metadata
        inv.get_records = cust_get_records
    
    def test_get_invenio_metadata(self):        
        data_out = {'author': ({'affiliations': [],
                    'emails': [],
                    'name': u'Fake Quest, Cosmo',
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