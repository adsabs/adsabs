from flask import Blueprint, request, g, render_template

from flask.ext.login import current_user #@UnresolvedImport
from .forms import QueryForm, get_missing_defaults
from adsabs.core.solr import query
from misc_functions import build_basicquery_components

#I define the blueprint
search_blueprint = Blueprint('search', __name__, template_folder="templates", static_folder="static")

__all__ = ['search_blueprint','search', 'search_advanced']


@search_blueprint.route('/', methods=('GET', 'POST'))
def search():
    """
    returns the results of a search
    """
    #I add the default values if they have not been submitted by the form and I create the new form
    form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
    if form.validate():
        query_components = build_basicquery_components(form, request.values)
        resp = query(query_components['q'], filters=query_components['filters'], sort=query_components['sort'], start=query_components['start'], sort_direction=query_components['sort_direction'])
        return render_template('search_results.html', resp=resp, form=form)

    
    return render_template('search.html', form=form)

@search_blueprint.route('/advanced/', methods=('GET', 'POST'))
def search_advanced():
    """
    """
    pass