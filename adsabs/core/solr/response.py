'''
Created on Sep 19, 2012

@author: jluker
'''

import logging

from config import config
from solrdoc import SolrDocument

from flask import request as current_request, current_app as app
from flask.ext.solrquery import SearchResponseMixin 

__all__ = ['SolrResponse']

class SolrResponse(SearchResponseMixin):
    
    def __init__(self, data, request, http_response, **kwargs):
        self.raw = data
        self.request = request
        self.http_response = http_response
        self.meta = {}
        
    def is_error(self):
        return self.raw.get('responseHeader',{}).get('status', False)
    
    def get_http_status(self):
        return self.http_response.status_code
    
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
    
    def get_error_message(self):
        """Function to remove the useless part of the error message coming from SOLR"""
        error_message = self.get_error()
        if error_message:
            if error_message.startswith('org.apache.lucene'):
                error_split = error_message.split(':', 1)
                if len(error_split) > 1:
                    return (''.join(error_split[1])).strip()
                else:
                    return 'Unspecified error from search engine.'
            else:
                return error_message
        else:
            return None
    
    def add_meta(self, key, value):
        self.meta[key] = value
        
    def raw_response(self):
        return self.raw
    
    def get_docset_objects(self):
        return [SolrDocument(x) for x in self.get_docset()]

    def get_doc_object(self, idx):
        doc = self.get_doc(idx)
        if doc:
            return SolrDocument(doc)
    
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
            search_filters = self.request.get_param('ui_filters')
            #I extract only the parameters of the allowed facets
            inverted_allowed_facet_dict = dict((v,k) for k,v in config.ALLOWED_FACETS_FROM_WEB_INTERFACE.iteritems())
            for filter_val in search_filters:
                filter_split = filter_val.split(':', 1)
                filter_query_name = filter_split[0]
                
                #if the filter starts with a "-" sign (exclude), need to remove it and prepend to the value
                negative_filter = filter_query_name.startswith(u'-')
                if negative_filter:
                    filter_query_name = filter_query_name[1:]
                
                #remove the filter query parser if present
                if config.SOLR_FILTER_QUERY_PARSER:
                    if filter_query_name.startswith(u"{!%s}" %  config.SOLR_FILTER_QUERY_PARSER):
                        filter_query_name = filter_query_name[len(u"{!%s}" %  config.SOLR_FILTER_QUERY_PARSER):]
                
                if filter_query_name in inverted_allowed_facet_dict:
                    facet_name = inverted_allowed_facet_dict[filter_query_name]
                    filter_value = filter_split[1].strip('"')
                    if negative_filter:
                        filter_value = u'-%s' % filter_value
                    facet_params.append((facet_name, filter_value))
                        
            self.request_facet_params = facet_params
        return self.request_facet_params
    
    def get_pagination(self):
        """
        wrap default pagination but use our row count setting
        """
        try:
            num_rows = int(self.request.params.rows)
        except (ValueError, TypeError):
            num_rows = int(config.SEARCH_DEFAULT_ROWS)
        return super(SolrResponse, self).get_pagination(rows_per_page=num_rows)
        
        
