'''
Created on Sep 19, 2012

@author: jluker
'''

class SolrDocument(object):
    def __init__(self, data):
        self.data = data

class SolrDocumentSet(object):
    
    @classmethod
    def from_dict_list(cls, dict_list):
        doclist = [SolrDocument(x) for x in dict_list]
        return cls(doclist)
    
    def __init(self, doclist=[]):
        self.doclist = doclist
        

class SolrFacets(object):
    pass