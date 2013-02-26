'''
Created on Nov 30, 2012

@author: dimilia
'''

from werkzeug.datastructures import CombinedMultiDict
from config import config

#def _get_page_component(request_values):
#    """"Handles the page number component that is a function of the max number of results in the page """
#    page = request_values.get('page')
#    if page:
#        if int(page) >0:
#            return str((int(page) - 1) * int(config.SEARCH_DEFAULT_ROWS))
#    return None
#
#def _get_resorting_component(request_values):
#    """Handles the resorting components"""
#    sort = config.SEARCH_DEFAULT_SORT
#    sort_direction = config.SEARCH_DEFAULT_SORT_DIRECTION
#    if request_values.get('re_sort_type') in config.RE_SORT_OPTIONS.keys():
#        sort = request_values.get('re_sort_type')
#        if request_values.get('re_sort_dir') in ['asc', 'desc']:
#            sort_direction = request_values.get('re_sort_dir')       
#    return sort, sort_direction

def build_basicquery_components(form, request_values=CombinedMultiDict([])):
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
        mindate = '*'
        maxdate = '*'
        if form.year_from.data:
            if form.month_from.data:
                mindate = u'%s%s00' % (form.year_from.data, unicode(form.month_from.data).zfill(2))
            else:
                mindate = u'%s%s00' % (form.year_from.data, u'00')
        if form.year_to.data:
            if form.month_to.data:
                maxdate = u'%s%s00' % (form.year_to.data, unicode(form.month_to.data).zfill(2))
            else:
                maxdate = u'%s%s00' % (form.year_to.data, u'13')
        search_components['filters'].append(u'pubdate_sort:[%s TO %s]' % (mindate, maxdate))
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
    for facet in config.ALLOWED_FACETS_FROM_WEB_INTERFACE.keys():
        for elem in request_values.getlist(facet):
            search_components['filters'].append(u'%s:"%s"' % (config.ALLOWED_FACETS_FROM_WEB_INTERFACE[facet], elem))
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
        
    # facet field/prefix options
    if request_values.get('facet_field'):
        field = request_values.get('facet_field')
        try:
            facet_config = filter(lambda x: x[0] == field, config.SOLR_SEARCH_DEFAULT_FACETS)[0]
            search_components['facet_fields'] = [facet_config]
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
    