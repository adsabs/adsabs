'''
Created on Nov 30, 2012

@author: dimilia
'''

import logging
from adsabs.core.logevent import LogEvent
from werkzeug.datastructures import CombinedMultiDict
from config import config
from flask import g, session


def build_basicquery_components(form, request_values=CombinedMultiDict([]), facets_components=False):
    """
    Takes in input a validated basic form and returns a dictionary containing 
    all the components needed to run a SOLR query
    """
    search_components = {
            'q' : None,
            'filters': [],
            'sort': config.SEARCH_DEFAULT_SORT,
            'start': None,
            'sort_direction':config.SEARCH_DEFAULT_SORT_DIRECTION,
    }
    #one box query
    search_components['q'] = form.q.data
    #databases
    if form.db_key.data in ('ASTRONOMY', 'PHYSICS',):
        search_components['filters'].append('database:%s' % form.db_key.data)
    #sorting
    if form.sort_type.data in config.SOLR_SORT_OPTIONS.keys():
        search_components['sort'] = form.sort_type.data
    #second order operators wrap the query
    elif form.sort_type.data in config.SEARCH_SECOND_ORDER_OPERATORS_OPTIONS:
        search_components['q'] = u'%s(%s)' % (form.sort_type.data, search_components['q'])
        search_components['sort'] = None
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
        search_components['filters'].append(u'pubdate:[%s TO %s]' % (mindate, maxdate))
    #refereed
    if form.refereed.data:
        search_components['filters'].append(u'property:REFEREED')
    #articles only
    if form.article.data:
        search_components['filters'].append(u'-property:NONARTICLE')
    #journal abbreviation
    if form.journal_abbr.data:
        journal_abbr_string = ''
        for bibstem in form.journal_abbr.data.split(','):
            journal_abbr_string += u'bibstem:%s OR ' % bibstem.strip()
        search_components['filters'].append(journal_abbr_string[:-4]) 
    #the facets that are not included in the form
    for facet in config.ALLOWED_FACETS_FROM_WEB_INTERFACE:
        for elem in request_values.getlist(facet):
            #I have to distinguish between a simple facet and a complex one
            if not (elem.startswith('(') or elem.startswith('[') or elem.startswith('-(')):
                search_components['filters'].append(u'%s:"%s"' % (config.ALLOWED_FACETS_FROM_WEB_INTERFACE[facet], elem))
            else:
                search_components['filters'].append(u'%s:%s' % (config.ALLOWED_FACETS_FROM_WEB_INTERFACE[facet], elem))            
    #I handle the page number
    page = request_values.get('page')
    if page:
        try:
            int_page = int(page)
        except ValueError:
            int_page = None
        if int_page >0:
            search_components['start'] = str((int(page) - 1) * int(config.SEARCH_DEFAULT_ROWS))
    #re-sorting options
    if request_values.get('re_sort_type') in config.RE_SORT_OPTIONS.keys():
        search_components['sort'] = request_values.get('re_sort_type')
        if request_values.get('re_sort_dir') in ['asc', 'desc']:
            search_components['sort_direction'] = request_values.get('re_sort_dir')       
    
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
                    search_components['facet_fields']= []
                    search_components['facet_field_interf_id'] = facet_field_interface
                    try:
                        facet_config = list(filter(lambda x: x[0] == config.ALLOWED_FACETS_FROM_WEB_INTERFACE[facet_field], config.SOLR_SEARCH_DEFAULT_FACETS)[0])
                        #I want all the sublevel facets
                        facet_config[1] = -1
                        facet_config[4] = facet_prefix
                        search_components['facet_fields'].append(tuple(facet_config))
                    except IndexError:
                        pass
        
    return search_components

def build_singledoc_components(request_values):
    """
    Query components for queries not coming from the search forms (like the list of references or citations)
    """
    search_components = {
            'sort': config.SEARCH_DEFAULT_SORT,
            'start': None,
            'sort_direction':config.SEARCH_DEFAULT_SORT_DIRECTION,
    }
    #I handle the page number
    page = request_values.get('page')
    if page:
        try:
            int_page = int(page)
        except ValueError:
            int_page = None
        if int_page >0:
            search_components['start'] = str((int(page) - 1) * int(config.SEARCH_DEFAULT_ROWS))
    #re-sorting options
    if request_values.get('re_sort_type') in config.RE_SORT_OPTIONS.keys():
        search_components['sort'] = request_values.get('re_sort_type')
        if request_values.get('re_sort_dir') in ['asc', 'desc']:
            search_components['sort_direction'] = request_values.get('re_sort_dir')
    return search_components
    
def log_search(resp):
    data = {
        'q': resp.get_query(),
        'hits': resp.get_hits(),
        'count': resp.get_count(),
        'start': resp.get_start_count(),
        'qtime': resp.get_qtime(),
#        'user_cookie_id': g.user_cookie_id,
        }
    event = LogEvent.new(**data)
    logging.getLogger('search').info(event)
    
    
    
    