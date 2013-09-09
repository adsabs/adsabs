
from .response import *
from .adapter import SolrRequestAdapter
from .solrdoc import *
from query_builder import QueryBuilderSimple, QueryBuilderSearch

from flask import current_app as app, request as current_request, g
from flask.ext.solrquery import solr, signals as solrquery_signals #@UnresolvedImport
from copy import deepcopy

from adsabs.core.logevent import log_event

__all__ = [
    'SolrResponse',
    'SolrDocument',
    'query',
    'get_document',
    'SolrRequestAdapter',
    'QueryBuilderSimple',
    'QueryBuilderSearch',
    'AdsabsSolrqueryException'
    ]

@solrquery_signals.search_signal.connect
def handle_search_signal(sender, **kwargs):
    """
    catches the search signal sent from the flask-solrquery extension,
    extracts some event data and sends it to the appropriate logger.
    TODO: figure out a way to push the logic of which event stream
    (e.g., 'api' or 'search') should handle the event out of here and into
    the actual blueprints. I tried and failed to come up with a solution.
    """

    resp = kwargs.pop('response')

    # common search event data
    log_data = {
        'q': resp.get_query(),
        'hits': resp.get_hits(),
        'count': resp.get_count(),
        'start': resp.get_start_count(),
        'qtime': resp.get_qtime(),
        'results': resp.get_doc_values('bibcode', 0, config.SEARCH_DEFAULT_ROWS),
        'error_msg': resp.get_error_message(),
        'http_status': resp.get_http_status(),
        'solr_url': resp.request.url,
    }

    if hasattr(g, 'api_user'):
        log_data['dev_key'] = g.api_user.get_dev_key()
        log_event('api', **log_data)
    elif hasattr(g, 'user_cookie_id'):
        log_data['user_cookie_id'] = g.user_cookie_id
        log_event('search', **log_data)

class AdsabsSolrqueryException(Exception):
    def __init__(self, message, exc_info):
        Exception.__init__(self, message)
        self.exc_info = exc_info
        
def get_document(identifier, **kwargs):
    q = "identifier:%s" % identifier
    resp = solr.query(q, rows=1, fields=config.SOLR_SEARCH_DEFAULT_FIELDS, **kwargs)
    if resp.get_hits() == 1:
        return resp.get_doc_object(0)
    else:
        return None
        
