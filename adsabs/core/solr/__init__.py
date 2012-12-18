
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

def request(q, filters=[], sort=config.SEARCH_DEFAULT_SORT, sort_direction=config.SEARCH_DEFAULT_SORT_DIRECTION, \
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
    
    req.set_fields(config.SEARCH_DEFAULT_SOLR_FIELDS)
    
    for facet in config.SEARCH_DEFAULT_SOLR_FACETS:
        req.add_facet(*facet)
        
    for hl in config.SEARCH_DEFAULT_HIGHLIGHT_FIELDS:
        req.add_highlight(*hl)
    
    # allow for manual overrides
    req.set_params(**kwargs)
    return req

def query(*args, **kwargs):
    req = request(*args, **kwargs)
    return req.get_response()
        
def get_document(solr_id, **kwargs):
    req = SolrRequest(q="identifier:%s" % solr_id, fl="*")
    resp = req.get_response()
    if resp.get_count() == 1:
        return resp.get_doc_object(0)

