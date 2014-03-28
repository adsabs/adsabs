'''
Created on Mar 27, 2014

@author: ehenneken
'''
import os
import re
import sys
import time
from datetime import datetime
import random as rndm
from itertools import groupby
from config import config
import urllib
import requests
from numpy import *
import operator
import cPickle
import pymongo
from flask import current_app as app
from flask.ext.solrquery import solr #@UnresolvedImport
from .errors import *
from .recommender_defs import ASTkeywords
from adsabs.modules.bibutils.utils import get_citing_papers

__all__ = ['get_recommendations','get_suggestions']
# Helper functions
def flatten(items):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8, 9, 10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for item in items:
        if hasattr(item, '__iter__'):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

def multikeysort(items, columns):
    '''
    Given a list L of dictionaries with elements of the form 
    
       {'key1':value1, 'key2':value2, 'key3':value3, 'key4':value4}
    
    we want to be able to e.g. do
    
       multikeysort(L, ['-key1', 'key2', '-key3'])
       
    where the list is sorted based on the given keys, where the prepended
    '-' sign means 'descending'
    
    '''
    comparers = [ ((operator.itemgetter(col[1:].strip()), -1) if col.startswith('-') else (operator.itemgetter(col.strip()), 1)) for col in columns]

    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)

def get_before_after(item,list):
    '''
    For a given list, given an item, give the items
    directly before and after that given item
    '''
    idx = list.index(item)
    try:
        before = list[idx-1]
    except:
        before = "NA"
    try:
        after = list[idx+1]
    except:
        after = "NA"
    return [before,after]

def get_frequencies(l):
    '''
    For a list of items, return a list of tuples, consisting of
    unique items, augemented with their frequency in the original list
    '''
    tmp = [(k,len(list(g))) for k, g in groupby(sorted(l))]
    return sorted(tmp, key=operator.itemgetter(1),reverse=True)[:100]

def make_date(datestring):
    '''
    Turn an ADS publication data into an actual date
    '''
    pubdate = map(lambda a: int(a), datestring.split('-'))
    if pubdate[1] == 0:
        pubdate[1] = 1
    return datetime(pubdate[0],pubdate[1],1)

def get_normalized_keywords(bibc):
    '''
    For a given publication, construct a list of normalized keywords of this
    publication and its references
    '''
    keywords = []
    q = 'bibcode:%s or references(bibcode:%s)' % (bibc,bibc)
    try:
        # Get the information from Solr
        resp = solr.query(q, rows=config.BIBUTILS_MAX_HITS, fields=['keyword_norm'])
    except SolrQueryError, e:
        app.logger.error("Solr keywords query for %s blew up (%s)" % (bibc,e))
        raise
    search_results = resp.search_response()
    for doc in search_results['results']['docs']:
        try:
            keywords += map(lambda a: a.lower(), doc['keyword_norm'])
        except:
            pass
    return filter(lambda a: a in ASTkeywords, keywords)

def get_article_data(biblist, check_references=True):
    '''
    Get basic article metadata for a list of bibcodes
    '''
    list = " OR ".join(map(lambda a: "bibcode:%s"%a, biblist))
    q = '%s' % list
    fl= ['bibcode','title','first_author','keyword_norm','reference','citation_count','pubdate']
    try:
        # Get the information from Solr
        resp = solr.query(q, sort=[["pubdate", "desc"], ["bibcode", "desc"]], rows=config.BIBUTILS_MAX_HITS, fields=fl)
    except SolrQueryError, e:
        app.logger.error("Solr article data query for %s blew up (%s)" % (str(biblist),e))
        raise
    search_results = resp.search_response()
    results = search_results['results']['docs']
    if check_references:
        results = filter(lambda a: 'reference' in a, results)
        return results
    else:
        data_dict = {}
        for doc in results:
            title = 'NA'
            if 'title' in doc: title = doc['title'][0]
            author = 'NA'
            if 'first_author' in doc: author = "%s,+"%doc['first_author'].split(',')[0]
            data_dict[doc['bibcode']] = {'title':title, 'author':author}
        return data_dict

def get_recently_viewed(cookie):
    '''
    Given a cookie ID, retrieve the most recently viewed records
    '''
    bibcodes = []
    if len(cookie) != 10:
        return bibcodes
    cookie = cookie.strip()
    lines = urllib.urlopen(config.RECOMMENDER_RECENTS_URL%cookie).read().strip().split('\n')
    bibrecs  = filter(lambda a: a.strip()[:9] == '<bibcode>',lines)
    bibcodes = map(lambda a: re.sub('</?bibcode>','',a).replace('&amp;','&'), bibrecs)
    return bibcodes
#   
# Helper Functions: Data Processing
def make_paper_vector(bibc):
    '''
    Given a bibcode, retrieve the list of normalized keywords for this publication AND
    its references. Then contruct a vector of normalized frequencies. This is an ordered
    vector, i.e. the first entry is for the first normalized keyword etc etc etc
    '''
    data = get_normalized_keywords(bibc)
    if len(data) == 0:
        return []
    freq = dict((ASTkeywords.index(x), float(data.count(x))/float(len(data))) for x in data)
    FreqVec = [0.0]*len(ASTkeywords)
    for i in freq.keys():
        FreqVec[i] = freq[i]
    return FreqVec

def project_paper(pvector,pcluster=None):
    '''
    If no cluster is specified, this routine projects a paper vector (with normalized frequencies
    for ALL normalized keywords) onto the reduced 100-dimensional space. When a cluster is specified
    the this is a cluster-specific projection to further reduce the dimensionality to 5 dimensions
    '''
    if not pcluster:
        pcluster = -1
    client = pymongo.MongoClient(config.RECOMMENDER_MONGO_HOST,config.RECOMMENDER_MONGO_PORT)
    db = client.recommender
    db.authenticate(config.RECOMMENDER_MONGO_USER,config.RECOMMENDER_MONGO_PASSWORD)
    collection = db.matrices
    res = collection.find_one({'cluster':int(pcluster)})
    projection = cPickle.loads(res['projection_matrix'])
    PaperVector = array(pvector)
    try:
        coords = dot(PaperVector,projection)
    except:
        coords = []
    return coords

def find_paper_cluster(pvec,bibc):
    '''
    Given a paper vector of normalized keyword frequencies, reduced to 100 dimensions, find out
    to which cluster this paper belongs
    '''
    client = pymongo.MongoClient(config.RECOMMENDER_MONGO_HOST,config.RECOMMENDER_MONGO_PORT)
    db = client.recommender
    db.authenticate(config.RECOMMENDER_MONGO_USER,config.RECOMMENDER_MONGO_PASSWORD)
    collection = db.clusters
    res = collection.find_one({'members':bibc})
    if res:
        return res['cluster']

    min_dist = 9999
    clusters = collection.find()
    for entry in clusters:
        centroid = cPickle.loads(entry['centroid'])
        dist = linalg.norm(pvec-array(centroid))
        if dist < min_dist:
            cluster = entry['cluster']
        min_dist = min(dist, min_dist)
    return str(cluster)

def find_cluster_papers(pcluster):
    '''
    Given a cluster ID, retrieve the papers belonging to this cluster
    '''
    result = []
    client = pymongo.MongoClient(config.RECOMMENDER_MONGO_HOST,config.RECOMMENDER_MONGO_PORT)
    db = client.recommender
    db.authenticate(config.RECOMMENDER_MONGO_USER,config.RECOMMENDER_MONGO_PASSWORD)
    cluster_coll = db.recent_paper_clustering
    entries = cluster_coll.find({'cluster':int(pcluster)})
    for entry in entries:
        result.append(entry)
    return result

def find_closest_cluster_papers(pcluster,vec):
    '''
    Given a cluster and a paper (represented by its vector), which are the
    papers in the cluster closest to this paper?
    '''
    client = pymongo.MongoClient(config.RECOMMENDER_MONGO_HOST,config.RECOMMENDER_MONGO_PORT)
    db = client.recommender
    db.authenticate(config.RECOMMENDER_MONGO_USER,config.RECOMMENDER_MONGO_PASSWORD)
    cluster_coll = db.clusters
    paper_coll = client.recommender.clustering
    res = cluster_coll.find_one({'cluster':int(pcluster)})
    distances = []
    for paper in res['members']:
        res = paper_coll.find_one({'paper':paper})
        if res:
            cvector = cPickle.loads(res['vector_low'])
        else:
            continue
        dist = linalg.norm(vec-cvector)
        distances.append((paper,dist))
    d = sorted(distances, key=operator.itemgetter(1),reverse=False)
    return map(lambda a: a[0],d[:config.RECOMMENDER_MAX_NEIGHBORS])

def find_recommendations(G,remove=None):
    '''Given a set of papers (which is the set of closest papers within a given
    cluster to the paper for which recommendations are required), find recommendations.'''
    client = pymongo.MongoClient(config.RECOMMENDER_MONGO_HOST,config.RECOMMENDER_MONGO_PORT)
    db = client.recommender
    db.authenticate(config.RECOMMENDER_MONGO_USER,config.RECOMMENDER_MONGO_PASSWORD)
    reads_coll = db.reads
    # get all reads series by frequent readers who read
    # any of the closest papers (stored in G)
    res = reads_coll.find({'reads':{'$in':G}})
    # lists to record papers read just before and after a paper
    # was read from those closest papers, and those to calculate
    # associated frequency distributions
    before = []
    BeforeFreq = []
    after  = []
    AfterFreq = []
    # list to record papers read by people who read one of the
    # closest papers
    alsoreads = []
    AlsoFreq = []
    # start processing those reads we determined earlier
    for item in res:
        alsoreads += item['reads']
        overlap = list(set(item['reads']) & set(G))
        before_after_reads = map(lambda a: get_before_after(a, item['reads']), overlap)
        for reads_pair in before_after_reads:
            before.append(reads_pair[0])
            after.append(reads_pair[1])
    # remove all "NA"
    before = filter(lambda a: a != "NA", before)
    after  = filter(lambda a: a != "NA", after)
    # remove (if specified) the paper for which we get recommendations
    if remove:
        alsoreads = filter(lambda a: a != remove, alsoreads)
    # calculate frequency distributions
    BeforeFreq = get_frequencies(before)
    AfterFreq  = get_frequencies(after)
    AlsoFreq  = get_frequencies(alsoreads)
    # get publication data for the top 100 most alsoread papers
    top100 = map(lambda a: a[0], AlsoFreq)
    top100_data = get_article_data(top100)
    # For publications with no citations, Solr docs don't have a citation count
    tmpdata = []
    for item in top100_data:
        if 'citation_count' not in item:
            item.update({'citation_count':0})
        tmpdata.append(item)
    top100_data = tmpdata
    mostRecent = top100_data[0]['bibcode']
    top100_data = sorted(top100_data, key=operator.itemgetter('citation_count'),reverse=True)
    # get the most cited paper from the top 100 most alsoread papers
    MostCited = top100_data[0]['bibcode']
    # get the most papers cited BY the top 100 most alsoread papers
    # sorted by citation
    refs100 = flatten(map(lambda a: a['reference'], top100_data))
    RefFreq = get_frequencies(refs100)
    # get the papers that cite the top 100 most alsoread papers
    # sorted by frequency
    cits100 = get_citing_papers(bibcodes=top100)
    CitFreq = get_frequencies(cits100)
    # now we have everything to build the recommendations
    FieldNames = 'Field definitions:'
    Recommendations = []
    Recommendations.append(FieldNames)
    Recommendations.append(G[0])
    Recommendations.append(BeforeFreq[0][0])
    if AfterFreq[0][0] == BeforeFreq[0][0]:
        try:
            Recommendations.append(AfterFreq[1][0])
        except:
            Recommendations.append(AfterFreq[0][0])
    else:
        Recommendations.append(AfterFreq[0][0])
    try:
        Recommendations.append(rndm.choice(AlsoFreq[:10])[0])
    except:
        Recommendations.append(AlsoFreq[0][0])
    Recommendations.append(mostRecent)
    try:
        Recommendations.append(rndm.choice(CitFreq[:10])[0])
    except:
        Recommendations.append(CitFreq[0][0])
    try:
        Recommendations.append(rndm.choice(RefFreq[:10])[0])
    except:
        Recommendations.append(RefFreq[0][0])
    Recommendations.append(MostCited)

    return Recommendations

# The actual recommending functions
def get_recommendations(bibcode):
    '''
    Recommendations for a single bibcode
    '''
    vec = make_paper_vector(bibcode)
    pvec = project_paper(vec)
    pclust = find_paper_cluster(pvec,bibcode)
    cvec = project_paper(pvec,pcluster=pclust)
    close = find_closest_cluster_papers(pclust,cvec)
    R = find_recommendations(close,remove=bibcode)
    # Get meta data for the recommendations
    meta_dict = get_article_data(R[1:], check_references=False)
    # Filter out any bibcodes for which no meta data was found
    recommendations = filter(lambda a: a in meta_dict, R)

    result = {'paper':bibcode,
              'recommendations':[{'bibcode':x,'title':meta_dict[x]['title'], 
              'author':meta_dict[x]['author']} for x in recommendations[1:]]}

    return result

def get_suggestions(**args):
    '''
    Get recommendations for a list of bibcodes. Example:
    get recommendations based on recently read papers
    These are single recommendations for each submitted
    bibcode. These recommendations are determined by first
    determining the cluster to which the input bibcode is
    assigned to, and then the cluster paper is determined
    that is most recent, most read and as close as possible.
    '''
    if 'cookie' in args:
        biblist = get_recently_viewed(args['cookie'])
    elif 'bibcodes' in args:
        biblist = args['bibcodes']
    suggestions = []
    Nselect = config.RECOMMENDER_MAX_INPUT
    input_data = get_article_data(biblist)
    for entry in input_data[:config.RECOMMENDER_INPUT_LIMIT]:
        bibcode = entry['bibcode']
        pdate_p = make_date(entry['pubdate'])
        vec = make_paper_vector(bibcode)
        papervec = array(vec)
        if len(vec) == 0:
            continue
        try:
            pvec = project_paper(vec)
            pclust=find_paper_cluster(pvec,bibcode)
        except:
            continue
        clusterPapers = find_cluster_papers(pclust)
        Nclusterpapers= len(clusterPapers)
        if Nclusterpapers == 0:
            continue
        if Nclusterpapers > Nselect:
            selection = rndm.sample(range(Nclusterpapers),Nselect)
            clusterSelection = map(lambda a: clusterPapers[a], selection)
        else:
            clusterSelection = clusterPapers
        resdicts = []
        for entry in clusterSelection:
            paper   = entry['paper']
            reads   = entry['reads']
            pdate_c = entry['pubdate']
            cpvec = cPickle.loads(entry['vector'])
            # remove potential suggestions that are in the
            # submitted list of bibcodes, or in already
            # generated suggestions
            if paper in biblist or paper in suggestions:
                continue
            # calculate reads rate
            time_span = max(1,abs((pdate_c - pdate_p).days))
            multiplier = float(reads)/float(time_span)
            dist = linalg.norm(papervec-cpvec)
            resdicts.append({'bibcode':paper, 'year':int(paper[:4]), 'distance':dist, 'reads':multiplier})
        # sort by year (high to low), then distance (low to high),
        # then reads (high to low)
        a = multikeysort(resdicts, ['-year', 'distance', '-reads'])
        suggestions.append(a[0]['bibcode'])
        if len(suggestions) == config.RECOMMENDER_SUGGEST_NUMBER:
            break
    # Get meta data for the recommendations
    meta_dict = get_article_data(suggestions, check_references=False)
    # Filter out any bibcodes for which no meta data was found
    suggestions = filter(lambda a: a in meta_dict, suggestions)
    result = {'type':'recently viewed',
                  'recommendations':[{'bibcode':x,'title':meta_dict[x]['title'], 
                  'author':meta_dict[x]['author']} for x in suggestions]
             }
    return result
