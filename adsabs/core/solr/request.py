'''
Created on Sep 19, 2012

@author: jluker
'''
import re
import logging

from flask import g
from urllib import urlencode
from simplejson import loads
from config import config
from .response import SolrResponse

log = logging.getLogger(__name__)
        
class SolrRequest(object):
    
    def __init__(self, q, **kwargs):
        self.q = q
        self.params = SolrParams(q=q, **kwargs)
        
    def set_format(self, fmt):
        self.params.wt = fmt
        
    def set_rows(self, rows):
        self.params.rows = rows
        
    def set_start(self, start):
        self.params.start = start
        
    def set_fields(self, fields):
        if isinstance(fields, list):
            self.params.fl = ','.join(fields)
        elif isinstance(fields, basestring):
            self.params.fl = fields
        else:
            raise Exception("fields must be expressed as a list or comma-separated string")
        
    def set_sort(self, sort_field, direction="asc"):
        self.params.sort = "%s %s" % (sort_field, direction)
        
    def add_sort(self, sort_field, direction="asc"):
        if not self.params.has_key('sort'):
            self.set_sort(sort_field, direction)
        else:
            self.params.sort += ',%s %s' % (sort_field, direction)
        
    def set_hlq(self, hlq):
        self.params['hl.q'] = hlq
        
    def add_filter(self, filter_):
        self.params.append('fq', filter_)
        
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
    
    def get_raw_request_url(self):
        qstring = []
        to_str = lambda s: s.encode('utf-8') if isinstance(s, unicode) else s
        for key, value in self.params.items():
#            key = key.replace(self.arg_separator, '.')
            if isinstance(value, (list, tuple)):
                qstring.extend([(key, to_str(v)) for v in value])
            else:
                qstring.append((key, to_str(value)))
        qstring = urlencode(qstring, doseq=True)
        return "%s/select?%s" % (g.solr.url, qstring)
        
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
                                