from flask import Blueprint, request, g, render_template

from flask.ext.login import current_user #@UnresolvedImport
from .forms import QueryForm, get_defaults_if_missing
from adsabs.core.solr import query

#I define the blueprint
search_blueprint = Blueprint('search', __name__, template_folder="templates", static_folder="static")

__all__ = ['search_blueprint','search', 'search_advanced']

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