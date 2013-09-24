'''
Created on Sep 10, 2013

@author: dimilia
'''
import simplejson as json
from simplejson import JSONDecodeError
from flask import (Blueprint, request, url_for, Response, current_app as app, abort, render_template, jsonify)
from flask.ext.solrquery import solr, signals as solr_signals #@UnresovledImport
from config import config
from authorsnetwork import get_authorsnetwork
#from alladinlite import get_objects

visualization_blueprint = Blueprint('visualization', __name__, template_folder="templates", url_prefix='/visualization')


@visualization_blueprint.route('/author_network', methods=['GET', 'POST'])
def author_network():
    """
    View that creates the data for the author network
    """
    #list of bibcodes to extract
    lists_of_authors = []
        
    #if there are not bibcodes, there should be a query to extract the authors
    if not request.values.has_key('bibcode'):
        try:
            query_components = json.loads(request.values.get('current_search_parameters'))
        except (TypeError, JSONDecodeError):
            #@todo: logging of the error
            return render_template('errors/generic_error.html', error_message='Error while creating the author network (code #1). Please try later.')
        #update the query parameters to return only what is necessary
        query_components.update({'facets':[], 'fields': ['author_norm'], 'highlights':[], 'rows': str(config.AUTHOR_NETWORK_DEFAULT_FIRST_RESULTS)})
    #otherwise query to extract the authors from the bibcodes
    else:
        bibcodes = request.values.getlist('bibcode')
        q = 'bibcode:%s' % bibcodes.pop()
        for bibcode in bibcodes:
            q = '%s OR bibcode:%s' % (q, bibcode)
        query_components = {'q':q, 'fields': ['author_norm'], 'rows': str(config.AUTHOR_NETWORK_DEFAULT_FIRST_RESULTS),'facets':[], 'highlights':[], }
        
    resp = solr.query(**query_components)
    if resp.is_error():
        return render_template('errors/generic_error.html', error_message='Error while creating the author network (code #2). Please try later.')
    #extract the authors
    for doc in resp.get_docset_objects():
        #check if there is actually a list of authors
        if doc.author_norm:
            lists_of_authors.append(doc.author_norm)
        
    return render_template('author_network_embedded.html', network_data=get_authorsnetwork(lists_of_authors))

@visualization_blueprint.route('/alladin_lite', methods=['GET', 'POST'])
def alladin_lite():
    """
    View that creates the data for alladin lite
    """
    #list of bibcodes to extract
    lists_of_authors = []
        
    #if there are not bibcodes, there should be a query to extract the authors
    if not request.values.has_key('bibcode'):
        bibcodes=[]
        try:
            query_components = json.loads(request.values.get('current_search_parameters'))
        except (TypeError, JSONDecodeError):
            #@todo: logging of the error
            return render_template('errors/generic_error.html', error_message='Error. Please try later.')
        #update the query parameters to return only what is necessary
        query_components.update({'facets':[], 'fields': ['bibcode'], 'highlights':[], 'rows': str(config.AUTHOR_NETWORK_DEFAULT_FIRST_RESULTS)})
        resp = solr.query(**query_components)
        if resp.is_error():
            return render_template('errors/generic_error.html', error_message='Error while creating the author network (code #2). Please try later.')
        for doc in resp.get_docset_objects():
            print "DOC IS", doc.data, doc.to_json()
            bibcodes.append(doc.bibcode)
    else:
        bibcodes = request.values.getlist('bibcode')

        
    
        
    return render_template('alladin_lite_embedded.html', bibcodes={'bibcodes':bibcodes})