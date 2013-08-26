
from .response import *
from .adapter import SolrRequestAdapter
from .solrdoc import *
from query_builder import QueryBuilderSimple, QueryBuilderSearch

from flask import current_app as app, request as current_request, g
from flask.ext.solrquery import solr #@UnresolvedImport
from copy import deepcopy

__all__ = [
    'SolrResponse',
    'SolrDocument',
    'query',
    'search_request',
    'facet_request',
    'document_request',
    'get_document',
    'SolrRequestAdapter',
    'QueryBuilderSimple',
    'QueryBuilderSearch',
    ]


def search_request(q, filters=[], sort=config.SEARCH_DEFAULT_SORT, 
                   sort_direction=config.SEARCH_DEFAULT_SORT_DIRECTION, 
                   query_fields=config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   rows=config.SEARCH_DEFAULT_ROWS, start=None, ui_q=None, 
                   ui_filters=[], **kwargs):
    
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
    req.set_query_fields(query_fields)
    
    for facet in config.SOLR_SEARCH_DEFAULT_FACETS:
        req.add_facet(*facet)
        
    for hl in config.SOLR_SEARCH_DEFAULT_HIGHLIGHTS:
        req.add_highlight(*hl)
    
    if ui_q:
        req.set_params(ui_q=ui_q)
    if ui_filters:
        req.set_params(ui_fq=deepcopy(ui_filters))
    
    # allow for manual overrides
    if len(kwargs):
        req.set_params(**kwargs)
        
    return req

def query(q, **kwargs):
    req = search_request(q, **kwargs)
    return req.get_response()

def facet_request(q, filters=[], facet_fields=None, ui_q=None, ui_filters=[], 
                  query_fields=config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS, **kwargs):

    req = SolrRequest(q, rows=0)
    
    req.set_query_fields(query_fields)

    for filter_ in filters:
        req.add_filter(filter_)
    
    if not facet_fields:
        facet_fields = config.SOLR_SEARCH_DEFAULT_FACETS
        
    for facet in facet_fields:
        req.add_facet(*facet)
    
    if ui_q:
        req.set_params(ui_q=ui_q)
    if ui_filters:
        req.set_params(ui_fq=deepcopy(ui_filters))
        
    if len(kwargs):
        req.set_params(**kwargs)
        
    return req
    
def facet_query(q, **kwargs):
    req = facet_request(q, **kwargs)
    return req.get_response()
        
def get_document(identifier, **kwargs):
    q = "identifier:%s" % identifier
    resp = solr.query(q, rows=1, fields=config.SOLR_SEARCH_DEFAULT_FIELDS, **kwargs)
    if resp.get_hits() == 1:
        return resp.get_doc_object(0)
    else:
        return None
        
