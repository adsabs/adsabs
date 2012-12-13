'''
Created on Sep 19, 2012

@author: jluker
'''

import logging
from simplejson import loads,dumps
from math import ceil
from config import config
from .solrdoc import SolrDocument
from copy import deepcopy

log = logging.getLogger(__name__)

class SolrResponse(object):
    
    def __init__(self, raw, request=None):
        self.raw = deepcopy(raw)
        self.request = request
        
    def is_error(self):
        return self.raw['responseHeader']['status'] != 0
    
    def search_response(self):
        resp = {
            'meta': { 
                'query': self.get_query(),
                'qtime': self.get_qtime(),
                'count': self.get_count(),
             },
            'results': {
                'docs': self.get_docset(),
                'facets': self.get_all_facets(),
            }
        }
        return resp
    
    def record_response(self, idx=0):
        try:
            return self.get_docset()[idx]
        except IndexError:
            return None
        
    def get_error(self):
        return self.raw['error']['msg']
    
    def raw_response(self):
        return self.raw
    
    def get_docset(self):
        docset = self.raw['response'].get('docs', [])
        if self.raw.has_key('highlighting'):
            for doc in docset:
                doc['highlights'] = self.raw['highlighting'][doc['id']]
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
    
    def get_all_facets(self):
        if not self.request.facets_on():
            return {}
        return self.raw['facet_counts']
    
    def get_facets_fields(self, facet_name):
        """
        Returns the facets list for a specific facet.
        It takes care of checking if the facet has been selected 
        """
        if not self.request.facets_on():
            return []
        solr_field_name = config.ALLOWED_FACETS_FROM_WEB_INTERFACE.get(facet_name, None)
        
        #I extract the facets from the raw response
        raw_facet_fields = self.raw['facet_counts']['facet_fields']
        facets_list = raw_facet_fields.get(solr_field_name, [])
        
        #I split the list in tuples
        facets_tuples_list = [tuple(facets_list[i:i+2]) for i in xrange(0, len(facets_list), 2)]
        
        #I extract the facet parameter submitted
        query_parameters = self.get_facet_param_field(facet_name)
        return [(elem[0], elem[1], 'selected') if elem[0] in query_parameters else (elem[0], elem[1], '') for elem in facets_tuples_list]
    
    def get_hier_facets_fields(self, facet_name):
        """
        Like get_facets_fields but returns a more complex structure for the hierarchical facets 
        """
        if not self.request.facets_on():
            return []
        solr_field_name = config.ALLOWED_FACETS_FROM_WEB_INTERFACE.get(facet_name, None)
    
    
    def get_facet_param_field(self, facet_name):
        """
        Returns the list of query parameters for the current facet name
        """
        return [elem[1] for elem in self.get_facet_parameters() if elem[0] == facet_name]
    
    def get_facet_parameters(self):
        """
        Returns the list of query parameters
        """
        if not hasattr(self, 'request_facet_params'):
            facet_params = []
            #first I extract the query parameters excluding the default ones
            search_filters = self.request.get_filters(exclude_defaults=True)
            #I extract only the parameters of the allowed facets
            inverted_allowed_facet_dict = dict((v,k) for k,v in config.ALLOWED_FACETS_FROM_WEB_INTERFACE.iteritems())
            for filter_val in search_filters:
                filter_split = filter_val.split(':', 1)
                if filter_split[0] in inverted_allowed_facet_dict:
                    facet_name = inverted_allowed_facet_dict[filter_split[0]]
                    facet_params.append((facet_name, filter_split[1].strip('"')))
                        
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
        Returns a dictionary containing all the informations
        about the status of the pagination 
        """
        try:
            self.pagination
        except AttributeError:
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
            self.pagination = {
                   'max_pagination_len':max_pagination_len ,
                   'num_total_pages': num_total_pages,
                   'current_page': current_page,
                   'pages_before': pages_before,
                   'pages_after': pages_after,       
            }
        return self.pagination
    
    def get_qtime(self):
        return self.raw['responseHeader']['QTime']
        
        