'''
Created on Jul 16, 2013

@author: ehenneken
'''

# general module imports
import sys
import os
import operator
from itertools import groupby
from multiprocessing import Process, JoinableQueue, cpu_count, Manager
import urllib
import requests
# BEER-specific imports
from flask import current_app as app
# memory mapped data
manager = Manager()
cit_dict = manager.dict()
# local imports
from config import config
from .errors import SolrCitationQueryError
from .errors import SolrReferenceQueryError
from .errors import SolrMetaDataQueryError
 
__all__ = ['get_suggestions','get_citations','get_references','get_meta_data']

def solr_req(url, **kwargs):
    kwargs['wt'] = 'json'
    query_params = urllib.urlencode(kwargs)
    r = requests.get(url, params=query_params)
    return r.json()

class CitationHarvester(Process):
    """
    Class to allow parallel retrieval from citation lists from Solr
    """
    def __init__(self, task_queue, result_queue):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            bibcode = self.task_queue.get()
            if bibcode is None:
                self.task_queue.task_done()
                break
            q = 'citations(bibcode:%s)' % bibcode
            fl= 'bibcode'
            try:
                if sys.platform == 'darwin':
                    resp = solr_req(config.SOLR_URL + '/select', q=q, fl=fl, rows=config.BIBUTILS_MAX_HITS)
                    result_field = 'response'
                else:
                # create the Solr request object
                    req = SolrRequest(q)
                    result_field = 'results'
                # we only need the contents of the 'bibcode' field, i.e. the citations
                    req.params['fl'] = fl
                    req.params['q'] = q
                    req.params['wt'] = 'json'
                    req.params['rows'] = config.BIBUTILS_MAX_HITS
                # do the query and filter out the results without the bibcode field
                # (publications without citations return an empty document)
                    resp = req.get_response().search_response()
                # update the citation dictionary
                cit_dict[bibcode] =  map(lambda b: b['bibcode'], 
                                        filter(lambda a: 'bibcode' in a, resp[result_field]['docs']))
            except SolrCitationQueryError, e:
                app.logger.error("Solr citation query for %s blew up (%s)" % (bibcode,e))
                raise
            finally:
                self.task_queue.task_done()
        return

def get_citations(**args):
    """
    Method to prepare the actual citation dictionary creation
    """
    # create the queues
    tasks = JoinableQueue()
    results = JoinableQueue()
    # how many threads are there to be used
    if 'threads' in args:
        threads = args['threads']
    else:
        threads = cpu_count()
    # initialize the "harvesters" (each harvester get the citations for a bibcode)
    harvesters = [ CitationHarvester(tasks, results) for i in range(threads)]
    # start the harvesters
    for b in harvesters:
        b.start()
    # put the bibcodes in the tasks queue
    for bib in args['bibcodes']:
        tasks.put(bib)
    # add some 'None' values at the end of the tasks list, to faciliate proper closure
    for i in range(threads):
        tasks.put(None)

    tasks.join()
    for b in harvesters:
        b.join()

    return [item for sublist in cit_dict.values() for item in sublist]

def get_meta_data(**args):
    """
    Get the meta data for a set of bibcodes
    """
    data_dict = {}
    # This information can be retrieved with one single Solr query
    # (just an 'OR' query of a list of bibcodes)
    bibcodes = [bibcode for (bibcode,score) in args['results']]
    list = " OR ".join(map(lambda a: "bibcode:%s"%a, bibcodes))
    q = '%s' % list
    # Initialize the Solr reuqest object
    req = SolrRequest(q)
    req.set_rows(config.BIBUTILS_MAX_HITS)
    # Get the title and first author fields from Solr
    req.set_fields(['bibcode,title,first_author'])
    try:
        # Get the information from Solr
        resp = req.get_response().search_response()
    except SolrMetaDataQueryError, e:
        app.logger.error("Solr references query for %s blew up (%s)" % (bibcode,e))
        raise
    # Collect meta data
    for doc in resp['results']['docs']:
        title = 'NA'
        if 'title' in doc: title = doc['title']
        author = 'NA'
        if 'first_author' in doc: author = "%s,+"%doc['first_author'].split(',')[0]
        data_dict[doc['bibcode']] = {'title':title, 'author':author}
    return data_dict

def get_references(**args):
    """
    Get the references for a set of bibcodes
    """
    papers= []
    # This information can be retrieved with one single Solr query
    # (just an 'OR' query of a list of bibcodes)
    list = " OR ".join(map(lambda a: "bibcode:%s"%a, args['bibcodes']))
    q = '%s' % list
    # Initialize the Solr reuqest object
    req = SolrRequest(q)
    # We only need the contents of the 'reference' field (i.e. the list of bibcodes 
    # referenced by the paper at hand)
    req.params['fl'] = 'reference'
    req.params['q'] = q
    req.params['wt'] = 'json'
    req.params['rows'] = config.BIBUTILS_MAX_HITS
    try:
        # Get the information from Solr
        resp = req.get_response().search_response()
    except SolrReferenceQueryError, e:
        app.logger.error("Solr references query for %s blew up (%s)" % (bibcode,e))
        raise
    # Collect all bibcodes in a list (do NOT remove multiplicity)
    for doc in resp['results']['docs']:
        if 'reference' in doc:
            papers += doc['reference']
    return papers

def get_suggestions(**args):
    # initializations
    papers = []
    bibcodes = []
    if 'bibcodes' in args:
        bibcodes = args['bibcodes']
    if len(bibcodes) == 0:
        return []
    # Any overrides for default values?
    if 'Nsuggest' in args:
        Nsuggestions = args['Nsuggest']
    else:
        Nsuggestions = config.BIBUTILS_DEFAULT_SUGGESTIONS
    if 'fmt' in args: 
        output_format = args['fmt']
    else:
        output_format = config.BIBUTILS_DEFAULT_FORMAT
    # get rid of potential trailing spaces
    bibcodes = map(lambda a: a.strip(), bibcodes)[:config.BIBUTILS_MAX_INPUT]
    # start processing
    # get the citations for all publications (keeping multiplicity is essential)
    cits = get_citations(bibcodes=bibcodes, threads=config.BIBUTILS_THREADS)
    # clean up cits
    cits = filter(lambda a: len(a) > 0, cits)
    # get references
    refs = get_references(bibcodes=bibcodes)
    # clean up refs
    refs = filter(lambda a: len(a) > 0, refs)
    # removes papers from the original list to get candidates
    papers = filter(lambda a: a not in bibcodes, cits + refs)
    # establish frequencies of papers in results
    paperFreq = [(k,len(list(g))) for k, g in groupby(sorted(papers))]
    # and sort them, most frequent first
    paperFreq = sorted(paperFreq, key=operator.itemgetter(1),reverse=True)
    # remove all papers with frequencies smaller than threshold
    paperFreq = filter(lambda a: a[1] > config.BIBUTILS_THRESHOLD_FREQUENCY, paperFreq)
    # get metadata for suggestions
    meta_dict = get_meta_data(results=paperFreq[:Nsuggestions])
    # return results in required format
    if output_format == 'score':
        return [{'bibcode':x,'score':y, 'title':meta_dict[x]['title'], 'author':meta_dict[x]['author']} for (x,y) in paperFreq[:Nsuggestions]]
    else:
        return [{'bibcode':x,'score':'NA', 'title':meta_dict[x]['title'], 'author':meta_dict[x]['author']} for (x,y) in paperFreq[:Nsuggestions]]
