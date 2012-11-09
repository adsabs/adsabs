'''
Created on Nov 5, 2012

@author: jluker
'''

import os
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from adsabs.app import create_app
from config import config

from adsabs.core import solr

class SolrParamsTestCase(unittest.TestCase):

    def test_filters(self):
        sp = solr.SolrParams()
        sp.setdefault('fq', [])
        sp['fq'].append('foo')
        sp.append('fq', 'bar')
        return
        
if __name__ == '__main__':
    unittest.main()