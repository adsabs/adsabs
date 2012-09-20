'''
Created on Sep 19, 2012

@author: jluker
'''

from simplejson import loads
from .solrdoc import SolrDocumentSet, SolrFacets

class SolrResponse(object):
    
    @classmethod
    def from_json(cls, json):
        data = loads(json)
        count = data['response']['numFound']
        qtime = data['responseHeader']['QTime']
        docset = SolrDocumentSet.from_dict_list(data['response']['docs'])
        facets = SolrFacets.from_dict(data['response']['facet_counts'])
        
        return cls(docset, count, qtime, facets)
        
    def __init__(self, docset=[], count=None, qtime=None, facets=None):
        self.docset = docset
        self.count = count
        self.qtime = qtime
        self.facets = facets