from flask import Blueprint, request, g, render_template

from flask.ext.login import current_user #@UnresolvedImport
from .forms import QueryForm, get_missing_defaults
from adsabs.core.solr import query
from adsabs.core.data_formatter import field_to_json
from misc_functions import build_basicquery_components
from config import config

#I define the blueprint
search_blueprint = Blueprint('search', __name__, template_folder="templates", static_folder="static")

__all__ = ['search_blueprint','search', 'search_advanced']

@search_blueprint.after_request
def add_caching_header(response):
    """
    Adds caching headers
    """
    if not config.DEBUG:
        cache_header = 'max-age=3600, must-revalidate'
    else:
        cache_header = 'no-cache'
    response.headers.setdefault('Cache-Control', cache_header)    
    return response

@search_blueprint.route('/', methods=('GET', 'POST'))
def search():
    """
    returns the results of a search
    """
    #I add the default values if they have not been submitted by the form and I create the new form
    form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
    if form.validate():
        #I append to the g element a dictionary of functions I need in the template
        g.formatter_funcs = {'field_to_json':field_to_json}
        query_components = build_basicquery_components(form, request.values)
        resp = query(query_components['q'], filters=query_components['filters'], sort=query_components['sort'], start=query_components['start'], sort_direction=query_components['sort_direction'])
        return render_template('search_results.html', resp=resp, form=form)

    
    return render_template('search.html', form=form)

@search_blueprint.route('/advanced/', methods=('GET', 'POST'))
def search_advanced():
    """
    """
    pass