from flask import Blueprint, request, g, render_template, flash
from flask.ext.solrquery import solr, signals as solr_signals #@UnresovledImport

#from flask.ext.login import current_user #@UnresolvedImport
from .forms import QueryForm
from adsabs.core.solr import QueryBuilderSearch
from adsabs.core.data_formatter import field_to_json
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
            resp = solr.query(**query_components)
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
    form = QueryForm.init_with_defaults(request.values)
    if form.validate():
        query_components = QueryBuilderSearch.build(form, request.values, facets_components=True)
        resp = solr.query(**query_components)
        return render_template('facets_sublevel.html', resp=resp, facet_field_interf_id=query_components['facet_field_interf_id'] )

#         if query_components.get('facet_fields') and query_components.get('facet_field_interf_id'):
#             resp = solr.facet_query(query_components['q'], 
#                             facet_fields=query_components['facet_fields'],
#                             filters=query_components['filters'],
#                             ui_filters=query_components['ui_filters'],
#                             ui_q=query_components['ui_q'],
#                             query_fields=query_components['query_fields']
#                             )
#             return render_template('facets_sublevel.html', resp=resp, facet_field_interf_id=query_components['facet_field_interf_id'] )
#         else:
#             return 'facet query parameters error'
    
    
@search_blueprint.route('/advanced/', methods=('GET', 'POST'))
def search_advanced():
    """
    """
    pass

@solr_signals.error_signal.connect
def log_solr_error(sender, **kwargs):
    if hasattr(g, 'user_cookie_id'):
        kwargs['user_cookie_id'] = g.user_cookie_id
        event = LogEvent.new(request.url, **kwargs)
        logging.getLogger('search').info(event)           
    
@solr_signals.search_signal.connect
def log_solr_search(sender, **kwargs):
    """
    extracts some data from the solr  for log/analytics purposes
    """
    if hasattr(g, 'user_cookie_id'):
        resp = kwargs.pop('response')
        log_data = {
            'q': resp.get_query(),
            'hits': resp.get_hits(),
            'count': resp.get_count(),
            'start': resp.get_start_count(),
            'qtime': resp.get_qtime(),
            'results': resp.get_doc_values('bibcode', 0, config.SEARCH_DEFAULT_ROWS),
            'error_msg': resp.get_error_message(),
            'http_status': resp.get_http_status(),
            'solr_url': resp.request.url,
            'user_cookie_id': g.user_cookie_id
        }
        log_data.update(kwargs)
        event = LogEvent.new(request.url, **log_data)
        logging.getLogger('search').info(event)           
