'''
Created on Sep 24, 2012

@author: jluker
'''
from flask import Blueprint, request, g, render_template, abort

from adsabs.core.solr import get_document, QueryBuilderSimple, denormalize_solr_doc
from adsabs.core.data_formatter import field_to_json
from config import config

import logging
from signals import abstract_view_signal
from adsabs.core.logevent import LogEvent
from adsabs.extensions import statsd

from adsabs.modules.visualization.paper_thumbnails import get_thumbnails

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

@abs_blueprint.route('/', methods=['GET'])
@abs_blueprint.route('/<bibcode>/', methods=['GET'])
def abstract(bibcode=None):
    
    if bibcode is None:
        abort(404)
        
    solrdoc = get_document(bibcode)
    if not solrdoc:
        abort(404)
    denormdoc = denormalize_solr_doc(solrdoc)

    # get article graphics info
    graphics = get_thumbnails(bibcode)
    # log the request
    abstract_view_signal.send(abs_blueprint, bibcode=bibcode, list_type="abstract")
    statsd.incr("abs.abstract.viewed")
    
    return render_template('abstract_tabs.html', solrdoc=solrdoc, denormdoc=denormdoc, graphics=graphics, curview='abstract')
    
@abs_blueprint.route('/<bibcode>/<list_type>/', methods=['GET'])
def tab_list(bibcode, list_type):

    solrdoc = get_document(bibcode)

    denormdoc = denormalize_solr_doc(solrdoc)
    graphics = {}
    if list_type != 'graphics':
        #if there are no references return a 404
        if not solrdoc or not solrdoc.has_assoc_list(list_type):
            abort(404)
        #parse the get options 
        query_components = QueryBuilderSimple.build(request.values, list_type=list_type)

        # use the appropriate getter method
        list_method = getattr(solrdoc, "get_%s" % list_type)
        if not list_method:
            abort(404)

        #get the list of associated docs
        resp = list_method(**query_components)
    else:
        resp = {}
        # get article graphics info
        graphics = get_thumbnails(bibcode)
    # log the request
    abstract_view_signal.send(abs_blueprint, bibcode=bibcode, list_type=list_type)
    statsd.incr("abs.%s.viewed" % list_type)
    
    return render_template('abstract_tabs.html', solrdoc=solrdoc, denormdoc=denormdoc, curview=list_type, article_list=resp, graphics=graphics)

@abstract_view_signal.connect
def log_abstract_view(sender, **kwargs):
    kwargs['user_cookie_id'] = g.user_cookie_id
    event = LogEvent.new(request.url, **kwargs)
    logging.getLogger('abs').info(event)
