'''
Created on Sep 19, 2012

@author: jluker
'''

import logging
from simplejson import loads,dumps

from .solrdoc import SolrDocument, SolrFacets

log = logging.getLogger(__name__)

class SolrResponse(object):
    
    def __init__(self, raw, request=None):
        self.raw = raw
        self.request = request
        
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
        
    def raw_response(self):
        return self.raw
    
    def get_docset(self):
        return self.raw['response'].get('docs', [])
    
    def get_docset_objects(self):
        return [SolrDocument(x) for x in self.get_docset()]

    def get_doc_object(self, idx):
        doc = self.get_doc(idx)
        if doc:
            return SolrDocument(doc)
    
    def get_doc(self, idx):
        try:
            return self.get_docset()[idx]
        except IndexError:
            log.debug("response has no doc at idx %d" % idx)
    
    def get_facets(self):
        return self.raw.get('facet_counts', {})
    
    def get_facets_fields(self, facet_name):
        facets = self.get_facets().get('facet_fields', {}).get(facet_name, [])
        return [tuple(facets[i:i+2]) for i in xrange(0, len(facets), 2)]
    
    def get_query(self):
        return self.raw['responseHeader']['params']['q']
    
    def get_count(self):
        return int(self.raw['response']['numFound'])
    
    def get_start_count(self):
        return int(self.raw['response']['start'])
    
    def get_qtime(self):
        return self.raw['responseHeader']['QTime']
        
        