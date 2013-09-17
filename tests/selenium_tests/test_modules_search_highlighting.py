import nose
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest2 as unittest

from utils import BaseSeleniumTestCase
import page_objects as po

class SearchHighlightingTest(BaseSeleniumTestCase):
    
    def test_highlights_1(self):
        home = po.HomePage(self.tc)
        search_results = home.search('"GO9-0102X"')
        self.assertTrue(search_results.has_highlights('GO9-0102X'))
        
    def test_highlights_2(self):
        home = po.HomePage(self.tc)
        search_results = home.search('full:"GO9-0102X"')
        self.assertTrue(search_results.has_highlights('GO9-0102X'))
        
    def test_highlights_3(self):
        home = po.HomePage(self.tc)
        search_results = home.search('"GO9-0102x"')
        self.assertTrue(search_results.has_highlights('GO9-0102x'))
        
    def test_highlights_4(self):
        home = po.HomePage(self.tc)
        search_results = home.search('shapley bibcode:1913AN....196..385S')
        self.assertTrue(search_results.has_highlights('shapley'))
        
    def test_highlights_5(self):
        home = po.HomePage(self.tc)
        search_results = home.search('full:shapley bibcode:1913AN....196..385S')
        self.assertTrue(search_results.has_highlights('shapley'))
        
    def test_highlights_6(self):
        home = po.HomePage(self.tc)
        search_results = home.search('"post-agb"')
        self.assertTrue(search_results.has_highlights('post-agb'))
        
    def test_highlights_7(self):
        home = po.HomePage(self.tc)
        search_results = home.search('MCMC +monte*')
        self.assertTrue(search_results.has_highlights('MCMC'))
        
    def test_highlights_8(self):
        home = po.HomePage(self.tc)
        search_results = home.search('MCMC +monte*')
        self.assertTrue(search_results.has_highlights('monte'))
        
    def test_highlights_9(self):
        home = po.HomePage(self.tc)
        search_results = home.search('author:"de Souza"')
        self.assertFalse(search_results.has_highlights())
        
    def test_highlights_10(self):
        home = po.HomePage(self.tc)
        search_results = home.search('author:"*woo"')
        self.assertFalse(search_results.has_highlights())
        
    def test_highlights_11(self):
        home = po.HomePage(self.tc)
        search_results = home.search('black holes database:astronomy')
        self.assertFalse(search_results.has_highlights("database"))
    
if __name__ == '__main__':
    unittest.main()

