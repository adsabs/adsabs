
from .request import *
from .response import *
from .solrdoc import *

import logging

__all__ = [
    'SolrRequest',
    'SolrResponse',
    'SolrDocument',
    'query',
    'request',
    'get_document',
    ]

log = logging.getLogger(__name__)

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
            log.error("Invalid sort option: %s" % sort)
                
    for filter_ in filters:
        req.add_filter(filter_)
    
    req.set_fields(config.SOLR_SEARCH_DEFAULT_FIELDS)
    
    for facet in config.SOLR_SEARCH_DEFAULT_FACETS:
        req.add_facet(*facet)
        
    for hl in config.SOLR_SEARCH_DEFAULT_HIGHLIGHTS:
        req.add_highlight(*hl)
    
    # allow for manual overrides
    req.set_params(**kwargs)
    return req

def query(*args, **kwargs):
    req = search_request(*args, **kwargs)
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
        

