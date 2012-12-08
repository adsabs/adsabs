'''
Created on Sep 19, 2012

@author: jluker
'''

import logging
from simplejson import loads,dumps
from math import ceil

from config import config
from .solrdoc import SolrDocument, SolrFacets

log = logging.getLogger(__name__)

class SolrResponse(object):
    
    def __init__(self, raw, request=None):
        self.raw = raw
        self.request = request
        
    def search_response(self):
        resp = {
            'meta': { 'errors': None },
            'results': {
                'count': self.get_count(),
                'docs': self.get_docset(),
                'facets': self.get_facets(),
            }
        }
        return resp
    
    def record_response(self, idx=0):
        try:
            return self.get_docset()[idx]
        except IndexError:
            return None
        
    def raw_response(self):
        return self.raw
    
    def get_docset(self):
        return self.raw['response'].get('docs', [])
    
    def get_docset_objects(self):
        return [SolrDocument(x) for x in self.get_docset()]

    def get_doc_object(self, idx):
        doc = self.get_doc(idx)
        if doc:
            return SolrDocument(doc)
    
    def get_doc(self, idx):
        try:
            return self.get_docset()[idx]
        except IndexError:
            log.debug("response has no doc at idx %d" % idx)
    
    def get_facets(self):
        return self.raw.get('facet_counts', {})
    
    def get_facets_fields(self, facet_name):
        #I extract the facets from the raw response
        facets_list = self.get_facets().get('facet_fields', {}).get(config.ALLOWED_FACETS_FROM_WEB_INTERFACE.get(facet_name, None), [])
        #I split the list in tuples
        facets_tuples_list = [tuple(facets_list[i:i+2]) for i in xrange(0, len(facets_list), 2)]
        #I extract the facet parameter submitted
        query_parameters = self.get_facet_param_field(facet_name)
        return [(elem[0], elem[1], 'selected') if elem[0] in query_parameters else (elem[0], elem[1], '') for elem in facets_tuples_list]
    
    def get_facet_param_field(self, facet_name):
        """
        Returns the list of query parameters for the current facet name
        """
        return [elem[1] for elem in self.get_facet_parameters() if elem[0] == facet_name]
    
    def get_facet_parameters(self):
        """
        Returns the list of query parameters
        """
        try: 
            self.request_facet_params
        except AttributeError:
            facet_params = []
            #first I extract the query parameters excluding the default ones
            search_params = list(set(self.request.params.get('fq', [])) - set(dict(config.SOLR_MISC_DEFAULT_PARAMS).get('fq', [])))
            #I extract only the parameters of the allowed facets
            for solr_facet in config.ALLOWED_FACETS_FROM_WEB_INTERFACE:
                for elem in search_params:
                    param = elem.split(':', 1)
                    if param[0] == config.ALLOWED_FACETS_FROM_WEB_INTERFACE[solr_facet]:
                        facet_params.append((solr_facet, param[1].strip('"')))
            self.request_facet_params = facet_params
        return self.request_facet_params
    
    def get_query(self):
        return self.raw['responseHeader']['params']['q']
    
    def get_count(self):
        """
        Returns the total number of record found
        """
        return int(self.raw['response']['numFound'])
    
    def get_start_count(self):
        """
        Returns the number of the first record in the 
        response compared to the total number
        """
        return int(self.raw['response']['start'])
    
    def get_count_in_resp(self):
        """
        Returns the number of records in the current response
        (it can be different from config.SEARCH_DEFAULT_ROWS)
        """
        return len(self.raw['response']['docs'])
    
    def get_pagination(self):
        """
        Returns a dictioary containing all the informations
        about the status of the pagination 
        """
        max_pagination_len = 5 #maybe we want to put this in the configuration
        num_total_pages = int(ceil(float(self.get_count()) / float(config.SEARCH_DEFAULT_ROWS)))
        current_page = (int(self.get_start_count()) / int(config.SEARCH_DEFAULT_ROWS)) + 1
        max_num_pages_before = int(ceil(min(max_pagination_len, num_total_pages) / 2.0)) - 1
        max_num_pages_after = int(min(max_pagination_len, num_total_pages)) / 2
        distance_to_1 = current_page - 1
        distance_to_max = num_total_pages - current_page
        num_pages_before = min(distance_to_1, max_num_pages_before)
        num_pages_after = min(distance_to_max, max_num_pages_after)
        if num_pages_before < max_num_pages_before:
            num_pages_after += max_num_pages_before - num_pages_before
        if num_pages_after < max_num_pages_after:
            num_pages_before += max_num_pages_after - num_pages_after 
        pages_before = sorted([current_page - i for i in range(1, num_pages_before+1)])
        pages_after = sorted([current_page + i for i in range(1, num_pages_after+1)])
        return {
               'max_pagination_len':max_pagination_len ,
               'num_total_pages': num_total_pages,
               'current_page': current_page,
               'pages_before': pages_before,
               'pages_after': pages_after,       
        }
    
    def get_qtime(self):
        return self.raw['responseHeader']['QTime']
        
        