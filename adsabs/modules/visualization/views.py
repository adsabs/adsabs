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
from solrjsontowordcloudjson import wc_json
#from alladinlite import get_objects

visualization_blueprint = Blueprint('visualization', __name__, template_folder="templates", url_prefix='/visualization')


@visualization_blueprint.route('/author_network', methods=['GET', 'POST'])
def author_network():
    """
    View that creates the data for the author network
    """
        
    #if there are not bibcodes, there should be a query to extract the authors
    try:
        query_components = json.loads(request.values.get('current_search_parameters'))
    except (TypeError, JSONDecodeError):
        #@todo: logging of the error
        return render_template('errors/generic_error.html', error_message='Error while creating the author network (code #1). Please try later.')

    # get the maximum number of records to use
    query_components['rows'] = request.values.get('numRecs', config.MAX_EXPORTS['authnetwork'])

    # checked bibcodes will be input as
    if request.values.has_key('bibcode'):
        bibcodes = request.values.getlist('bibcode')
        query_components['q'] = ' OR '.join(["bibcode:%s" % b for b in bibcodes])

    #update the query parameters to return only what is necessary
    query_components.update({
        'facets': [], 
        'fields': ['author_norm'], 
        'highlights': [], 
        })

    resp = solr.query(**query_components)

    if resp.is_error():
        return render_template('errors/generic_error.html', error_message='Error while creating the author network (code #2). Please try later.')

    #extract the authors
    lists_of_authors = [doc.author_norm for doc in resp.get_docset_objects() if doc.author_norm]
        
    return render_template('author_network_embedded.html', network_data=get_authorsnetwork(lists_of_authors))


@visualization_blueprint.route('/word_cloud', methods=['GET', 'POST'])
def word_cloud():
    """
    View that creates the data for the word cloud
    """

    query_url = config.SOLRQUERY_URL
    tvrh_query_url = query_url.rsplit('/', 1)[0] + '/tvrh'

    try:
        query_components = json.loads(request.values.get('current_search_parameters'))
    except (TypeError, JSONDecodeError):
        #@todo: logging of the error
        return render_template('errors/generic_error.html', error_message='Error while creating the word cloud (code #1). Please try later.')

    # get the maximum number of records to use
    query_components['rows'] = request.values.get('numRecs', config.MAX_EXPORTS['wordcloud'])

    # checked bibcodes will be input as
    if request.values.has_key('bibcode'):
        bibcodes = request.values.getlist('bibcode')
        query_components['q'] = ' OR '.join(["bibcode:%s" % b for b in bibcodes])

    query_components.update({
        'facets': [],
        'fields': ['id'],
        'highlights': [],
        'defType':'aqp', 
        'tv.tf_idf': 'true', 
        'tv.tf': 'true', 
        'tv.positions':'false',
        'tf.offsets':'false',
        'tv.fl':'abstract,title',
        'fl':'abstract,title' 
    })
            
    resp = solr.query(query_url=tvrh_query_url, **query_components)

    if resp.is_error():
        return render_template('errors/generic_error.html', error_message='Error while creating the word cloud (code #2). Please try later.')
    
    return render_template('word_cloud_embedded.html', wordcloud_data=wc_json(resp.raw_response()))

@visualization_blueprint.route('/alladin_lite', methods=['GET', 'POST'])
def alladin_lite():
    """
    View that creates the data for alladin lite
    """
    #if there are not bibcodes, there should be a query to extract the authors
    if request.values.has_key('bibcode'):
        bibcodes = request.values.getlist('bibcode')
    else:
        try:
            query_components = json.loads(request.values.get('current_search_parameters'))
        except (TypeError, JSONDecodeError):
            #@todo: logging of the error
            return render_template('errors/generic_error.html', error_message='Error. Please try later.')

        # get the maximum number of records to use
        query_components['rows'] = request.values.get('numRecs', config.MAX_EXPORTS['skymap'])

        #update the query parameters to return only what is necessary
        query_components.update({
            'facets': [],
            'fields': ['bibcode'],
            'highlights': [],
            })

        resp = solr.query(**query_components)

        if resp.is_error():
            return render_template('errors/generic_error.html', error_message='Error while creating the objects skymap. Please try later.')

        bibcodes = [x.bibcode for x in resp.get_docset_objects()]

    return render_template('alladin_lite_embedded.html', bibcodes={'bibcodes':bibcodes})
