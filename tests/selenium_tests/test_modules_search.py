
import unittest2 as unittest
import page_objects as po
from utils import BaseSeleniumTestCase

class SearchTest(BaseSeleniumTestCase):
    
    def test_default_database_home(self):
        home = po.HomePage(self.tc)
        search_results = home.search("black holes")
        self.assertTrue(search_results.facet_applied('database', 'astronomy'))
        
    def test_default_database_search(self):
        search_home = po.SearchHomePage(self.tc)
        search_results = search_home.search("black holes")
        self.assertTrue(search_results.facet_applied('database', 'astronomy'))
        
    def test_database_physics_search(self):
        search_home = po.SearchHomePage(self.tc)
        search_home.set_database('physics')
        search_results = search_home.search("black holes")
        self.assertTrue(search_results.facet_applied('database', 'physics'))
        
    def test_database_all_search(self):
        search_home = po.SearchHomePage(self.tc)
        search_home.set_database('')
        search_results = search_home.search("black holes")
        self.assertFalse(search_results.has_facets_applied())
        
    def test_basic_search(self):

        home = po.HomePage(self.tc)
        search_results = home.search("black holes")
        self.assertIn("black holes", search_results.title())
        self.assertTrue(search_results.has_pagination())
        
if __name__ == '__main__':
    
    unittest.main()