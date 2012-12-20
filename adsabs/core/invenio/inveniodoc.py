'''
Created on Dec 19, 2012

@author: dimilia
'''

class InvenioDoc(object):
        
    def __init__(self, data):
        self.data = data
        
    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]