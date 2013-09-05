'''
Created on Nov 30, 2012

@author: dimilia
'''

from copy import deepcopy
from werkzeug.datastructures import CombinedMultiDict
from config import config
from adsabs.core.exceptions import ConfigurationError
from flask import current_app as app

import sys
THIS_MODULE = sys.modules[__name__]

def _append_to_list(list_, item):
    """
    Simple append to a list
    """
    cur_list = deepcopy(list_)
    cur_list.append(item)
    return cur_list
    
def _append_to_query(query, item):
    """
    Append to query string
    """
    return u'%s AND %s' % (query, item)

class QueryBuilderSearch(object):

    DEFAULT_COMPONENTS = {
            'q' : None,
            'filter_queries': [],
            'ui_q':None,
            'ui_filters': [],
            'sort': (config.SOLR_SORT_OPTIONS[config.SEARCH_DEFAULT_SORT],config.SEARCH_DEFAULT_SORT_DIRECTION),
            'rows':config.SEARCH_DEFAULT_ROWS,
            'fields': config.SOLR_SEARCH_DEFAULT_FIELDS,
            'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
            'highlights': config.SOLR_SEARCH_DEFAULT_HIGHLIGHTS,
            'facets': config.SOLR_SEARCH_DEFAULT_FACETS
            }

    @classmethod
    def build(cls, form, request_values=CombinedMultiDict([]), facets_components=False):
        """
        Takes in input a validated basic form and returns a dictionary containing 
        all the components needed to run a SOLR query
        """

        search_components = deepcopy(cls.DEFAULT_COMPONENTS)
        
        def add_filter_to_search_components(facet_name, value, force_to_q=False):
            """
            Internal function that takes care of appending to the search components 
            """
            #if force to query is set, there is no need to proceed with the rest
            if force_to_q:
                search_components['q'] = _append_to_query(search_components['q'], value)
                return None
            
            #by default if there is not a real configuration the facets are considered as  query 
            #and the default function is a simple append to the query string
            mode = config.FACET_TO_SOLR_QUERY.get(facet_name, {}).get('default_mode', 'q')
            funct_mame = config.FACET_TO_SOLR_QUERY.get(facet_name, {}).get('default_function', '_append_to_query')
            #actually load the right function specified in the config file
            try:    
                funct = getattr(THIS_MODULE, funct_mame)
            except AttributeError:
                raise ConfigurationError('function %s in configuration file but not implemented' % funct_mame)
                    
            if mode == 'q':
                search_components['q'] = funct(search_components['q'], value)
            elif mode == 'fq':
                search_components['filter_queries'] = funct(search_components['filter_queries'], value)
            #this function doesn't return anything: if modifies the search_components variable
            return None
        
        #one box query
        search_components['q'] = u'(%s)' % form.q.data
        search_components['ui_q'] = form.q.data
          
        #date range
        if form.year_from.data or form.year_to.data:
            mindate = '0001-00-00' #'*' the * has a bug
            maxdate = '9999-00-00' #'*' the * has a bug
            if form.year_from.data:
                if form.month_from.data:
                    mindate = u'%s-%s-00' % (form.year_from.data, unicode(form.month_from.data).zfill(2))
                else:
                    mindate = u'%s-%s-00' % (form.year_from.data, u'00')
            if form.year_to.data:
                if form.month_to.data:
                    maxdate = u'%s-%s-00' % (form.year_to.data, unicode(form.month_to.data).zfill(2))
                else:
                    maxdate = u'%s-%s-00' % (form.year_to.data, u'12')
            add_filter_to_search_components('pubdate', u'pubdate:[%s TO %s]' % (mindate, maxdate))
            search_components['ui_filters'].append(u'pubdate:[%s TO %s]' % (mindate, maxdate))
    
        #articles only
        if form.article.data:
            add_filter_to_search_components('prop_f', u'NOT property:NONARTICLE', force_to_q=True)
            
        #disable fulltext
        if form.no_ft.data:
            #if the param is set by default the conf is set to the limited value
            search_components['query_fields'] = config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS_METADATA_ONLY
            #if there is only one field in raw_data and its 
            if len(form.no_ft.raw_data) == 1:
                if form.no_ft.raw_data[0] == '1':
                    #the default value is ok here
                    pass
                else:
                    #otherwise the parameter will be the custom one
                    search_components['query_fields'] = form.no_ft.raw_data[0]
            
        #number of rows
        if form.nr.data and form.nr.data != 'None':
            search_components['rows'] = form.nr.data
        
        #the facets that are not included in the form
        for facet in config.ALLOWED_FACETS_FROM_WEB_INTERFACE:
            for elem in request_values.getlist(facet):
                #I have to distinguish between a simple facet and a complex one
                if not (elem.startswith('(') or elem.startswith('[') or elem.startswith('-(')):
                    cur_filter = u'%s:"%s"' % (config.ALLOWED_FACETS_FROM_WEB_INTERFACE[facet], elem)
                    cur_filter_ui = cur_filter
                    add_filter_to_search_components(facet, cur_filter)
                else:
                    if elem.startswith('-('):
                        cur_filter = u'NOT %s:%s' % (config.ALLOWED_FACETS_FROM_WEB_INTERFACE[facet], elem[1:])
                        cur_filter_ui = u'-%s:%s' % (config.ALLOWED_FACETS_FROM_WEB_INTERFACE[facet], elem[1:])
                        add_filter_to_search_components(facet, cur_filter, force_to_q=True)
                    else:
                        cur_filter = u'%s:%s' % (config.ALLOWED_FACETS_FROM_WEB_INTERFACE[facet], elem)
                        cur_filter_ui = cur_filter
                        add_filter_to_search_components(facet, cur_filter)
                search_components['ui_filters'].append(cur_filter_ui)
        #I handle the page number
        page = request_values.get('page')
        if page:
            try:
                int_page = int(page)
            except ValueError:
                int_page = None
            if int_page >0:
                search_components['start'] = str((int(page) - 1) * int(search_components['rows']))
    
        #If I'm managing facets components
        if facets_components:
            # facet field/prefix options
            facet_field_interface = request_values.get('facet_field')
            facet_prefix = request_values.get('facet_prefix')    
            if facet_field_interface and facet_prefix:
                if facet_field_interface in config.FACETS_IN_TEMPLATE_CONFIG:
                    facet_field = config.FACETS_IN_TEMPLATE_CONFIG[facet_field_interface]['facetid']
                    #if the facet is allowed 
                    if facet_field in config.ALLOWED_FACETS_FROM_WEB_INTERFACE:
                        #I add the tuple containing the facet that I want to extract
                        search_components['facets']= []
                        search_components['facet_field_interf_id'] = facet_field_interface
                        try:
                            facet_config = list(filter(lambda x: x[0] == config.ALLOWED_FACETS_FROM_WEB_INTERFACE[facet_field], config.SOLR_SEARCH_DEFAULT_FACETS)[0])
                            #I want all the sublevel facets
                            facet_config[1] = -1
                            facet_config[4] = facet_prefix
                            search_components['facets'].append(tuple(facet_config))
                        except IndexError:
                            pass
    
        # update any sort options
        sort_options = create_sort_param(request_values)
        if sort_options is not None:
            search_components['sort'] = sort_options
        
        #wrapping the query with topn function if there is a valid number (the validation must be done in the form) 
        if form.topn.data and form.topn.data != 'None':
            set_topn_query(form.topn.data, search_components, request_values)
            
        return search_components
    
class QueryBuilderSimple(object):
    
    DEFAULT_COMPONENTS = {
        'sort': (config.SOLR_SORT_OPTIONS[config.SEARCH_DEFAULT_SORT],config.SEARCH_DEFAULT_SORT_DIRECTION),
        'rows': config.SEARCH_DEFAULT_ROWS
    }

    @classmethod
    def build(cls, request_values):
        """
        Query components for queries not coming from the search forms (like the list of references or citations)
        """
        search_components = deepcopy(cls.DEFAULT_COMPONENTS)

        #I handle the page number
        page = request_values.get('page')
        if page:
            try:
                int_page = int(page)
            except ValueError:
                int_page = None
            if int_page >0:
                search_components['start'] = str((int(page) - 1) * int(config.SEARCH_DEFAULT_ROWS))

        # update any sort options
        sort_options = create_sort_param(request_values)
        if sort_options is not None:
            search_components['sort'] = sort_options

        return search_components

def create_sort_param(rv):    
    sort_type = rv.get('re_sort_type')
    sort_dir = rv.get('re_sort_dir')

    #re-sorting options
    if sort_type in config.RE_SORT_OPTIONS and sort_dir in ['asc','desc']:
        return (config.RE_SORT_OPTIONS[sort_type], sort_dir)
    elif sort_type in config.RE_SORT_OPTIONS and sort_dir is None:
        return (config.RE_SORT_OPTIONS[sort_type], config.SEARCH_DEFAULT_SORT_DIRECTION)
    else:
        if sort_type is not None or sort_dir is not None:
            app.logger.error("Got bad sort options: %s, %s" % (sort_type, sort_dir))
        return None

def set_topn_query(topn, sc, rv):    
    sort_type = rv.get('re_sort_type', 'RELEVANCE')
    if sort_type is 'RELEVANCE':
        # sorting by solr score doesn't allow a direction
        topn_sort = config.RE_SORT_OPTIONS[sort_type]
    else:
        # use the tuple we created in the previous sort step
        topn_sort = "%s %s" % sc['sort']
            
    # if the topn is used, no sorting is needed by SOLR
    #sc['sort'] = None #actually for some reason Roman needs the sorting
    sc['q'] = u'topn(%s, (%s), "%s")' % (topn, sc['q'], topn_sort)
    
    