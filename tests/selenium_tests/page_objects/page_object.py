'''
Created on Aug 2, 2013

@author: jluker
'''

class BasePageObject(object):
    
    def __init__(self, tc):
        self.tc = tc
            
    def title(self):
        return self.tc.browser.title
