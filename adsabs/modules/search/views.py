import sys
from flask import Blueprint, request, g, render_template, flash, current_app, abort
from flask.ext.solrquery import solr #@UnresolvedImport

#from flask.ext.login import current_user #@UnresolvedImport
from .forms import QueryForm
from adsabs.core.solr import QueryBuilderSearch, AdsabsSolrqueryException
from adsabs.core.data_formatter import field_to_json
from config import config
from adsabs.core.logevent import log_event
import traceback

#Definition of the blueprint
search_blueprint = Blueprint('search', __name__, template_folder="templates", 
                             static_folder="static", url_prefix='/search')

__all__ = ['search_blueprint','search', 'search_advanced']

@search_blueprint.errorhandler(AdsabsSolrqueryException)
def solrquery_exception(error):
    msg = "Search service error: %s" % error
    user_cookie_id = hasattr(g, 'user_cookie_id') and g.user_cookie_id or None
    exc_info = error.exc_info
    exc_str = traceback.format_exception(*exc_info)
    current_app.logger.error("%s: (%s, %s) %s" % (msg, exc_info[0], exc_info[1], exc_info[2]))
    log_event('search', msg=msg, user_cookie_id=user_cookie_id, exception=exc_str)
    flash(msg, 'error')
    abort(500)

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

@search_blueprint.before_request
def register_formatting_funcs():
    g.formatter_funcs = {'field_to_json': field_to_json}

@search_blueprint.route('/', methods=('GET', 'POST'))
def search():
    """
    returns the results of a search
    """
    if not len(request.values):
        form = QueryForm(csrf_enabled=False)
        # prefill the database select menu option
        form.db_f.default = config.SEARCH_DEFAULT_DATABASE
    else:
        form = QueryForm.init_with_defaults(request.values)
        if form.validate():
            query_components = QueryBuilderSearch.build(form, request.values)
            try:
                resp = solr.query(**query_components)
            except Exception, e:
                raise AdsabsSolrqueryException("Error communicating with search service", sys.exc_info())
            if resp.is_error():
                flash(resp.get_error_message(), 'error')
            return render_template('search_results.html', resp=resp, form=form, query_components=query_components)
        else:
            for field_name, errors_list in form.errors.iteritems():
                flash('errors in the form validation: %s.' % '; '.join(errors_list), 'error')
    return render_template('search.html', form=form)

@search_blueprint.route('/facets', methods=('GET', 'POST'))
def facets():
    """
    returns facet sets for a search query
    """
    form = QueryForm.init_with_defaults(request.values)
    if form.validate():
        query_components = QueryBuilderSearch.build(form, request.values, facets_components=True)
        try:
            resp = solr.query(**query_components)
        except Exception, e:
            raise AdsabsSolrqueryException("Error communicating with search service", sys.exc_info())
        return render_template('facets_sublevel.html', resp=resp, facet_field_interf_id=query_components['facet_field_interf_id'] )

@search_blueprint.route('/advanced/', methods=('GET', 'POST'))
def search_advanced():
    """
    """
    pass

