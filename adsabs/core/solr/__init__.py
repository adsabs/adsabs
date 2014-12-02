
from .response import *
from .adapter import SolrRequestAdapter
from .solrdoc import *
from query_builder import QueryBuilderSimple, QueryBuilderSearch
import copy 

from flask import current_app as app, request as current_request, g
from flask.ext.solrquery import solr, signals as solrquery_signals 
from copy import deepcopy

from adsabs.core.logevent import log_event
from adsabs.extensions import statsd

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
    with statsd.timer("core.solr.document.query_response_time"):
        resp = solr.query(q, rows=1, fields=config.SOLR_SEARCH_DEFAULT_FIELDS, **kwargs)
    if resp.get_hits() == 1:
        return resp.get_doc_object(0)
    else:
        return None
    
def get_document_similar(q, **kwargs):        
    params = dict(config.SOLR_MLT_PARAMS)
    params['mlt.fl'] = ','.join(config.SOLR_MLT_FIELDS)
    params.update(**kwargs)
    # TODO: someday maybe flask-solrquery can be made to know about different endpoints
    query_url = config.SOLRQUERY_URL
    mlt_query_url = query_url.rsplit('/', 1)[0] + '/mlt'
    return solr.query(q, query_url=mlt_query_url, **params)


def _extract_authors(solrdoc):
    authors = []
    i = 0
    affs = 'aff' in solrdoc and solrdoc['aff'] or []
    emails = 'email' in solrdoc and solrdoc['email'] or []
    afflen = 0

    if 'author' in solrdoc:
        for a in solrdoc['author']:
            author = {'name': a}
            affinfo = False
            if len(affs) > i and affs[i] != '-':
                author['affiliation'] = affs[i]
                affinfo = True
            if len(emails) > i and emails[i] != '-':
                author['email'] = emails[i]
                affinfo = True
            i += 1
            authors.append(author)
            if affinfo:
                afflen += 1
        
        if affs:
            del solrdoc['aff']
        if emails:
            del solrdoc['email']

    solrdoc['afflen'] = afflen
    return authors

def _extract_controlled_keywords(solrdoc):
    kws = {}
    if 'keyword' in solrdoc and 'keyword_schema' in solrdoc and \
        len(solrdoc['keyword']) == len(solrdoc['keyword_schema']):
        for schema,kw in zip(solrdoc['keyword_schema'], solrdoc['keyword']):
            if schema == '-':
                schema = 'Free Keywords'
            if schema not in kws:
                kws[schema] = set()
            kws[schema].add(kw)
        for k,v in kws.items():
            kws[k] = sorted(v)
        del solrdoc['keyword_schema']
    return kws
    
def denormalize_solr_doc(solrdoc):
    """
    Nested values are normalized in the solr document, this function
    will group them again, eg. authors will get together with
    their affiliations and emails
    """
    new_doc = copy.deepcopy(solrdoc.data)
    new_doc['title'] = ': '.join('title' in new_doc and new_doc['title'] or [])
    new_doc['keyword'] = _extract_controlled_keywords(new_doc)
    new_doc['author'] = _extract_authors(new_doc)
    return SolrDocument(new_doc)
