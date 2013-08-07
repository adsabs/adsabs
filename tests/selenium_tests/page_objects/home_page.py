'''
Created on Aug 2, 2013

@author: jluker
'''

from search_page import BaseSearchPage
from config import test_config

class HomePage(BaseSearchPage):
    
    def __init__(self, tc):
        BaseSearchPage.__init__(self, tc)
        self.tc.get(test_config.SELENIUM_BASE_URL)
        
