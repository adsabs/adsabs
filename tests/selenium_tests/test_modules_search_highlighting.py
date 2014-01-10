import nose
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys
if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest
    

from utils import BaseSeleniumTestCase
import page_objects as po

class SearchHighlightingTest(BaseSeleniumTestCase):
    
    def test_highlights(self):
        home = po.HomePage(self.tc)
        search_results = home.search('"GO9-0102X"')
        self.assertTrue(search_results.has_highlights('GO9-0102X'))
        
        home = po.HomePage(self.tc)
        search_results = home.search('full:"GO9-0102X"')
        self.assertTrue(search_results.has_highlights('GO9-0102X'))
        
        home = po.HomePage(self.tc)
        search_results = home.search('"GO9-0102x"')
        self.assertTrue(search_results.has_highlights('GO9-0102x'))
        
        home = po.HomePage(self.tc)
        search_results = home.search('shapley bibcode:1913AN....196..385S')
        self.assertTrue(search_results.has_highlights('shapley'))
        
        home = po.HomePage(self.tc)
        search_results = home.search('full:shapley bibcode:1913AN....196..385S')
        self.assertTrue(search_results.has_highlights('shapley'))
        
        home = po.HomePage(self.tc)
        search_results = home.search('"post-agb"')
        self.assertTrue(search_results.has_highlights('post-agb'))
        
        home = po.HomePage(self.tc)
        search_results = home.search('MCMC +monte*')
        self.assertTrue(search_results.has_highlights('MCMC'))
        
        home = po.HomePage(self.tc)
        search_results = home.search('MCMC +monte*')
        self.assertTrue(search_results.has_highlights('monte'))
        
    
if __name__ == '__main__':
    unittest.main()

