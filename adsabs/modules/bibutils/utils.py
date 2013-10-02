'''
Created on Jul 16, 2013

@author: ehenneken
'''

# general module imports
import sys
import os
import time
import operator
import glob
from itertools import groupby
from multiprocessing import Process, Queue, cpu_count
import xlwt
import uuid
import simplejson
from flask import current_app as app
from flask.ext.solrquery import solr #@UnresolvedImport
from flask.ext.adsdata import adsdata #@UnresolvedImport
# local imports
from config import config
from .errors import SolrCitationQueryError
from .errors import SolrReferenceQueryError
from .errors import SolrMetaDataQueryError
from .errors import MongoQueryError

__all__ = ['get_suggestions','get_citations','get_references','get_meta_data']

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
    def run(self):
        while True:
            bibcode = self.task_queue.get()
            if bibcode is None:
                break
            try:
                doc = adsdata.get_doc(bibcode)
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
    def _get_references_number(self,bbc):
        collection = adsdata.get_collection('references')
        res = collection.find_one({'_id': bbc})
        Nrefs = 0
        if res:
            Nrefs = len(res.get('references',[]))
        return Nrefs
    def _is_refereed(self,bbc):
        collection = adsdata.get_collection('refereed')
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
                cit_collection = adsdata.get_collection('citations')
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
    def run(self):
        while True:
            bibcode = self.task_queue.get()
            if bibcode is None:
                break
            try:
                pubyear = int(bibcode[:4])
                cit_collection = adsdata.get_collection('citations')
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

def legacy_format(data):
    entry_mapping = {0:0, 1:2, 2:3, 3:1, 4:4, 5:6, 6:7, 7:5}
    citation_histogram = {}
    for (year,values) in data['citation histogram'].items():
        entries = values.split(':') 
        new_entries = [entries[entry_mapping[i]] for i in range(len(entries))]
        citation_histogram[year] = ":".join(new_entries)
    return data['all stats'],data['refereed stats'],data['all reads'],data['refereed reads'],data['paper histogram'],data['reads histogram'],citation_histogram,data['metrics series']

def export_metrics(data):
    stats = legacy_format(data)
    Total = stats[0]
    Refereed = stats[1]
    totalReads = stats[2]
    refereedReads = stats[3]
    paperhist = stats[4]
    readshist = stats[5]
    citshist = stats[6]
    series = stats[7]

    papers_table = (('Number of papers', (Total, Refereed)), ('Normalized paper count', (Total, Refereed)), ('Total number of reads', (totalReads, refereedReads)), 
                  ('Average number of reads', (totalReads, refereedReads)), ('Median number of reads', (totalReads, refereedReads)), 
                  ('Total number of downloads', (totalReads, refereedReads)), ('Average number of downloads', (totalReads, refereedReads)), 
                  ('Median number of downloads', (totalReads, refereedReads)))
    citation_table = (('Number of citing papers', (Total, Refereed)), ('Total citations', (Total, Refereed)), ('Average citations', (Total, Refereed)), 
                      ('Median citations', (Total, Refereed)), ('Normalized citations', (Total, Refereed)), ('Refereed citations', (Total, Refereed)), 
                      ('Average refereed citations', (Total, Refereed)), ('Median refereed citations', (Total, Refereed)), ('Normalized refereed citations', (Total, Refereed)))
    indices_table = (('H-index', (Total, Refereed)), ('g-index', (Total, Refereed)), ('e-index', (Total, Refereed)), 
                     ('i10-index', (Total, Refereed)), ('tori index', (Total, Refereed)), ('roq index', (Total, Refereed)), ('m-index', (Total, Refereed)))
    ############
    #generation of an excel file
    wbk = xlwt.Workbook(encoding='UTF-8')
    #style to have bold
    fnt = xlwt.Font()
    fnt.bold = True
    fnt.height = 250 #the font size
    style = xlwt.XFStyle()
    style.font = fnt
    #Writing the page with the tables of statistics
    sheet = wbk.add_sheet('Papers, citations, indices')
    #counter of rows
    row = 0
    sheet.write(row, 0, 'Papers', style)
    row += 1
    sheet.write(row, 1, 'Total')
    sheet.write(row, 2, 'Refereed')
    row += 1
    for elem in papers_table:
        #I write the line
        sheet.write(row, 0, elem[0])
        sheet.write(row, 1, elem[1][0][elem[0]])
        sheet.write(row, 2, elem[1][1][elem[0]])
        row+=1
    row += 1
    sheet.write(row, 0, 'Citations', style)
    row += 1
    sheet.write(row, 1, 'Total')
    sheet.write(row, 2, 'Refereed')
    row += 1
    for elem in citation_table:
        #I write the line
        sheet.write(row, 0, elem[0])
        sheet.write(row, 1, elem[1][0][elem[0]])
        sheet.write(row, 2, elem[1][1][elem[0]])
        row+=1
    row += 1
    sheet.write(row, 0, 'Indices', style)
    row += 1
    sheet.write(row, 1, 'Total')
    sheet.write(row, 2, 'Refereed')
    row += 1
    for elem in indices_table:
        #I write the line
        sheet.write(row, 0, elem[0])
        sheet.write(row, 1, elem[1][0][elem[0]])
        sheet.write(row, 2, elem[1][1][elem[0]])
        row+=1
    #Writing the page with the data for the plot #1
    sheet = wbk.add_sheet('Publications per year')
    #I delete useless keys in the dictionary
    del paperhist['type']
    row = 0
    #I write the name of the data 
    sheet.write(row, 0, 'Publications per year', style)
    row += 1
    #I write the labels on the first row
    sheet.write(row, 0, 'Year')
    sheet.write(row, 1, 'Refereed')
    sheet.write(row, 2, 'Non Refereed')
    sheet.write(row, 3, 'Normalized Refereed')
    sheet.write(row, 4, 'Normalized Non Refereed')
    row += 1
    years = paperhist.keys()
    years.sort()
    for year in years:
        sheet.write(row, 0, year)
        datan = paperhist[year].split(':')
        sheet.write(row, 1, float(datan[1]))
        sheet.write(row, 2, float(datan[0]) - float(datan[1]))
        sheet.write(row, 3, float(datan[3]))
        sheet.write(row, 4, float(datan[2]) - float(datan[3]))
        row += 1
    #Writing the page with the data for the plot #2
    sheet = wbk.add_sheet('Reads per year')
    #I delete useless keys in the dictionary
    del readshist['type']
    row = 0
    #I write the name of the data 
    sheet.write(row, 0, 'Reads per year', style)
    row += 1
    #I write the labels on the first row
    sheet.write(row, 0, 'Year')
    sheet.write(row, 1, 'Refereed')
    sheet.write(row, 2, 'Non Refereed')
    sheet.write(row, 3, 'Normalized Refereed')
    sheet.write(row, 4, 'Normalized Non Refereed')
    row += 1
    years = readshist.keys()
    years.sort()
    for year in years:
        sheet.write(row, 0, year)
        datan = readshist[year].split(':')
        sheet.write(row, 1, float(datan[1]))
        sheet.write(row, 2, float(datan[0]) - float(datan[1]))
        sheet.write(row, 3, float(datan[3]))
        sheet.write(row, 4, float(datan[2]) - float(datan[3]))
        row += 1
    #Writing the page with the data for the plot #3
    sheet = wbk.add_sheet('Citations per year')
    del citshist['type']
    row = 0
    #I write the name of the data 
    sheet.write(row, 0, 'Citations per year', style)
    row += 1
    #I write the labels on the first row
    sheet.write(row, 0, 'Year')
    sheet.write(row, 1, 'Ref. citations to ref. papers')
    sheet.write(row, 2, 'Ref. citations to non ref. papers')
    sheet.write(row, 3, 'Non ref. citations to ref. papers')
    sheet.write(row, 4, 'Non ref. citations to non ref. papers')
    sheet.write(row, 5, 'Normalized Ref. citations to ref. papers')
    sheet.write(row, 6, 'Normalized Ref. citations to non ref. papers')
    sheet.write(row, 7, 'Normalized Non ref. citations to ref. papers')
    sheet.write(row, 8, 'Normalized Non ref. citations to non ref. papers')
    row += 1
    years = citshist.keys()
    years.sort()
    for year in years:
        sheet.write(row, 0, year)
        datan = citshist[year].split(':')
        # extract the two groups of data
        from_all_to_all, from_all_to_ref, from_ref_to_ref, from_ref_to_all = float(datan[0]), float(datan[1]), float(datan[2]), float(datan[3])
        norm_from_all_to_all, norm_from_all_to_ref, norm_from_ref_to_ref, norm_from_ref_to_all = float(datan[4]), float(datan[5]), float(datan[6]), float(datan[7])
        # compute the missing for the normal
        from_all_to_notref = from_all_to_all - from_all_to_ref
        from_ref_to_notref = from_ref_to_all - from_ref_to_ref
        from_notref_to_ref = from_all_to_ref - from_ref_to_ref
        from_notref_to_notref = from_all_to_notref - from_ref_to_notref
        # and then for the normalized
        norm_from_all_to_notref = norm_from_all_to_all - norm_from_all_to_ref
        norm_from_ref_to_notref = norm_from_ref_to_all - norm_from_ref_to_ref
        norm_from_notref_to_ref = norm_from_all_to_ref - norm_from_ref_to_ref
        norm_from_notref_to_notref = norm_from_all_to_notref - norm_from_ref_to_notref
        sheet.write(row, 1, from_ref_to_ref)
        sheet.write(row, 2, from_ref_to_notref)
        sheet.write(row, 3, from_notref_to_ref)
        sheet.write(row, 4, from_notref_to_notref)
        sheet.write(row, 5, norm_from_ref_to_ref)
        sheet.write(row, 6, norm_from_ref_to_notref)
        sheet.write(row, 7, norm_from_notref_to_ref)
        sheet.write(row, 8, norm_from_notref_to_notref)
        row += 1
    # Writing the page with the data for the plot #4
    sheet = wbk.add_sheet('Indices')
    del series['type']
    row = 0
    # Write the name of the data 
    sheet.write(row, 0, 'Indices', style)
    row += 1
    # Write the labels on the first row
    sheet.write(row, 0, 'Year')
    sheet.write(row, 1, 'h-index')
    sheet.write(row, 2, 'g-index')
    sheet.write(row, 3, 'i10-index')
    sheet.write(row, 4, 'tori-index')
    row += 1
    years = series.keys()
    years.sort()
    for year in years:
        sheet.write(row, 0, str(year))
        datan = series[year].split(':')
        sheet.write(row, 1, float(datan[0]))
        sheet.write(row, 2, float(datan[1]))
        sheet.write(row, 3, float(datan[2]))
        sheet.write(row, 4, float(datan[3]))
        row += 1
    # Save the spreadsheet to a temporary file
    filename = config.METRICS_TMP_DIR + '/Metrics' + str(uuid.uuid4())
    wbk.save(filename)
    # Remove all temporary files older than 2 hours
    now = time.time()
    stale_tmp_files = filter(lambda f: now-os.stat(f).st_mtime > 7200, glob.glob("%s/Metrics*"%config.METRICS_TMP_DIR))
    for entry in stale_tmp_files:
        os.remove(entry)
    return os.path.basename(filename)
