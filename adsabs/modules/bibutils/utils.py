'''
Created on Jul 16, 2013

@author: ehenneken
'''

# general module imports
import sys
import os
import operator
from itertools import groupby
from multiprocessing import Process, Queue, cpu_count
import urllib
import requests
from flask import current_app as app
from flask.ext.solrquery import solr #@UnresolvedImport
import adsdata
# local imports
from config import config
from .errors import SolrCitationQueryError
from .errors import SolrReferenceQueryError
from .errors import SolrMetaDataQueryError
from .errors import MongoQueryError

__all__ = ['get_suggestions','get_citations','get_references','get_meta_data']

def chunks(l, n):
    """ 
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

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
            bbc = self.task_queue.get()
            if bbc is None:
                break
            Nauths = 1
            try:
                bibcode,Nauths = bbc.split('/')
            except:
                bibcode = bbc
            q = 'citations(bibcode:%s)' % bibcode
            fl= 'bibcode,property,reference'
            try:
                if sys.platform == 'darwin':
                    search_results = solr_req(config.SOLRQUERY_URL + '/select', q=q, fl=fl, rows=config.BIBUTILS_MAX_HITS)
                    result_field = 'response'
                else:
                    result_field = 'results'
                # do the query and filter out the results without the bibcode field
                # (publications without citations return an empty document)
                    resp = solr.query(q, rows=config.BIBUTILS_MAX_HITS, fields=fl.split(','))
                    search_results = resp.search_response()
                # gather citations and put them into the results queue
                citations = []
                cits = []
                ref_cits = []
                non_ref_cits = []
                for doc in search_results[result_field]['docs']:
                    if not 'bibcode' in doc:
                        continue
                    pubyear = int(bibcode[:4])
                    try:
                        Nrefs = len(doc['reference'])
                    except:
                        Nrefs = 0
                    citations.append(doc['bibcode'])
                    cits.append((doc['bibcode'],Nrefs,int(Nauths),pubyear))
                    if 'REFEREED' in doc['property']:
                        ref_cits.append((doc['bibcode'],Nrefs,int(Nauths),pubyear))
                    else:
                        non_ref_cits.append((doc['bibcode'],Nrefs,int(Nauths),pubyear))
                self.result_queue.put({'bibcode':bibcode,'citations':citations,'cit_info':cits,'ref_cit_info':ref_cits,'non_ref_cit_info':non_ref_cits})
            except SolrCitationQueryError, e:
                app.logger.error("Solr citation query for %s blew up (%s)" % (bibcode,e))
                raise
        return

class DataHarvester(Process):
    """
    Class to allow parallel retrieval from publication data from Solr
    """
    def __init__(self, task_queue, result_queue):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            biblist = self.task_queue.get()
            if biblist is None:
                break
            q = " OR ".join(map(lambda a: "bibcode:%s"%a, biblist))
            fl = 'bibcode,reference,author_norm,property,read_count'
            try:
                if sys.platform == 'darwin':
                    search_results = solr_req(config.SOLRQUERY_URL + '/select', q=q, fl=fl, rows=config.BIBUTILS_MAX_HITS)
                    result_field = 'response'
                else:
                    result_field = 'results'
                # do the query and filter out the results without the bibcode field
                # (publications without citations return an empty document)
                    resp = solr.query(q, rows=config.BIBUTILS_MAX_HITS, fields=fl.split(','))
                    search_results = resp.search_response()
                # gather citations and put them into the results queue
                self.result_queue.put(search_results[result_field]['docs'])
            except SolrCitationQueryError, e:
                app.logger.error("Solr data query for %s blew up (%s)" % (q,e))
                raise
        return

class MongoHarvester(Process):
    """
    Class to allow parallel retrieval from publication data from Mongo
    """
    def __init__(self, task_queue, result_queue):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.session = adsdata.get_session()
    def run(self):
        while True:
            bibcode = self.task_queue.get()
            if bibcode is None:
                break
            try:
                doc = self.session.get_doc(bibcode)
                self.result_queue.put(doc)
            except MongoQueryError, e:
                app.logger.error("Mongo data query for %s blew up (%s)" % (bibcode,e))
                raise
        return

class MongoCitationHarvester(Process):
    """
    Class to allow parallel retrieval from citation data from Mongo
    """
    def __init__(self, task_queue, result_queue):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.session = adsdata.get_session()
    def _get_references_number(self,bbc):
        collection = self.session.get_collection('references')
        res = collection.find_one({'_id': bbc})
        Nrefs = 0
        if res:
            Nrefs = len(res.get('references',[]))
        return Nrefs
    def _is_refereed(self,bbc):
        collection = self.session.get_collection('refereed')
        res = collection.find_one({'_id': bbc})
        if res:
            return True
        else:
            return False
    def run(self):
        while True:
            bbc = self.task_queue.get()
            if bbc is None:
                break
            Nauths = 1
            try:
                bibcode,Nauths = bbc.split('/')
            except:
                bibcode = bbc
            try:
                pubyear = int(bibcode[:4])
                cit_collection = self.session.get_collection('citations')
                res1 = cit_collection.find_one({'_id': bibcode})
                if res1:
                    citations = res1.get('citations',[])
                    refereed_citations = filter(lambda a: self._is_refereed(a)==True, citations)
                    non_refereed_citations = filter(lambda a: a not in refereed_citations, citations)
                    cits = [(x,self._get_references_number(x),int(Nauths),pubyear) for x in citations]
                    ref_cits = [(x,self._get_references_number(x),int(Nauths),pubyear) for x in refereed_citations]
                    non_ref_cits = [(x,self._get_references_number(x),int(Nauths),pubyear) for x in non_refereed_citations]
                else:
                    citations = cits = ref_cits = non_ref_cits = []
                self.result_queue.put({'bibcode':bibcode,'citations':citations,'cit_info':cits,'ref_cit_info':ref_cits,'non_ref_cit_info':non_ref_cits})
            except MongoQueryError, e:
                app.logger.error("Mongo data query for %s blew up (%s)" % (bibcode,e))
                raise
        return

class MongoCitationListHarvester(Process):
    """
    Class to allow parallel retrieval of citation data from Mongo
    """
    def __init__(self, task_queue, result_queue):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.session = adsdata.get_session()
    def run(self):
        while True:
            bibcode = self.task_queue.get()
            if bibcode is None:
                break
            try:
                pubyear = int(bibcode[:4])
                cit_collection = self.session.get_collection('citations')
                res1 = cit_collection.find_one({'_id': bibcode})
                if res1:
                    citations = res1.get('citations',[])
                else:
                    citations = cits = ref_cits = non_ref_cits = []
                self.result_queue.put({'citations':citations})
            except MongoQueryError, e:
                app.logger.error("Mongo citation list query for %s blew up (%s)" % (bibcode,e))
                raise
        return

def get_citations(**args):
    """
    Method to prepare the actual citation dictionary creation
    """
    # create the queues
    tasks = Queue()
    results = Queue()
    # how many threads are there to be used
    if 'threads' in args:
        threads = args['threads']
    else:
        threads = cpu_count()
    # for the metrics module we need more metadata
    if 'type' in args:
        data_type = args['type']
    else:
        data_type = 'default'
    if data_type == 'metrics':
        pubdata = args['pubdata']
        bibcodes = map(lambda a: "%s/%s"%(a,max(1,len(pubdata[a].get('author_norm',0)))),args['bibcodes'])
    else:
        bibcodes = args['bibcodes']
    # initialize the "harvesters" (each harvester get the citations for a bibcode)
    if config.BIBUTILS_CITATION_SOURCE == 'SOLR':
        harvesters = [ CitationHarvester(tasks, results) for i in range(threads)]
    else:
        harvesters = [ MongoCitationHarvester(tasks, results) for i in range(threads)]
    # start the harvesters
    for b in harvesters:
        b.start()
    # put the bibcodes in the tasks queue
    num_jobs = 0
    for bib in bibcodes:
        tasks.put(bib)
        num_jobs += 1
    # add some 'None' values at the end of the tasks list, to faciliate proper closure
    for i in range(threads):
        tasks.put(None)
    # gather all results into one citation dictionary
    cit_dict = {}
    ref_cit_dict = {}
    non_ref_cit_dict = {}
    while num_jobs:
        data = results.get()
        if len(data['citations']) > 0:
            if data_type == 'default':
                cit_dict[data['bibcode']] = data['citations']
            else:
                cit_dict[data['bibcode']] = data['cit_info']
                ref_cit_dict[data['bibcode']] = data['ref_cit_info']
                non_ref_cit_dict[data['bibcode']] = data['non_ref_cit_info']
        num_jobs -= 1

    if data_type == 'default':
        return cit_dict
    else:
        return cit_dict,ref_cit_dict,non_ref_cit_dict

def get_publication_data(**args):
    """
    Method to prepare the actual citation dictionary creation
    """
    # create the queues
    tasks = Queue()
    results = Queue()
    # how many threads are there to be used
    if 'threads' in args:
        threads = args['threads']
    else:
        threads = cpu_count()
    # initialize the "harvesters" (each harvester get the citations for a bibcode)
    harvesters = [ DataHarvester(tasks, results) for i in range(threads)]
    # start the harvesters
    for b in harvesters:
        b.start()
    # put the bibcodes in the tasks queue
    num_jobs = 0
    for biblist in args['biblists']:
        tasks.put(biblist)
        num_jobs += 1
    # add some 'None' values at the end of the tasks list, to faciliate proper closure
    for i in range(threads):
        tasks.put(None)
    # gather all results into one publication dictionary
    publication_data = {}
    while num_jobs:
        data = results.get()
        for item in data:
            publication_data[item['bibcode']] = item
        num_jobs -= 1
    return publication_data

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
    try:
        # Get the information from Solr
        resp = solr.query(q, rows=config.BIBUTILS_MAX_HITS, fields=['bibcode,title,first_author'])
    except SolrMetaDataQueryError, e:
        app.logger.error("Solr references query for %s blew up (%s)" % (bibcode,e))
        raise
    # Collect meta data
    search_results = resp.search_response()
    for doc in search_results['results']['docs']:
        title = 'NA'
        if 'title' in doc: title = doc['title'][0]
        author = 'NA'
        if 'first_author' in doc: author = "%s,+"%doc['first_author'].split(',')[0]
        data_dict[doc['bibcode']] = {'title':title, 'author':author}
    return data_dict

def get_mongo_data(**args):
    """
    Method to prepare the actual citation dictionary creation
    """
    # create the queues
    tasks = Queue()
    results = Queue()
    # how many threads are there to be used
    if 'threads' in args:
        threads = args['threads']
    else:
        threads = cpu_count()
    # initialize the "harvesters" (each harvester get the citations for a bibcode)
    harvesters = [ MongoHarvester(tasks, results) for i in range(threads)]
    # start the harvesters
    for b in harvesters:
        b.start()
    # put the bibcodes in the tasks queue
    num_jobs = 0
    for bibcode in args['bibcodes']:
        tasks.put(bibcode)
        num_jobs += 1
    # add some 'None' values at the end of the tasks list, to faciliate proper closure
    for i in range(threads):
        tasks.put(None)
    # gather all results into one publication dictionary
    ads_data = {}
    while num_jobs:
        data = results.get()
        if data:
            ads_data[data['_id']] = data
        num_jobs -= 1
    return ads_data

def get_citing_papers(**args):
    # create the queues
    tasks = Queue()
    results = Queue()
    # how many threads are there to be used
    if 'threads' in args:
        threads = args['threads']
    else:
        threads = cpu_count()
    bibcodes = args.get('bibcodes',[])
    # initialize the "harvesters" (each harvester get the citations for a bibcode)
    harvesters = [ MongoCitationListHarvester(tasks, results) for i in range(threads)]
    # start the harvesters
    for b in harvesters:
        b.start()
    # put the bibcodes in the tasks queue
    num_jobs = 0
    for bib in bibcodes:
        tasks.put(bib)
        num_jobs += 1
    # add some 'None' values at the end of the tasks list, to faciliate proper closure
    for i in range(threads):
        tasks.put(None)
    # gather all results into one citation dictionary
    cit_list = []
    while num_jobs:
        data = results.get()
        cit_list += data.get('citations',[])
        num_jobs -= 1
    return cit_list

def get_references(**args):
    """
    Get the references for a set of bibcodes
    """
    papers= []
    # This information can be retrieved with one single Solr query
    # (just an 'OR' query of a list of bibcodes)
    # To restrict the size of the query URL, we split the list of
    # bibcodes up in a list of smaller lists
    biblists = list(chunks(args['bibcodes'], config.METRICS_CHUNK_SIZE))
    for biblist in biblists:
        q = " OR ".join(map(lambda a: "bibcode:%s"%a, biblist))
        try:
            # Get the information from Solr
            # We only need the contents of the 'reference' field (i.e. the list of bibcodes 
            # referenced by the paper at hand)
            resp = solr.query(q, rows=config.BIBUTILS_MAX_HITS, fields=['reference'])
        except SolrReferenceQueryError, e:
            app.logger.error("Solr references query for %s blew up (%s)" % (q,e))
            raise
        # Collect all bibcodes in a list (do NOT remove multiplicity)
        search_results = resp.search_response()
        for doc in search_results['results']['docs']:
            if 'reference' in doc:
                papers += doc['reference']
    return papers

def get_publications_from_query(q):
    try:
        # Get the information from Solr
        resp = solr.query(q, rows=config.BIBUTILS_MAX_HITS, fields=['reference'])
    except SolrReferenceQueryError, e:
        app.logger.error("Solr publications query for %s blew up (%s)" % (q,e))
        raise
    # Collect all bibcodes in a list
    search_results = resp.search_response()
    return map(lambda a: a['bibcode'],search_results['results']['docs'])

def get_bibcodes_from_private_library(id):
    sys.stderr.write('Private libraries are not yet implemented')
    return []
    
