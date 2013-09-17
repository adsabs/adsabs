'''
Created on Aug 2, 2013

@author: jluker
'''
import sys
import re
from search_page import BaseSearchPage

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
        
        