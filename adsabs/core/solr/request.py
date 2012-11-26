'''
Created on Sep 19, 2012

@author: jluker
'''
import re
import logging

from flask import g
from simplejson import loads
from config import config
from .response import SolrResponse

log = logging.getLogger(__name__)
        
class SolrRequest(object):
    
    def __init__(self, q, **kwargs):
        self.q = q
        self.params = SolrParams(q=q, **kwargs)
        
    def set_rows(self, rows):
        self.params.rows = rows
        
    def set_start(self, start):
        self.params.start = start
        
    def set_fields(self, fields):
        self.params.fl = fields
        
    def set_sort(self, sort):
        self.params.sort = sort
        
    def set_hlq(self, hlq):
        self.params['hl.q'] = hlq
        
    def add_filter(self, filter):
        self.params.append('fq', filter)
        
    def add_facet(self, field, limit=None, mincount=None):
        self.params['facet'] = "true"
        self.params.append('facet.field', field)
        if limit:
            self.params['f.%s.limit' % field] = limit
        if mincount:
            self.params['f.%s.mincount' % field] = mincount
            
    def add_highlight(self, field, count=None):
        self.params['hl'] = "true"
        if not self.params.has_key('hl.fl'):
            self.params['hl.fl'] = field
        else:
            self.params['hl.fl'] += ',' + field
        if count:
            self.params['hl.%s.snippets' % field] = count
            
    def get_response(self):
        try:
            json = g.solr.raw_query(**self.params)
        except:
            log.error("Something blew up when querying solr")
            raise
        
        data = loads(json)
        return SolrResponse(data)
    
        
class SolrParams(dict):
    
    def __init__(self, *args, **kwargs):
        # set default values
        self.update(
                    config.SOLR_MISC_DEFAULT_PARAMS,
                    sort=config.SOLR_DEFAULT_SORT,
                    rows=config.SOLR_DEFAULT_ROWS,
                    wt=config.SOLR_DEFAULT_FORMAT
                    )
        self.update(*args, **kwargs)

    def __getattr__(self, key):
        val = dict.__getitem__(self, key)
        return val

    def __setattr__(self, key, val):
        dict.__setitem__(self, key, val)

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v
            
    def append(self, key, val):
        self.setdefault(key, [])
        if val not in self[key]:
            self[key].append(val)
                                