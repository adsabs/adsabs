'''
Created on Sep 19, 2012

@author: jluker
'''
import re

from flask import g, current_app as app, request as current_request
from copy import deepcopy
from simplejson import loads, JSONDecodeError
from config import config
from .response import SolrResponse
from .adapter import SolrRequestAdapter
from .signals import error_signal, search_signal

import requests

__all__ = ['SolrRequest','SolrParams']

requests_session = requests.Session()
requests_session.mount('http://', SolrRequestAdapter())
requests_session.keep_alive = False

class SolrRequest(object):
    
    def __init__(self, q, **kwargs):
        self.q = q
        self.params = SolrParams(q=q, **kwargs)
        
    def set_params(self, **kwargs):
        self.params.update(**kwargs)
        return self
        
    def set_format(self, fmt):
        self.params.wt = fmt
        return self
        
    def set_rows(self, rows):
        self.params.rows = rows
        return self
        
    def set_start(self, start):
        self.params.start = start
        return self
        
    def set_fields(self, fields):
        fields.extend(config.SOLR_SEARCH_REQUIRED_FIELDS)
        self.params.fl = ','.join(fields)
        return self
        
    def get_fields(self):
        if self.params.has_key('fl'):
            return self.params.fl.split(',')
        return []
        
    def set_sort(self, sort_field, direction="desc"):
        self.params.sort = "%s %s" % (sort_field, direction)
        return self
        
    def add_sort(self, sort_field, direction="desc"):
        if not self.params.has_key('sort'):
            self.set_sort(sort_field, direction)
        else:
            self.params.sort += ',%s %s' % (sort_field, direction)
        return self
        
    def get_sort(self):
        sort = []
        if self.params.has_key('sort'):
            return [tuple(x.split()) for x in self.params.sort.split(',')]
    
    def set_hlq(self, hlq):
        self.params['hl.q'] = hlq
        return self
        
    def add_filter(self, filter_):
        if config.SOLR_FILTER_QUERY_PARSER:
            filter_ = "{!%s}%s" % (config.SOLR_FILTER_QUERY_PARSER, filter_)
        self.params.append('fq', filter_)
        return self
        
    def get_filters(self, exclude_defaults=False):
        filters = self.params.get('fq', [])
        if exclude_defaults:
            default_params = dict(config.SOLR_MISC_DEFAULT_PARAMS)
            filters = filter(lambda x: x not in default_params.get('fq', []), filters)
        return filters
        
    def add_facet(self, field, limit=None, mincount=None, output_key=None, prefix=None):
        self.params['facet'] = "true"
        self.params.setdefault('facet.field', [])
        if output_key:
            self.params.append('facet.field', "{!ex=dt key=%s}%s" % (output_key, field))
        else:
            self.params.append('facet.field', field)
        if limit:
            self.params['f.%s.facet.limit' % field] = limit
        if mincount:
            self.params['f.%s.facet.mincount' % field] = mincount
        if prefix:
            self.params['f.%s.facet.prefix' % field] = prefix
        return self
            
    def add_facet_query(self, query):
        self.params['facet'] = "true"
        self.params.setdefault('facet.query', [])
        self.params.append('facet.query', query)
        return self
    
    def get_facet_queries(self):
        facet_queries = []
        if self.facets_on():
            for fq in self.params.get('facet.query', []):
                facet_queries.append(fq)
        return facet_queries
        
    def facets_on(self):
        return self.params.facet and True or False
    
    def add_facet_prefix(self, field, prefix):
        self.params['f.%s.facet.prefix' % field] = prefix
    
    def get_facets(self):
        facets = []
        if self.facets_on():
            for fl in self.params.get('facet.field', []):
                if fl.startswith('{!ex=dt'):
                    m = re.search("key=(\w+)}(\w+)", fl)
                    output_key, fl = m.groups()
                else:
                    output_key = None
                limit = self.params.get('f.%s.facet.limit' % fl, None)
                mincount = self.params.get('f.%s.facet.mincount' % fl, None)
                prefix = self.params.get('f.%s.facet.prefix' % fl, None)
                facets.append((fl, limit, mincount, output_key, prefix))
        return facets
    
    def add_highlight(self, fields, count=None, fragsize=None):
        self.params['hl'] = "true"
        if isinstance(fields, basestring):
            fields = [fields]
        for field in fields:
            if not self.params.has_key('hl.fl'):
                self.params['hl.fl'] = field
            elif field not in self.params['hl.fl'].split(','):
                self.params['hl.fl'] += ',' + field
            if count:
                self.params['f.%s.hl.snippets' % field] = count
            if fragsize:
                self.params['f.%s.hl.fragsize' % field] = fragsize
        return self
            
    def highlights_on(self):
        return self.params.hl and True or False
    
    def get_highlights(self):
        highlights = []
        if self.highlights_on() and self.params.has_key('hl.fl'):
            for fl in self.params.get('hl.fl').split(','):
                count = self.params.get('f.%s.hl.snippets' % fl, None)
                fragsize = self.params.get('f.%s.hl.fragsize' % fl, None)
                highlights.append((fl, count, fragsize))
        return highlights
    
    def get_response(self):
        
        http_status,content = self._get_solr_response()
        try:
            data = loads(content)
        except JSONDecodeError, e:
            error_msg = "JSON response from solr failed to parse: %s" % content
            error_signal.send(self, error_msg=error_msg)
            app.logger.error(error_msg)
            raise
        resp = SolrResponse(data, self)
        
        log_data = { 
            'q': resp.get_query(),
            'hits': resp.get_hits(),
            'count': resp.get_count(),
            'start': resp.get_start_count(),
            'qtime': resp.get_qtime(),
            'results': resp.get_doc_values('bibcode', 0, config.SEARCH_DEFAULT_ROWS),
            'error_msg': resp.get_error_message(),
            'http_status': http_status,
            'solr_url': self.url
        }
        search_signal.send(self, **log_data)
        
        return resp
    
    def _get_solr_response(self):
        r = requests.Request('GET', config.SOLR_URL + '/select', params=self.params.get_dict()).prepare()
        self.url = r.url
        http_resp = None 
        
        try:
            http_resp = requests_session.send(r, timeout=config.SOLR_TIMEOUT)
        except requests.RequestException, e:
            error_msg = "Something blew up when querying solr: %s; request url: %s" % \
                             (e, r.url)
            error_signal.send(self, error_msg=error_msg)
            app.logger.error(error_msg)
            raise
        return (http_resp.status_code, http_resp.content)
        
class SolrParams(dict):
    
    def __init__(self, *args, **kwargs):
        # set default values
        default_params = dict(
                    config.SOLR_MISC_DEFAULT_PARAMS,
                    wt=config.SOLR_DEFAULT_FORMAT
                    )
        self.update(**deepcopy(default_params))
        self.update(*args, **kwargs)

    def __getattr__(self, key):
        if not self.has_key(key):
            return None
        return dict.__getitem__(self, key)

    def __setattr__(self, key, val):
        dict.__setitem__(self, key, val)

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)
    
    def get_dict(self):
        return dict.copy(self)
    
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v
            
    def append(self, key, val):
        self.setdefault(key, [])
        if val not in self[key]:
            self[key].append(val)
                                
