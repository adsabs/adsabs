
from .request import *
from .response import *
from .solrdoc import *

#from flask import current_app as app

__all__ = [
    'SolrRequest',
    'SolrResponse',
    'SolrDocument',
    'query',
    'search_request',
    'facet_request',
    'document_request',
    'get_document',
    ]


def search_request(q, filters=[], sort=config.SEARCH_DEFAULT_SORT, sort_direction=config.SEARCH_DEFAULT_SORT_DIRECTION, \
          rows=config.SEARCH_DEFAULT_ROWS, start=None, **kwargs):
    
    req = SolrRequest(q, rows=rows)
    
    if start:
        req.set_start(start)
        
    if sort is not None:
        try:
            sort_field = config.SOLR_SORT_OPTIONS[sort]
            req.add_sort(sort_field, sort_direction)
        except KeyError:
            app.logger.error("Invalid sort option: %s" % sort)
                
    for filter_ in filters:
        req.add_filter(filter_)
    
    req.set_fields(config.SOLR_SEARCH_DEFAULT_FIELDS)
    
    for facet in config.SOLR_SEARCH_DEFAULT_FACETS:
        req.add_facet(*facet)
        
    for hl in config.SOLR_SEARCH_DEFAULT_HIGHLIGHTS:
        req.add_highlight(*hl)
    
    # allow for manual overrides
    if len(kwargs):
        req.set_params(**kwargs)
        
    return req

def query(q, **kwargs):
    req = search_request(q, **kwargs)
    return req.get_response()

def facet_request(q, filters=[], facet_fields=None, **kwargs):
    req = SolrRequest(q, rows=0)
    
    for filter_ in filters:
        req.add_filter(filter_)
    
    if not facet_fields:
        facet_fields = config.SOLR_SEARCH_DEFAULT_FACETS
        
    for facet in facet_fields:
        req.add_facet(*facet)
        
    if len(kwargs):
        req.set_params(**kwargs)
        
    return req
    
def facet_query(q, **kwargs):
    req = facet_request(q, **kwargs)
    return req.get_response()
        
def document_request(identifier, hlq=None, **kwargs):
    req = SolrRequest(q="identifier:%s" % identifier)
    
    req.set_fields(config.SOLR_SEARCH_DEFAULT_FIELDS)
    
    if hlq:
        for hl in config.SOLR_DOCUMENT_DEFAULT_HIGHLIGHTS:
            req.add_highlight(*hl)
        req.set_hlq(hlq)
        
    req.set_params(**kwargs)
    return req
    
def get_document(*args, **kwargs):
    req = document_request(*args, **kwargs)
    resp = req.get_response()
    if resp.get_hits() == 1:
        return resp.get_doc_object(0)
        

