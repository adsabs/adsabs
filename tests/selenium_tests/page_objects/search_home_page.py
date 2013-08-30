'''
Created on Aug 2, 2013

@author: jluker
'''

from search_page import BaseSearchPage
from config.test_config import test_config

class SearchHomePage(BaseSearchPage):
    
    def __init__(self, tc):
        BaseSearchPage.__init__(self, tc)
        self.tc.get(test_config.SELENIUM_BASE_URL)
        self.browser.find_element_by_link_text('Search').click()
        self.search_form = self.browser.find_element_by_xpath('//div[@id="search_form"]/form')
        
