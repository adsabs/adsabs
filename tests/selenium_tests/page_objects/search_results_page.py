'''
Created on Aug 2, 2013

@author: jluker
'''
import sys
from search_page import BaseSearchPage
from utils import case_ins_contains

class SearchResultsPage(BaseSearchPage):
    
    def has_pagination(self):
        elements = self.browser.find_elements_by_xpath("//a[contains(@href, '&page=2')][contains(text(),'Next')]")
        return len(elements) > 0
 
    def has_highlights(self, match=None):
        if not match:
            xpath = '//span[@class="highlight"]'
        else:
            xpath = '//span[@class="highlight"]/em[%s]' % case_ins_contains(match.lower())
        highlights = self.browser.find_elements_by_xpath(xpath)
        return len(highlights) > 0