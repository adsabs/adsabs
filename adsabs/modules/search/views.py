from flask import Blueprint, request, g, render_template

from flask.ext.login import current_user #@UnresolvedImport
from .forms import QueryForm, get_defaults_if_missing
from adsabs.core.solr import query
from config import config

#I define the blueprint
search_blueprint = Blueprint('search', __name__, template_folder="templates", static_folder="static")

__all__ = ['search_blueprint','search', 'search_advanced']


def build_basicquery_components(form):
    """
    Takes in input a validated basic form and returns a dictionary containing 
    all the components needed to run a SOLR query
    """
    search_components = {
            'q' : None,
            'filters': [],
            'sort': None,
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
                maxdate = 'u%s%s00' % (form.year_to.data, unicode(form.month_to.data).zfill(2))
            else:
                maxdate = u'%s%s00' % (form.year_to.data, u'00')
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
            journal_abbr_string += u'bibstem:%s OR' % bibstem
        search_components['filters'].append(journal_abbr_string[:-3])   
    return search_components


@search_blueprint.route('/', methods=('GET', 'POST'))
def search():
    """
    returns the results of a search
    """
    #I add the default values if they have not been submitted by the form and I create the new form
    form = QueryForm(get_defaults_if_missing(request.values, QueryForm), csrf_enabled=False)
    if form.validate():
        query_components = build_basicquery_components(form)
        resp = query(query_components['q'], filters=query_components['filters'], sort=query_components['sort'])
        return render_template('search_results.html', resp=resp, form=form)

    
    return render_template('search.html', form=form)

@search_blueprint.route('/advanced/', methods=('GET', 'POST'))
def search_advanced():
    """
    """
    pass