'''
Created on Sep 19, 2012

@author: jluker
'''

from simplejson import loads,dumps
from .solrdoc import SolrDocument, SolrFacets

class SolrResponse(object):
    
    def __init__(self, raw):
        self.raw = raw
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
        
    def search_response(self):
        resp = {
            'meta': { 'errors': None },
            'results': {
                'count': self.get_count(),
                'docs': self.get_docset(),
                'facets': self.get_facets(),
            }
        }
        return resp
    
    def record_response(self, idx=0):
        try:
            return self.get_docset()[idx]
        except IndexError:
            return None
        
    def get_docset(self):
        return self.raw['response'].get('docs', [])
    
    def get_docset_objects(self):
        return [SolrDocument(x) for x in self.get_docset()]

    def get_facets(self):
        return self.raw['response'].get('facet_counts', {})
    
    def get_query(self):
        return self.raw['responseHeader']['params']['q']
    
    def get_count(self):
        return int(self.raw['response']['numFound'])
    
    def get_qtime(self):
        return self.raw['responseHeader']['QTime']
        
    def as_json(self):
        return dumps(self.raw)
    
        