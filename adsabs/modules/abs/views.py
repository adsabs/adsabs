'''
Created on Sep 24, 2012

@author: jluker
'''
from flask import Blueprint, request, g, render_template, abort

from adsabs.core.solr import get_document, QueryBuilderSimple
from adsabs.core import invenio
from adsabs.core.data_formatter import field_to_json
from config import config

import logging
from signals import abstract_view_signal
from adsabs.core.logevent import LogEvent

abs_blueprint = Blueprint('abs', __name__, template_folder="templates", url_prefix='/abs')

@abs_blueprint.before_request
def formatter_funcs():
    """
    append to the g element a formatter needed in the templates
    """
    g.formatter_funcs = {'field_to_json':field_to_json}
    
@abs_blueprint.after_request
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

@abs_blueprint.route('/<bibcode>', methods=['GET'])
def abstract(bibcode):
    
    solrdoc = get_document(bibcode)
    if not solrdoc:
        abort(404)
    inveniodoc = invenio.get_invenio_metadata(bibcode)
    
    # log the request
    abstract_view_signal.send(abs_blueprint, bibcode=bibcode, type="abstract")
    
    return render_template('abstract_tabs.html', solrdoc=solrdoc, inveniodoc=inveniodoc, curview='abstract')
    
@abs_blueprint.route('/<bibcode>/<list_type>', methods=['GET'])
def tab_list(bibcode, list_type):

    #I get the document
    solrdoc = get_document(bibcode)

    #if there are no references I return a 404
    if not solrdoc or not solrdoc.has_assoc_list(list_type):
        abort(404)

    #I get the additional metadata
    inveniodoc = invenio.get_invenio_metadata(bibcode)

    #I parse the get options 
    query_components = QueryBuilderSimple.build(request.values)

    # use the appropriate getter method
    list_method = getattr(solrdoc, "get_%s" % list_type)
    if not list_method:
        abort(404)

    #I get the list of associated docs
    resp = list_method(**query_components)
    
    # log the request
    abstract_view_signal.send(abs_blueprint, bibcode=bibcode, type=list_type)
    
    return render_template('abstract_tabs.html', solrdoc=solrdoc, inveniodoc=inveniodoc, curview=list_type, article_list=resp)

@abstract_view_signal.connect
def log_abstract_view(sender, **kwargs):
    kwargs['user_cookie_id'] = g.user_cookie_id
    event = LogEvent.new(request.url, **kwargs)
    logging.getLogger('abs').info(event)