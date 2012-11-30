'''
Created on Sep 19, 2012

@author: jluker
'''

import logging
from simplejson import loads,dumps
from copy import deepcopy

from .solrdoc import SolrDocument

log = logging.getLogger(__name__)

class SolrResponse(object):
    
    def __init__(self, raw, request=None):
        self.raw = deepcopy(raw)
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
        docset = self.raw['response'].get('docs', [])
        if self.raw.has_key('highlighting'):
            for doc in docset:
                doc['highlights'] = self.raw['highlighting'][doc['id']]
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
    
    def get_query(self):
        return self.raw['responseHeader']['params']['q']
    
    def get_count(self):
        return int(self.raw['response']['numFound'])
    
    def get_qtime(self):
        return self.raw['responseHeader']['QTime']
        
        