import sys
import re
from flask import Blueprint, request, g, render_template, flash, current_app, abort, url_for,\
    Markup, redirect
from flask.ext.solrquery import solr #@UnresolvedImport
import re

#from flask.ext.login import current_user #@UnresolvedImport
from .forms import QueryForm
from adsabs.core.solr import QueryBuilderSearch, AdsabsSolrqueryException
from adsabs.core.solr.bigquery import prepare_bigquery_request, retrieve_bigquery, save_bigquery
from adsabs.core.data_formatter import field_to_json
from config import config
from adsabs.core.logevent import log_event
import traceback
import uuid
import pytz
from datetime import datetime

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
            bigquery_id = request.values.get('bigquery')
            try:
                
                req = solr.create_request(**query_components)

                if bigquery_id:
                    prepare_bigquery_request(req, request.values['bigquery'])
                    
                req = solr.set_defaults(req)
                resp = solr.get_response(req)
                
                if bigquery_id:
                    facets = resp.get_facet_parameters()
                    facets.append(('bigquery', bigquery_id))
                
            except Exception, e:
                raise AdsabsSolrqueryException("Error communicating with search service", sys.exc_info())
            if resp.is_error():
                flash(resp.get_error_message(), 'error')

            return render_template('search_results.html', resp=resp, form=form, 
                                   query_components=query_components, bigquery_id=bigquery_id)
        else:
            for field_name, errors_list in form.errors.iteritems():
                flash('errors in the form validation: %s.' % '; '.join(errors_list), 'error')
    return render_template('search.html', form=form)




@search_blueprint.route('/bigquery/', methods=('GET', 'POST'))
def bigquery():
    """
    Allows one to post a large number of ID's and get
    results in the search form
    """
    form = QueryForm(csrf_enabled=False)
    # prefill the database select menu option
    form.db_f.default = config.SEARCH_DEFAULT_DATABASE
    form.method = 'POST'
    form.flask_route = 'search.bigquery'
        
    # just for debugging, return what we know about the query
    if ('uuid' in request.values):
        data = retrieve_bigquery(request.values['uuid'])
        form.add_rendered_element(Markup(render_template('bigquery.html', data=data)))
        return render_template('search.html', form=form)
    
    # receive the data from the form
    v = request.values.get('bigquerydata')
    if (v is None or len(v) == 0):
        form.add_rendered_element(Markup(render_template('bigquery.html', data="")))
        return render_template('search.html', form=form)
    
    # reformat query value to handle the following separators between identifiers:
    #     '\s+', ', ', '; '
    # and make sure the data has proper header
    v = re.sub(r'\s+', r'\n', v.strip().replace(',',' ').replace(';',' '))
    if v[0:7] != 'bibcode':
        v = 'bibcode\n' + v
    
    qid = save_bigquery(v)
    
    flash("Please note that we do not guarantee the persistance of your query in our system (it will be deleted at some point)", "info")
    urlargs = dict(request.args)
    urlargs['bigquery'] = qid
    if 'q' not in urlargs:
        urlargs['q'] = '*:*'
    full_url = url_for('search.search', **urlargs)
    return redirect(full_url)

    # return the unique queryid
    #return qid

@search_blueprint.route('/pub-vol-page/', methods=('GET', 'POST'))
def pub_vol_page():
    """
    returns classic_search page
    """

    return render_template('pub-vol-page.html')
    
    
@search_blueprint.route('/classic-search/', methods=('GET', 'POST'))
def classic_search():
    """
    returns classic_search page
    """

    return render_template('classic-search.html')


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
