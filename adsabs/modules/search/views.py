from flask import Blueprint, request, g, render_template

from flask.ext.login import current_user #@UnresolvedImport
from .forms import QueryForm, get_defaults_if_missing
from adsabs.core.solr import query
from config import config

#I define the blueprint
search_blueprint = Blueprint('search', __name__, template_folder="templates", static_folder="static")

__all__ = ['search_blueprint','search', 'search_advanced']


def build_query_components(form):
    """
    Takes in input a validated form and returns a dictionary containing 
    all the components needed to run a SOLR query
    """
    search_components = {
            'q' : None,
            'filters': [],
            'sort': None,
            'sort_direction':None,
            'rows': None,
            'start': None,
    }
    #one box query
    search_components['q'] = form['q'].data
    #databases
    if form.db_key.data in ('AST', 'PHY',):
        search_components['filters'].append('database:%' % form.db_key.data)
    #sorting
    if form.sort_type.data in config.SOLR_SORT_OPTIONS.keys():
        search_components['sort'] = form.sort_type.data
    #second order operators wrap the query
    elif form.sort_type.data in config.SEARCH_SECOND_ORDER_OPERATORS_OPTIONS:
        search_components['q'] = '%s(%s)' % (form.sort_type.data, search_components['q'])
    #date range
    if form.year_from.data or form.year_to.data:
        mindate = '*'
        maxdate = '*'
        if form.year_from.data:
            if form.month_from.data:
                mindate = '%s%s00' % (form.year_from.data.zfill(4), form.month_from.data.zfill(2))
            else:
                mindate = '%s%s00' % (form.year_from.data.zfill(4), '00')
        if form.year_to.data:
            if form.month_to.data:
                maxdate = '%s%s00' % (form.year_to.data.zfill(4), form.month_to.data.zfill(2))
            else:
                maxdate = '%s%s00' % (form.year_to.data.zfill(4), '00')
        search_components['filters'].append('date_filter:[%s TO %s]' % (mindate, maxdate)) #????????????
        #check with jay what happens if someone puts a year like 0956 vs 956
    #refereed
    if form.refereed.data:
        search_components['filters'].append('property:REFEREED') #????????????
    #articles only
    if form.article.data:
        search_components['filters'].append('-property:NONARTICLE') #????????????
    
    return search_components


@search_blueprint.route('/', methods=('GET', 'POST'))
def search():
    """
    returns the results of a search
    """
    #I add the default values if they have not been submitted by the form
    form_vals = get_defaults_if_missing(request.values, QueryForm)
    
    form = QueryForm(form_vals, csrf_enabled=False)
    if form.validate():
        resp = query(form.q.data)
        return render_template('search_results.html', resp=resp, form=form)

    
    return render_template('search.html', form=form)

@search_blueprint.route('/advanced/', methods=('GET', 'POST'))
def search_advanced():
    """
    """
    pass