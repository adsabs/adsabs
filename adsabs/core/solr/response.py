'''
Created on Sep 19, 2012

@author: jluker
'''

import logging
from adsabs.core.logevent import LogEvent
from math import ceil
from copy import deepcopy

from config import config
from .solrdoc import SolrDocument

from flask import current_app as app

class SolrResponse(object):
    
    def __init__(self, raw, request=None):
        self.raw = deepcopy(raw)
        self.request = request
        self.meta = {}
        
    def is_error(self):
        return self.raw['responseHeader']['status'] != 0
    
    def search_response(self):
        
        self.meta.update({
                'query': self.get_query(),
                'qtime': self.get_qtime(),
                'hits': self.get_hits(),
                'count': self.get_count(),
        })
        
        resp = {
            'meta': self.meta,
            'results': {
                'docs': self.get_docset(),
            }
        }
        
        if self.request.facets_on():
            resp['results']['facets'] = self.get_all_facets()
            
        return resp
    
    def record_response(self, idx=0):
        try:
            return self.get_docset()[idx]
        except IndexError:
            return None
    
    def get_error_components(self):
        """Extracts all the components of an error from the response object"""
        if self.is_error():
            return self.raw['error']
        else:
            return {}
    
    def get_error(self):
        """Function that returns the raw error message"""
        error_components = self.get_error_components()
        return error_components.get('msg', None)
    
    def get_error_message(self):
        """Function to remove the useless part of the error message coming from SOLR"""
        error_message = self.get_error()
        if error_message:
            if error_message.startswith('org.apache.lucene'):
                return (''.join(error_message.split(':', 1)[1])).strip()
            else:
                return error_message
        else:
            return None
    
    def add_meta(self, key, value):
        self.meta[key] = value
        
    def raw_response(self):
        return self.raw
    
    def get_docset(self):
        if self.raw.has_key('response'):
            docset = self.raw['response'].get('docs', [])
            if self.request.highlights_on() and self.raw.has_key('highlighting'):
                for doc in docset:
                    doc['highlights'] = self.raw['highlighting'][doc['id']]
            return self.raw['response'].get('docs', [])
        else:
            return []
    
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
            app.logger.debug("response has no doc at idx %d" % idx)
            
    def get_doc_values(self, field, start=0, stop=None):
        docs = self.get_docset()
        return [x.get(field, None) for x in docs[int(start):int(stop)]]
    
    def get_all_facets(self):
        if not self.request.facets_on():
            return {}
        return self.raw['facet_counts']
    
    def get_all_facet_fields(self):
        return self.get_all_facets().get('facet_fields',{})
    
    def get_all_facet_queries(self):
        return self.get_all_facets().get('facet_queries',{})
    
    def get_facets_fields(self, facet_name, hierarchical=False):
        """
        Returns the facets list for a specific facet.
        It takes care of checking if the facet has been selected 
        """
        if not self.request.facets_on():
            return []
        solr_field_name = config.ALLOWED_FACETS_FROM_WEB_INTERFACE.get(facet_name, None)
        
        #I extract the facets from the raw response
        if self.raw.has_key('facet_counts'):
            raw_facet_fields = self.raw['facet_counts']['facet_fields']
        else:
            raw_facet_fields = {}
        facets_list = raw_facet_fields.get(solr_field_name, [])
        
        #I split the list in tuples
        facets_tuples_list = [tuple(facets_list[i:i+2]) for i in xrange(0, len(facets_list), 2)]
        
        #I extract the facet parameter submitted
        query_parameters = self.get_facet_param_field(facet_name)
        
        if not hierarchical:
            return sorted([(elem[0], elem[1], 'selected') if elem[0] in query_parameters else (elem[0], elem[1], '') for elem in facets_tuples_list], key= lambda x: (-x[1], x[0]))
        else:
            return sorted([tuple(elem[0].split('/') + [elem[1], 'selected', elem[0]]) if elem[0] in query_parameters else tuple(elem[0].split('/') + [elem[1], '', elem[0]]) for elem in facets_tuples_list], key= lambda x: (-x[-3], x[-4]))
        
    def get_hier_facets_fields(self, facet_name):
        """
        Like get_facets_fields but returns a more complex structure for the hierarchical facets 
        """
        def update_multidict(fac_dict, hier_facet):
            """ Function to create the data structure for the facets"""
            x = fac_dict
            level = hier_facet[0]
            fac_list = hier_facet[1:-2]
            last_value = hier_facet[-2]
            selection = hier_facet[-1]
            for i in range(int(level) +1):
                if i != int(level):
                    x = x[fac_list[i]][2]
                else:
                    x[fac_list[i]] = (last_value, selection, {})
        def fac_dict_to_tuple(fac_dict):
            """Returns a tuple version of the dictionary of facets"""
            tuple_facets = sorted(fac_dict.items(), key= lambda x: (-x[1][0], x[0]))
            ret_list = []
            for elem in tuple_facets:
                if not elem[1][2]:
                    ret_list.append(elem)
                else:
                    ret_list.append((elem[0], (elem[1][0], elem[1][1], fac_dict_to_tuple(elem[1][2]))))
            return tuple(ret_list)
                    
        if not self.request.facets_on():
            return []
        solr_field_name = config.ALLOWED_FACETS_FROM_WEB_INTERFACE.get(facet_name, None)
        
        raw_facet_fields = self.raw['facet_counts']['facet_fields']
        facets_list = raw_facet_fields.get(solr_field_name, [])
        #I split the list in tuples
        facets_tuples_list = [tuple(facets_list[i:i+2]) for i in xrange(0, len(facets_list), 2)]
        
        #I extract the facet parameter submitted
        query_parameters = self.get_facet_param_field(facet_name)
        #then I put all the levels of the hierarchical facets in a unique tuple
        hier_facets_split = [tuple(elem[0].split('/') + [elem[1], 'selected']) if elem[0] in query_parameters else tuple(elem[0].split('/') + [elem[1], '']) for elem in facets_tuples_list]
        #I sort the tuples because I need them in the right order to fill in the dictionary
        hier_facets_split.sort(key = lambda x: (x[0], -x[-2]))
        #I re organize the facets
        final_facets = {}
        for elem in hier_facets_split:
            update_multidict(final_facets, elem)
        #then I convert them back to lists of tuples and I return it
        return fac_dict_to_tuple(final_facets)
        
    
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
                filter_query_name = filter_split[0]
                #remove the filter query parser if present
                if config.SOLR_FILTER_QUERY_PARSER:
                    if filter_query_name.startswith(u"{!%s}" %  config.SOLR_FILTER_QUERY_PARSER):
                        filter_query_name = filter_query_name[len(u"{!%s}" %  config.SOLR_FILTER_QUERY_PARSER):]
                if filter_query_name in inverted_allowed_facet_dict:
                    facet_name = inverted_allowed_facet_dict[filter_query_name]
                    facet_params.append((facet_name, filter_split[1].strip('"')))
                        
            self.request_facet_params = facet_params
        return self.request_facet_params
    
    def get_query(self):
        return self.raw['responseHeader']['params']['q']
    
    def get_count(self):
        """
        Returns number of documents in current response
        """
        if self.raw.has_key('response'):
            return len(self.raw['response']['docs'])
        else:
            return 0
    
    def get_hits(self):
        """
        Returns the total number of record found
        """
        if self.raw.has_key('response'):
            return int(self.raw['response']['numFound'])
        else:
            return 0
    
    def get_start_count(self):
        """
        Returns the number of the first record in the 
        response compared to the total number
        """
        if self.raw.has_key('response'):
            return int(self.raw['response']['start'])
        else:
            return 0
    
    def get_pagination(self):
        """
        Returns a dictionary containing all the informations
        about the status of the pagination 
        """
        if not hasattr(self, 'pagination'):
            max_pagination_len = 5 #maybe we want to put this in the configuration
            num_total_pages = int(ceil(float(self.get_hits()) / float(config.SEARCH_DEFAULT_ROWS)))
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
    
    def log_search(self, logger_name, **xtra):
        """
        extracts some data from the response for log/analytics purposes
        """
        data = {
            'q': self.get_query(),
            'hits': self.get_hits(),
            'count': self.get_count(),
            'start': self.get_start_count(),
            'qtime': self.get_qtime(),
            'results': self.get_doc_values('bibcode', 0, config.SEARCH_DEFAULT_ROWS),
            'solr_url': self.request.get_raw_request_url(),
            }
        data.update(xtra)
        event = LogEvent.new(**data)
        logging.getLogger(logger_name).info(event)        
        
        
