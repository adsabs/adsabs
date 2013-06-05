from flask import Blueprint, request, g, render_template, flash

#from flask.ext.login import current_user #@UnresolvedImport
from .forms import QueryForm, get_missing_defaults
from adsabs.core import solr
from adsabs.core.data_formatter import field_to_json
from adsabs.core.form_functs import is_submitted_cust
from misc_functions import build_basicquery_components
from config import config
from adsabs.core.logevent import LogEvent
import logging

#Definition of the blueprint
search_blueprint = Blueprint('search', __name__, template_folder="templates", 
                             static_folder="static", url_prefix='/search')

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

@search_blueprint.before_request
def register_formatting_funcs():
    g.formatter_funcs = {'field_to_json': field_to_json}

def init_search_form():
    """
    common search request form populating
    """
    #I add the default values if they have not been submitted by the form and I create the new form
    params = get_missing_defaults(request.values, QueryForm)
    form = QueryForm(params, csrf_enabled=False)
    return form
    
@search_blueprint.route('/', methods=('GET', 'POST'))
def search():
    """
    returns the results of a search
    """
    form = init_search_form()
    if is_submitted_cust(form):
        if form.validate():
            #I append to the g element a dictionary of functions I need in the template
            query_components = build_basicquery_components(form, request.values)
            resp = solr.query(query_components['q'], 
                         filters=query_components['filters'], 
                         sort=query_components['sort'], 
                         start=query_components['start'], 
                         sort_direction=query_components['sort_direction'],
                         rows=query_components['rows']
                         )
            if resp.is_error():
                flash(resp.get_error_message(), 'error')
            return render_template('search_results.html', resp=resp, form=form)
        else:
            for field_name, errors_list in form.errors.iteritems():
                flash('errors in the form validation: %s.' % '; '.join(errors_list), 'error')
    return render_template('search.html', form=form)

@search_blueprint.route('/facets', methods=('GET', 'POST'))
def facets():
    """
    returns facet sets for a search query
    """
    form = init_search_form()
    if form.validate():
        query_components = build_basicquery_components(form, request.values, facets_components=True)
        if query_components.get('facet_fields') and query_components.get('facet_field_interf_id'):
            resp = solr.facet_query(query_components['q'], 
                            facet_fields=query_components['facet_fields'],
                            filters=query_components['filters']
                            )
            return render_template('facets_sublevel.html', resp=resp, facet_field_interf_id=query_components['facet_field_interf_id'] )
        else:
            return 'facet query parameters error'
    
    
@search_blueprint.route('/advanced/', methods=('GET', 'POST'))
def search_advanced():
    """
    """
    pass

    
@solr.signals.search_signal.connect
def log_solr_search(sender, resp, **kwargs):
    """
    extracts some data from the response for log/analytics purposes
    """
    data = { 
        'user_cookie_id': g.user_cookie_id,
        'q': resp.get_query(),
        'hits': resp.get_hits(),
        'count': resp.get_count(),
        'start': resp.get_start_count(),
        'qtime': resp.get_qtime(),
        'results': resp.get_doc_values('bibcode', 0, config.SEARCH_DEFAULT_ROWS),
        'error_msg': resp.get_error_message()
        }
    data.update(kwargs)
    event = LogEvent.new(request.url, **data)
    logging.getLogger('search').info(event)       

@solr.signals.error_signal.connect
def log_solr_error(sender, **kwargs):
    data = { 'user_cookie_id': g.user_cookie_id }
    data.update(kwargs)
    event = LogEvent.new(request.url, **data)
    logging.getLogger('search').info(event)                               
        
    