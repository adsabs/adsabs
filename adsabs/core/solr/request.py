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
    
    @staticmethod
    def parse_query_fields(q):
        fields = []
        p = re.compile('(?P<field>[a-z]+):\S') 
        return [match.group('field') for match in p.finditer(q)]
        
    def __init__(self, q, **kwargs):
        self.q = q
        self.params = SolrParams(q=q, **kwargs)
        
    def set_rows(self, rows):
        self.rows = rows
        self.params.rows = rows
        
    def set_fields(self, fields):
        self.fields = fields
        self.params.fl = ','.join(fields)
        
    def set_sort(self, sort, direction="asc"):
        self.sort = sort
        self.sort_direction = direction
        self.params.sort = "%s %s" % (sort, direction)
        
    def add_filter(self, field, value):
        if not hasattr(self, 'filters'):
            self.filters = {} 
        self.filters.setdefault('field', [])
        self.filters['field'].append(value)
        self.params.append('fq', '%s:%s' % (field, value))
        
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
                    config.SOLR_DEFAULT_PARAMS,
                    sort=config.SOLR_DEFAULT_SORT,
                    rows=config.SOLR_DEFAULT_ROWS,
                    wt=config.SOLR_DEFAULT_FORMAT
                    )
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        return val

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '%s(%s)' % (type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v
            
    def append(self, key, val):
        self.setdefault(key, [])
        self[key].append(val)
                                