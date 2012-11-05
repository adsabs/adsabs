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

class SearchTestCase(unittest.TestCase):

    def setUp(self):
        config.TESTING = True
        app = create_app(config)
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_search_page(self):
        rv = self.app.get('/search/')
        assert 'ADS 2.0 Basic Search' in rv.data
        
    def test_search_results(self):
        rv = self.app.get('/search/?q=black+holes')
        assert 'Total Hits:' in rv.data
        
if __name__ == '__main__':
    unittest.main()