'''
Created on Sep 23, 2013

@author: jluker
'''

from config.test_config import test_config
from page_object import BasePageObject

def new_abstract(tc, bibcode, tab=""):
    abstract = AbstractPage(tc)
    abstract.tc.get(test_config.SELENIUM_BASE_URL + ('abs/%s/%s' % (bibcode, tab)))
    return abstract
    
class AbstractPage(BasePageObject):
    
    def has_tab(self, tab_type):
        pass
            
    def has_citations(self):
        pass
        
    def has_references(self):
        pass
    
    def has_coreads(self):
        pass
    
    def has_similar(self):
        pass
    
    def has_toc(self):
        pass
