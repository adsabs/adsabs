from flask import Blueprint, request, g, render_template
from .forms import QueryForm
from adsabs.core.data import solr

#I define the blueprint
search_blueprint = Blueprint('search', __name__, template_folder="templates", static_folder="static")

__all__ = ['search_blueprint','search', 'search_advanced']

@search_blueprint.route('/', methods=('GET', 'POST'))
def search():
    """
    returns the results of a search
    """
    form = QueryForm(request.values, csrf_enabled=False)
    if form.validate():
        resp = solr.query(form.q.data)
        return render_template('search_results.html', resp=resp, form=form)
    
    return render_template('search.html', form=form)

@search_blueprint.route('/advanced/', methods=('GET', 'POST'))
def search_advanced():
    """
    """
    pass