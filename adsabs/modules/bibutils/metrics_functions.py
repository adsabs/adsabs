# general modules
import os
import operator
import sys
from multiprocessing import Pool, current_process
from multiprocessing import Manager
# BEER specific imports
from flask import current_app as app
from adsabs.core.solr import SolrRequest
# methods to retrieve various types of data
from utils import get_citations
from utils import get_mongo_data
from utils import get_publication_data
from utils import get_publications_from_query
# Get all pertinent configs
from config import config
# Every type of 'metric' is calculated in a 'model'
import metricsmodels
# memory mapped data
manager = Manager()
model_results = manager.list([])
# General fuctions
def sort_list_of_lists(L, index, rvrs=True):
    """
    Sort a list of lists with 'index' as sort key
    """
    return sorted(L, key=operator.itemgetter(index), reverse=rvrs)

def chunks(l, n):
    """ 
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def flatten(items):
    """
    Sometimes we need to turn a list of lists into a single list
    """
    result = []
    for item in items:
        if hasattr(item, '__iter__'):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

def get_timespan(biblist):
    """
    Returns the time span (years) for a list of bibcodes
    """
    years = map(lambda a: int(a[:4]), biblist)
    minYr = min(years)
    maxYr = max(years)
    span  = maxYr - minYr + 1
    return max(span,1)

def get_subset(mlist,year):
    """
    Gets the entries out of the list of "attribute" vectors for a certain year
    """
    newlist = []
    for entry in mlist:
        if int(entry[0][:4]) > int(year):
            continue
        newvec = entry[:9]
        citations = entry[8]
        citations = filter(lambda a: int(a[0][:4]) <= int(year), citations)
        newvec.append(citations)
        newvec[2]  = len(citations)
        newlist.append(newvec)
    return newlist

# C. Creation of data vectors for stats calculations
def make_vectors(pubs,pub_data,ads_data,cit_dict,ref_cit_dict,non_ref_cit_dict):
    """
    Most of the metrics/histograms are calculated by manipulation of lists
    (e.g. sums and averages over a list of numbers). Each publication is 
    represented by a 'vector', which is essentially a data structure containing
    all information necessary to calculate metrics. The entries are as follows:
    0: bibcode
    1: refereed status
    2: number of citations
    3: number of refereed citations
    4: number of authors
    5: number of reads
    6: number of downloads
    7: reads number per year
    8: citation dictionary (each value is a 4-tuple)
    9: refereed citation dictionary
    10:non-refereed citation dictionary
    The values of the citation dictionaries contain the bibcode of the citing
    paper and some additional info needed for tori-calculations
    """
    attr_list = []
    for bibcode in pubs:
        vector = [str(bibcode)]
        try:
            properties = pub_data[bibcode]['property']
        except:
            properties = []
        if 'REFEREED' in properties:
            vector.append(1)
        else:
            vector.append(0)
        try:
            Ncits = len(cit_dict[bibcode])
        except:
            Ncits = 0
        vector.append(Ncits)
        try:
            Ncits_ref = len(ref_cit_dict[bibcode])
        except:
            Ncits_ref = 0
        vector.append(Ncits_ref)
        try:
            Nauthors = max(1,len(pub_data[bibcode]['author_norm']))
        except:
            Nauthors = 1
        vector.append(Nauthors)
        try:
            vector.append(sum(ads_data[bibcode]['reads']))
        except:
            vector.append(0)
        try:
            vector.append(sum(ads_data[bibcode]['downloads']))
        except:
            vector.append(0)
        try:
            vector.append(ads_data[bibcode]['reads'])
        except:
            vector.append([])
        try:
            vector.append(cit_dict[bibcode])
        except:
            vector.append([])
        try:
            vector.append(ref_cit_dict[bibcode])
        except:
            vector.append([])
        try:
            vector.append(non_ref_cit_dict[bibcode])
        except:
            vector.append([])
        attr_list.append(vector)
    return attr_list
# D. General data accumulation
def get_attributes(args):
    """
    Gather all data necessary for metrics calculations
    """
    solr_url = config.SOLR_URL
    max_hits = config.METRICS_MAX_HITS
    threads  = config.METRICS_THREADS
    chunk_size = config.METRICS_CHUNK_SIZE
    # Get publication information
    if 'query' in args:
        # If we were fed a query, gather the associated bibcodes
        bibcodes = get_publications_from_query(args['query'])
    elif 'bibcodes' in args:
        bibcodes = map(lambda a: a.strip(), args['bibcodes'])
    elif 'libid' in args:
        # In theory we allow for retrieving bibcodes from private libraries
        # Clearly this will currently not be used
        bibcodes = get_bibcodes_from_private_library(args['libid'])
    # Split the list of bibcodes up in chunks, for parallel processing
    biblists = list(chunks(bibcodes,chunk_size))
    # Gather all publication information into one publication dictionary,
    # keyed on bibcode
    publication_data = get_publication_data(biblists=biblists)
    missing_bibcodes = filter(lambda a: a not in publication_data.keys(), bibcodes)
    app.logger.error("Bibcodes found with missing metadata: %s" % ",".join(missing_bibcodes))
    bibcodes = filter(lambda a: a not in missing_bibcodes, bibcodes)
    # Get citation dictionaries (all, refereed and non-refereed citations in
    # separate dictionaries, so that we don't have to figure this out later)
    (cit_dict,ref_cit_dict,non_ref_cit_dict) = get_citations(bibcodes=bibcodes, pubdata=publication_data, type='metrics')
    # divide by 4 because the values of the dictionary are 4-tuples
    # and the flattening removed all structure.
    Nciting = len(set([x[0] for v in cit_dict.values() for x in v]))
    Nciting_ref = len(set([x[0] for v in ref_cit_dict.values() for x in v]))
    # Now gather all usage data numbers from the MongoDB 'adsdata' collection
    # This info will get stored in the dictionary 'adsdata', also keyed on bibcode
    ads_data = get_mongo_data(bibcodes=bibcodes)
    # Generate the list of document attribute vectors and then
    # sort this list by citations (descending).
    # The attribute vectors will be used to calculate the metrics
    attr_list = make_vectors(bibcodes,publication_data,ads_data,cit_dict,ref_cit_dict,non_ref_cit_dict)
    # We sort the entries in the attribute list on citation count, which
    # will make e.g. the calculation of 'h' trivial
    attr_list = sort_list_of_lists(attr_list,2)

    return attr_list,Nciting,Nciting_ref

# E. Function to call individual model data generation functions
#    in parallel
def generate_data(model_class):
    model_class.generate_data()
    model_results.append(model_class.results)

# F. Format and export the end results
#    In theory we could build in other formats by e.g. a 'format=foo' in the
#    'args' and implementing an associated procedure in the method
def format_results(data_dict,**args):
    # We want to return JSON, and at the same time support backward compatibility
    # This is achieved by stucturing the resulting JSON into sections that
    # correspond with the output from the 'legacy' metrics module
    stats = ['publications', 'refereed_citations', 'citations', 'metrics','refereed_metrics']
    doc = {}
    doc['all stats'] = dict((k.replace('(Total)','').strip(),v) for d in data_dict for (k,v) in d.items() if '(Total)' in k and d['type'] in stats)
    doc['refereed stats'] = dict((k.replace('(Refereed)','').strip(),v) for d in data_dict for (k,v) in d.items() if '(Refereed)' in k and d['type'] in stats)
    reads = ['reads','downloads']
    doc['all reads'] = dict((k.replace('(Total)','').strip(),v) for d in data_dict for (k,v) in d.items() if '(Total)' in k and d['type'] in reads)
    doc['refereed reads'] = dict((k.replace('(Refereed)','').strip(),v) for d in data_dict for (k,v) in d.items() if '(Refereed)' in k and d['type'] in reads)
    doc['paper histogram'] = dict((k,v) for d in data_dict for (k,v) in d.items() if d['type'] == 'publication_histogram')
    doc['reads histogram'] = dict((k,v) for d in data_dict for (k,v) in d.items() if d['type'] == 'reads_histogram')
#    doc['all citation histogram'] = dict((k,v) for d in data_dict for (k,v) in d.items() if d['type'] == 'all_citation_histogram')
#    doc['refereed citation histogram'] = dict((k,v) for d in data_dict for (k,v) in d.items() if d['type'] == 'refereed_citation_histogram')
    doc['metrics series'] = dict((k,v) for d in data_dict for (k,v) in d.items() if d['type'] == 'metrics_series')
#    a = doc['all citation histogram']
    a = dict((k,v) for d in data_dict for (k,v) in d.items() if d['type'] == 'all_citation_histogram')
    del a['type']
#    b = doc['refereed citation histogram']
    b = dict((k,v) for d in data_dict for (k,v) in d.items() if d['type'] == 'refereed_citation_histogram')
    del b['type']
    c = dict((k,v) for d in data_dict for (k,v) in d.items() if d['type'] == 'non_refereed_citation_histogram')
    doc['citation histogram'] = dict((n, ":".join(["%s:%s"%(x,y) for (x,y) in zip(a[n],b[n])])) for n in set(a)|set(b))
    doc['citation histogram']['type'] = "citation_histogram"
    return doc

# General metrics engine
def generate_metrics(**args):
    # First we gather the necessary 'attributes' for all publications involved
    # (see above methods for more details)
    attr_list,num_cit,num_cit_ref = get_attributes(args)
    # What types of metrics are we gather (everything by default)
    stats_models = []
    try:
        model_types = args['types'].split(',')
    except:
        model_types = config.METRICS_DEFAULT_MODELS
    # Instantiate the metrics classes, defined in the 'models' module
    for model_class in metricsmodels.data_models(models=model_types):
        model_class.attributes = attr_list
        model_class.num_citing = num_cit
        model_class.num_citing_ref = num_cit_ref
        model_class.results = {}
        stats_models.append(model_class)
    # The metrics calculations are sent off in parallel
    rez=Pool(config.METRICS_THREADS).map(generate_data, stats_models)
    # Now shape the results in the final format
    results = format_results(model_results)
    # Send the result back to our caller
    return results
