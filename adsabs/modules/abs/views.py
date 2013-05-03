'''
Created on Sep 24, 2012

@author: jluker
'''
from flask import Blueprint, request, g, render_template, abort
from adsabs.core import solr
from adsabs.core import invenio
from adsabs.core.data_formatter import field_to_json
from adsabs.modules.search.misc_functions import build_singledoc_components
from config import config

import logging
from adsabs.core.logevent import LogEvent

abs_blueprint = Blueprint('abs', __name__, template_folder="templates", url_prefix='/abs')

def log_abstract_view(bibcode):
    event = LogEvent.new(bibcode=bibcode, user_cookie_id=g.user_cookie_id)
    logging.getLogger('abs').info(event)
    
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
    solrdoc = solr.get_document(bibcode)
    if not solrdoc:
        abort(404)
    inveniodoc = invenio.get_invenio_metadata(bibcode)
    #I append to the g element a dictionary of functions I need in the template
    g.formatter_funcs = {'field_to_json':field_to_json}
    
    # log the request
    log_abstract_view(bibcode)
    
    return render_template('abstract_tabs.html', solrdoc=solrdoc, inveniodoc=inveniodoc, curview='abstract')
    
@abs_blueprint.route('/<bibcode>/references', methods=['GET'])
def references(bibcode):
    #I get the document
    solrdoc = solr.get_document(bibcode)
    #if there are no references I return a 404
    if not solrdoc or not solrdoc.has_references():
        abort(404)
    #I get the additional metadata
    inveniodoc = invenio.get_invenio_metadata(bibcode)
    #I parse the get options 
    query_components = build_singledoc_components(request.values)
    #I get the list of references
    solr_reference_list = solrdoc.get_references(sort=query_components['sort'], start=query_components['start'], sort_direction=query_components['sort_direction'])
    #I append to the g element a dictionary of functions I need in the template
    g.formatter_funcs = {'field_to_json':field_to_json}
    return render_template('abstract_tabs.html', solrdoc=solrdoc, inveniodoc=inveniodoc, curview='references', reference_list=solr_reference_list)

@abs_blueprint.route('/<bibcode>/citations', methods=['GET'])
def citations(bibcode):
    #I get the document
    solrdoc = solr.get_document(bibcode)
    #if there are no citations I return a 404
    if not solrdoc or not solrdoc.has_citations():
        abort(404)
    #I get the additional metadata
    inveniodoc = invenio.get_invenio_metadata(bibcode)
    #I parse the get options 
    query_components = build_singledoc_components(request.values)
    #I get the list of citations
    solr_citation_list = solrdoc.get_citations(sort=query_components['sort'], start=query_components['start'], sort_direction=query_components['sort_direction'])
    #I append to the g element a dictionary of functions I need in the template
    g.formatter_funcs = {'field_to_json':field_to_json}
    return render_template('abstract_tabs.html', solrdoc=solrdoc, inveniodoc=inveniodoc, curview='citations', citation_list=solr_citation_list)

@abs_blueprint.route('/<bibcode>/toc', methods=['GET'])
def toc(bibcode):
    #I get the document
    solrdoc = solr.get_document(bibcode)
    #if there are no citations I return a 404
    if not solrdoc or not solrdoc.has_toc():
        abort(404)
    #I get the additional metadata
    inveniodoc = invenio.get_invenio_metadata(bibcode)
    #I parse the get options 
    query_components = build_singledoc_components(request.values)
    solr_toc_list = solrdoc.get_toc(sort=query_components['sort'], start=query_components['start'], sort_direction=query_components['sort_direction'])
    #I append to the g element a dictionary of functions I need in the template
    g.formatter_funcs = {'field_to_json':field_to_json}
    return render_template('abstract_tabs.html', solrdoc=solrdoc, inveniodoc=inveniodoc, curview='toc', toc_list=solr_toc_list)



