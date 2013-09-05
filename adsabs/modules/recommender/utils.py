'''
Created on Jul 16, 2013

@author: ehenneken
'''
import os
import sys
import re
from xmlrpclib import Server
from config import config
import urllib
import requests
from flask import current_app as app
from flask.ext.solrquery import solr #@UnresolvedImport
from .errors import SolrQueryError
from .errors import RecommderServerConnectionError

def get_bibcodes(cookie):
    lines = urllib.urlopen(config.RECOMMENDER_RECENTS_URL%cookie).read().strip().split('\n')
    bibrecs  = filter(lambda a: a.strip()[:9] == '<bibcode>',lines)
    bibcodes = map(lambda a: re.sub('</?bibcode>','',a).replace('&amp;','&'), bibrecs)
    return bibcodes

def get_meta_data(**args):
    """
    Get the meta data for a set of bibcodes
    """
    data_dict = {}
    # This information can be retrieved with one single Solr query
    # (just an 'OR' query of a list of bibcodes)
    bibcodes = args['bibcodes']
    list = " OR ".join(map(lambda a: "bibcode:%s"%a, bibcodes))
    q = '%s' % list
    try:
        # Get the information from Solr
        resp = solr.query(q, rows=config.BIBUTILS_MAX_HITS, fields=['bibcode,title,first_author'])
    except SolrQueryError, e:
        app.logger.error("Solr references query for %s blew up (%s)" % (q,e))
        raise
    # Gather meta data
    search_results = resp.search_response()
    for doc in search_results['results']['docs']:
        title = 'NA'
        if 'title' in doc: title = doc['title'][0]
        author = 'NA'
        if 'first_author' in doc: author = "%s,+"%doc['first_author'].split(',')[0]
        data_dict[doc['bibcode']] = {'title':title, 'author':author}
    return data_dict

def get_recommendations(**args):
    try:
        bibcode = args['bibcode']
    except:
        return {}
    try:
        server = Server(config.RECOMMENDER_SERVER)
    except RecommderServerConnectionError, err:
        sys.stderr.write('Unable to query recommender server! (%s)'%err)
 
    try:
        recommendations = server.recommend([bibcode])
    except:
        return {}
    # Get meta data for the recommendations
    meta_dict = get_meta_data(bibcodes=recommendations[1:])
    # Filter out any bibcodes for which no meta data was found
    recommendations = filter(lambda a: a in meta_dict, recommendations)

    return {'paper':bibcode,'recommendations':[{'bibcode':x,'title':meta_dict[x]['title'], 'author':meta_dict[x]['author']} for x in recommendations[1:]]}

def get_suggestions(**args):
    if args['cookie']:
        bibcodes = get_bibcodes(args['cookie'])
    elif args['bibcodes']:
        bibcodes = args['bibcodes']
    else:
        return []
    try:
        server = Server(config.RECOMMENDER_SERVER)
    except RecommderServerConnectionError, err:
        sys.stderr.write('Unable to query recommender server! (%s)'%err)

    try:
        recommendations = server.suggest(bibcodes)
    except:
        return []
    # Get meta data for the recommendations
    meta_dict = get_meta_data(bibcodes=recommendations)
    # Filter out any bibcodes for which no meta data was found
    recommendations = filter(lambda a: a in meta_dict, recommendations)

    return {'type':'recently viewed','recommendations':[{'bibcode':x,'title':meta_dict[x]['title'], 'author':meta_dict[x]['author']} for x in recommendations]}