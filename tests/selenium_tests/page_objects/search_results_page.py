'''
Created on Aug 2, 2013

@author: jluker
'''
from search_page import BaseSearchPage
from utils import case_ins_contains

class SearchResultsPage(BaseSearchPage):
    
    def __init__(self, tc):
        BaseSearchPage.__init__(self, tc)
        
    def has_pagination(self):
        browser = self.tc.browser
        elements = browser.find_elements_by_xpath("//a[contains(@href, '&page=2')][contains(text(),'Next')]")
        return len(elements) > 0
 
    def has_highlights(self, match=None):
        browser = self.tc.browser
        if not match:
            xpath = '//span[@class="highlight"]'
        else:
            xpath = '//span[@class="highlight"]/em[%s]' % case_ins_contains(match.lower())
        highlights = browser.find_elements_by_xpath('//span[@class="highlight"]')
        return len(highlights) > 0