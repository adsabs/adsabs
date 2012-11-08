'''
Created on Sep 19, 2012

@author: jluker
'''

from flask import g
from config import config
from .response import SolrResponse

class SolrParams(dict):
    
    def __init__(self, *args, **kwargs):
        # set default values
        self.update(
                    config.SOLR_DEFAULT_PARAMS,
                    fl=','.join(config.SOLR_DEFAULT_FIELDS_SEARCH),
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
        
class SolrRequest(object):
    
    def __init__(self, q, **kwargs):
        self.q = q
        self.params = SolrParams(q=q, **kwargs)
        
    def get_response(self):
        json = g.solr.raw_query(**self.params)
        return SolrResponse.from_json(json, request=self)
        
                                