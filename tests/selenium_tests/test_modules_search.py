import os
import sys
sys.path = [os.path.dirname(os.path.abspath(__file__))] + sys.path

import unittest2 as unittest
import page_objects as po
from utils import BaseSeleniumTestCase

class SearchTest(BaseSeleniumTestCase):
    
    def test_basic_search(self):

        home = po.HomePage(self.tc)
        search_results = home.search("black holes")
        self.assertIn("Search Results: black holes", search_results.title())
        self.assertTrue(search_results.has_pagination())
        
if __name__ == '__main__':
    
    unittest.main()