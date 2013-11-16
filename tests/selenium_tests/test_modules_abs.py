
import unittest2 as unittest
import page_objects as po
from utils import BaseSeleniumTestCase

class SearchTest(BaseSeleniumTestCase):
    
    def test_abstract_view(self):
        search_results = po.new_search(self.tc, 'bibcode:1998ApJ...500..525S')
        abstract = search_results.get_abstract()
        self.assertIn('Maps of Dust', abstract.title())
        
        abstract = po.new_abstract(self.tc, '1998ApJ...500..525S')
        self.assertIn('Maps of Dust', abstract.title())
    
if __name__ == '__main__':
    
    unittest.main()