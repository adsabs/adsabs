'''
Created on Aug 2, 2013

@author: jluker
'''
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select

from page_object import BasePageObject
from config.test_config import test_config

class BaseSearchPage(BasePageObject):
    """
    base class for page objects that provide a search input
    """
    def search(self, query):

        from search_results_page import SearchResultsPage

        query_input = self.browser.find_element_by_name("q")
        query_input.send_keys("black holes")
        query_input.send_keys(Keys.RETURN)

        return SearchResultsPage(self.tc)
    
    def advanced_options_shown(self):
        adv = self.browser.find_element_by_id('advanced_options')
        return adv.is_displayed()

    def toggle_advanced_options(self):
        self.browser.find_element_by_id('drawer_handler').click()
        
    def set_database(self, option_value):
        if not self.advanced_options_shown():
            self.toggle_advanced_options()
        select = Select(self.browser.find_element_by_name("db_f"))
        select.select_by_value(option_value)

    def has_facets_applied(self):
        try:
            self.browser.find_element_by_class_name('appliedFilter')
            return True
        except NoSuchElementException:
            return False
        
    def facet_applied(self, field, value):
        facet_text = "%s : %s" % (field, value)
        for applied in self.browser.find_elements_by_class_name('appliedFilter'):
            if applied.text.lower() == facet_text.lower():
                return True
        return False