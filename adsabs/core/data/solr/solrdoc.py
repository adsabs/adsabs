'''
Created on Sep 19, 2012

@author: jluker
'''

from config import DefaultConfig as config
from urllib2 import quote
from urllib import urlencode

from adsabs.core.data.invenio import record_url
from adsabs.core.data.classic import abstract_url

class SolrDocument(object):
        
    def __init__(self, data):
        self.data = data
        
    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]

    def classic_url(self):
        return abstract_url(self.bibcode)
    
    def invenio_url(self):
        return record_url(self.recid)
    
    def invenio_marcxml_url(self):
        return record_url(self.recid, of='xm')
    
    def solr_url(self, wt=None):
        if wt is None:
            return config.SOLR_URL + '/select?q=id:' + quote(str(self.id))
        else:
            return self.document_url() + urlencode({'wt': wt})
        
class SolrFacets(object):
    
    @staticmethod
    def from_dict(facet_data):
        queries = facet_data['facet_queries']
        fields = facet_data['facet_fields']
        dates = facet_data['facet_dates']
        ranges = facet_data['facet_ranges']
        return SolrFacets(fields, queries, dates, ranges)
        
    def __init__(self, fields, queries={}, dates={}, ranges={}):
        self.queries = queries
        self.fields = fields
        self.dates = dates
        self.ranges = ranges
        