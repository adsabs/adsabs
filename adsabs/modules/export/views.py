'''
Created on Sep 5, 2013

@author: dimilia
'''
import simplejson as json
from simplejson import JSONDecodeError
from flask import (Blueprint, request, Response, current_app as app, abort, render_template)
from adsabs.core.classic.export import get_classic_records_export
from adsabs.core.solr import get_document_similar
from flask.ext.solrquery import solr, signals as solr_signals #@UnresovledImport
from config import config


export_blueprint = Blueprint('export', __name__, template_folder="templates", url_prefix='/export')

@export_blueprint.route('/', methods=['GET', 'POST'])
def export_to_other_formats():
    """
    view that exports a set of papers
    the imput is a format and 
    a list of bibcodes or a variable containing the parameters for a solr query
    """
    #extract the format
    export_format = request.values.getlist('export_format')
    list_type = request.values.get('list_type')

    #list of bibcodes to extract
    bibcodes_to_export = []
    #flag to check if everything has been extracted
    all_extracted = True
    num_hits = None
    
    #if there are not bibcodes, there should be first a query to extract them  
    if not request.values.has_key('bibcode'):
        #@todo: code to query solr with the same query parameters but override the fields to retrieve
        try:
            query_components = json.loads(request.values.get('current_search_parameters'))
        except (TypeError, JSONDecodeError):
            #@todo: logging of the error
            return render_template('errors/generic_error.html', error_message='Error while exporting records (code #1). Please try later.')
        
        #update the query parameters to return only what is necessary
        query_components.update({'facets':[], 'fields': ['bibcode'], 'highlights':[], 'rows': str(config.EXPORT_DEFAULT_ROWS)})
        #execute the query
        if list_type == 'similar':
            resp = get_document_similar(**query_components)
        else:
            resp = solr.query(**query_components)
        if resp.is_error():
            return render_template('errors/generic_error.html', error_message='Error while exporting records (code #2). Please try later.')
        #extract the bibcodes
        for doc in resp.get_docset_objects():
            bibcodes_to_export.append(doc.bibcode)
        #check if all the results of the query have been extracted ( num results <= max to extract )
        if resp.get_hits() > config.EXPORT_DEFAULT_ROWS:
            all_extracted = False
            num_hits = resp.get_hits()

    else:
        #extract all the bibcodes
        bibcodes_to_export = request.values.getlist('bibcode')
        
    #actually export the records
    if bibcodes_to_export:
        export_str = get_classic_records_export(bibcodes_to_export, export_format)
    else:
        export_str = ''
    
    #if not everything has been extracted, show message on top  
    if not all_extracted:
        export_str = 'Exported first %s results of %s total. \n\n\n%s' % (config.EXPORT_DEFAULT_ROWS, num_hits, export_str)
    else:
        export_str = 'Exported %s records \n\n\n%s' % (len(bibcodes_to_export), export_str)
    
    return Response(export_str, mimetype='text/plain')



@export_blueprint.route('/get_bibcodes_from_query', methods=['GET', 'POST'])
def get_bibcodes_from_query():
    """
    view that retrieves the only bibcodes for a list of paper
    """
    #list of bibcodes to extract
    bibcodes_to_export = []
    list_type = request.values.get('list_type')
    
    try:
        query_components = json.loads(request.values.get('current_search_parameters'))
    except (TypeError, JSONDecodeError), e:
        #@todo: logging of the error
        return ''
    #update the query parameters to return only what is necessary
    query_components.update({'facets':[], 'fields': ['bibcode'], 'highlights':[], 'rows': str(config.EXPORT_DEFAULT_ROWS)})
    #execute the query
    
    if list_type == 'similar':
        resp = get_document_similar(**query_components)
    else:
        resp = solr.query(**query_components)
    if resp.is_error():
        #@todo: logging of the error
        return ''
    #extract the bibcodes
    for doc in resp.get_docset_objects():
        bibcodes_to_export.append(doc.bibcode)
    return ';'.join(bibcodes_to_export)
