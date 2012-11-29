
from .request import *
from .response import *
from .solrdoc import *

import logging

__all__ = [
    'SolrRequest',
    'SolrResponse',
    'SolrDocument',
    'query',
    'get_document',
    ]

log = logging.getLogger(__name__)

def query(q, filters=[], sort=config.SEARCH_DEFAULT_SORT, sort_direction=config.SEARCH_DEFAULT_SORT_DIRECTION, \
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
    req.add_facet(config.SEARCH_DEFAULT_SOLR_FACETS, 
        limit=config.SEARCH_DEFAULT_FACET_LIMIT, 
        mincount=config.SEARCH_DEFAULT_FACET_MINCOUNT
        )
    req.add_highlight(config.SEARCH_DEFAULT_HIGHLIGHT_FIELDS, 
        count=config.SEARCH_DEFAULT_HIGHLIGHT_COUNT
        )
    
    # allow for manual overrides
    req.set_params(**kwargs)
    return req.get_response()
        
def get_document(solr_id, **kwargs):
    req = SolrRequest(q="identifier:%s" % solr_id, fl="*")
    resp = req.get_response()
    if resp.get_count() == 1:
        return resp.get_doc(0)

