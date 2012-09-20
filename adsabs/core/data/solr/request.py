'''
Created on Sep 19, 2012

@author: jluker
'''

from flask import g
from .response import SolrResponse
from .solrdoc import *

from config import DefaultConfig as config

def query(q, **kwargs):
    req = SolrRequest(q, **kwargs)
    return req.get_response()

class SolrRequest(object):
    
    def __init__(self, q, rows=config.SOLR_DEFAULT_ROWS):
        self.q = q
        self.rows = rows
        
    def get_response(self):
        json = g.solr.raw_query(
                               q = self.q, 
                               fields=config.SOLR_DEFAULT_FIELDS_SEARCH,
                               sort=config.SOLR_DEFAULT_SORT,
                               rows=self.rows,
                               wt='json'
                               )
        return SolrResponse.from_json(json)
                                