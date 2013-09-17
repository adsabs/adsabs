'''
Created on Aug 2, 2013

@author: jluker
'''

from selenium.webdriver.common.by import By


class BasePageObject(object):
    
    def __init__(self, tc):
        self.tc = tc
        if not hasattr(tc, 'browser'):
            tc.open_browser()
        self.browser = self.tc.browser
            
    def title(self):
        self.tc.wait_for(By.TAG_NAME, 'title')
        return self.browser.title
