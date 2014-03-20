'''
Created on Jul 16, 2013

@author: ehenneken
'''

# general module imports
import sys
import os
import time
from datetime import datetime
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
from adsabs.core.solr import get_document_similar

# local imports
from config import config
from .errors import SolrCitationQueryError
from .errors import SolrReferenceQueryError
from .errors import SolrMetaDataQueryError
from .errors import MongoQueryError
from .pdf_report import MetricsReport

__all__ = ['get_suggestions','get_citations','get_references','get_meta_data']

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

class MetricsDataHarvester(Process):
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
                doc = adsdata.get_metrics_data(bibcode, manipulate=False)
                doc['author_num'] = max(doc['author_num'],1)
                self.result_queue.put(doc)
            except MongoQueryError, e:
                app.logger.error("Mongo metrics data query for %s blew up (%s)" % (bibcode,e))
                raise
        return

def get_metrics_data(**args):
    """
    Method to prepare the actual citation dictionary creation
    """
    # create the queues
    tasks = Queue()
    results = Queue()
    # how many threads are there to be used
    threads = args.get('threads',cpu_count())
    # get the bibcodes for which to get metrics data
    bibcodes = args.get('bibcodes',[])
    # initialize the "harvesters" (each harvester get the metrics data for a bibcode)
    harvesters = [ MetricsDataHarvester(tasks, results) for i in range(threads)]
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
    # gather all results into one metrics data dictionary
    metrics_data_dict = {}
    while num_jobs:
        data = results.get()
        # First remove self-citations for tori data
        try:
            rn_citations, rn_hist = remove_self_citations(bibcodes,data)
            data['rn_citations'] = rn_citations
            data['rn_citations_hist'] = rn_hist
        except:
            pass
        try:
            metrics_data_dict[data['_id']] = data
        except:
            pass
        num_jobs -= 1
    return metrics_data_dict

def remove_self_citations(biblist,datadict):
    # Remove all the entries in "datadict['rn_citation_data']" where the bibcode is
    # in the supplied list of bibcodes
    result = filter(lambda a: a['bibcode'] not in biblist, datadict['rn_citation_data'])
    rn_hist = {}
    for item in result:
        try:
            rn_hist[item['bibcode'][:4]] += item['ref_norm']
        except:
            rn_hist[item['bibcode'][:4]] = item['ref_norm']

    # Now we can aggregate the individual contributions to the overall normalized count
    return sum(map(lambda a: a['ref_norm'], result)), rn_hist

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

def get_publications_from_query(q,sort_order, list_type=None, bigquery_id=None):
    try:
        # Get the information from Solr
        if list_type and list_type == 'similar':
            resp = get_document_similar(q, rows=config.BIBUTILS_MAX_HITS, fields=['bibcode'], sort=sort_order)
        else:
            req = solr.create_request(q, rows=config.BIBUTILS_MAX_HITS, fields=['bibcode'], sort=sort_order)
            if bigquery_id:
                from adsabs.core.solr import bigquery
                bigquery.prepare_bigquery_request(req, bigquery_id)
            req = solr.set_defaults(req)
            resp = solr.get_response(req)

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
    sheet.write(0, 0, data['title'], style)
    #counter of rows
    row = 1
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
    sheet.write(0, 0, data['title'], style)
    #I delete useless keys in the dictionary
    del paperhist['type']
    row = 1
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
    sheet.write(0, 0, data['title'], style)
    #I delete useless keys in the dictionary
    del readshist['type']
    row = 1
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
    sheet.write(0, 0, data['title'], style)
    del citshist['type']
    row = 1
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
    sheet.write(0, 0, data['title'], style)
    del series['type']
    row = 1
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
    filename = config.METRICS_TMP_DIR + '/Metrics' + str(uuid.uuid4()) + ".xls"
    wbk.save(filename)
    # Remove all temporary Excel files older than 2 hours
    now = time.time()
    stale_tmp_files = filter(lambda f: now-os.stat(f).st_mtime > 7200, glob.glob("%s/Metrics*.xls"%config.METRICS_TMP_DIR))
    for entry in stale_tmp_files:
        os.remove(entry)
    return os.path.basename(filename)

def chunks(l, n):
    """ 
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def create_metrics_report(data,file_name='test', report_name='test report', single_record=False):
    '''
    Create a metrics report in PDF format
    '''
    report = MetricsReport()
    # This is where the PDF file will be stored
    report.file_name = config.METRICS_TMP_DIR + "/" + file_name
    # String to be used as name for the report (if empty, only the creation date will get listed)
    report.report_name = report_name
    # Creation date for the report
    report.report_date = datetime.now().strftime("%B %d, %Y (%I:%M%p)")
    # If 'True' this is a report for a single record
    report.single_record = single_record
    # Data to create the report from
    report.data = data
    # Let's start cookin'
    report.run()
    # Remove all temporary PDF files older than 2 hours
    now = time.time()
    stale_tmp_files = filter(lambda f: now-os.stat(f).st_mtime > 7200, glob.glob("%s/Metrics*.pdf"%config.METRICS_TMP_DIR))
    for entry in stale_tmp_files:
        os.remove(entry)
    # Return the file name of the report
    return os.path.basename(report.file_name)
    