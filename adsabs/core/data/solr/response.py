'''
Created on Sep 19, 2012

@author: jluker
'''

from simplejson import loads
from .solrdoc import SolrDocument, SolrFacets

class SolrResponse(object):
    
    @staticmethod
    def from_json(json, request=None):
        data = loads(json)
        docset = [SolrDocument(x) for x in data['response']['docs']]
        if 'facet_counts' in data['response']:
            facets = SolrFacets.from_dict(data['response']['facet_counts'])
        else:
            facets = None
        
        return SolrResponse(docset, data, facets, request)
        
    def __init__(self, docset=[], data={}, facets=None, request=None):
        self.docset = docset
        self.data = data
        self.facets = facets
        self.iter_idx = -1
        
    def __iter__(self):
        self.iter_idx = -1
        return self
            
    def next(self):
        if self.iter_idx < len(self.docset) - 1:
            self.iter_idx += 1         
            return self.docset[self.iter_idx]
        else:
            raise StopIteration
        
    def get_docset(self):
        return self.docset

    def get_query(self):
        return self.data['responseHeader']['params']['q']
    
    def get_count(self):
        return int(self.data['response']['numFound'])
    
    def get_qtime(self):
        return self.data['responseHeader']['QTime']
        
        