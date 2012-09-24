'''
Created on Sep 19, 2012

@author: jluker
'''

class SolrDocument(object):
        
    def __init__(self, data):
        self.data = data
        
    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]

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
        