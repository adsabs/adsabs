'''
Created on Aug 2, 2013

@author: jluker
'''
from selenium.webdriver.common.keys import Keys

from page_object import BasePageObject
from config import test_config

class BaseSearchPage(BasePageObject):
    """
    base class for page objects that provide a search input
    """
    def search(self, query):

        from search_results_page import SearchResultsPage

        query_input = self.tc.browser.find_element_by_name("q")
        query_input.send_keys("black holes")
        query_input.send_keys(Keys.RETURN)

        return SearchResultsPage(self.tc)
        
