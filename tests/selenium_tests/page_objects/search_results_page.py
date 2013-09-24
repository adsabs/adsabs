'''
Created on Aug 2, 2013

@author: jluker
'''
import sys
import re
from random import choice
from search_page import BaseSearchPage
from config.test_config import test_config

def new_search(tc, query):
    srp = SearchResultsPage(tc)
    srp.tc.get(test_config.SELENIUM_BASE_URL + 'search?q=' + query)
    return srp

class SearchResultsPage(BaseSearchPage):
    
    def has_pagination(self):
        elements = self.browser.find_elements_by_xpath("//a[contains(@href, '&page=2')][contains(text(),'Next')]")
        return len(elements) > 0
 
    def has_highlights(self, match=None, matchCase=False):
        """
        check for existence of (matching?) highlight <em> in the page
        TODO: shame we can't use xpath 2 here for case-insensitive search...
        """
        highlights = self.browser.find_elements_by_xpath('//span[@class="highlight"]/em')
        if not len(highlights):
            return False
        elif match is None:
            return True
        
        if matchCase:
            flags = None
        else:
            flags = re.I

        pattern = re.compile(match, flags)
        highlights = filter(lambda x: pattern.search(x.text) and True, highlights)

        return len(highlights) and True or False
    
    def get_abstract(self, result_idx=0):
        search_result_divs = self.browser.find_elements_by_class_name("searchresult")
        if not search_result_divs:
            print >>sys.stderr, "No results to click on!"
        link = search_result_divs[result_idx] \
            .find_element_by_class_name("title") \
            .find_element_by_tag_name("a")
        self.tc.follow_link(link)
        return AbstractPage(self.tc)
        
        
