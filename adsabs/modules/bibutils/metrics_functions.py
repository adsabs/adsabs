# general modules
import os
import operator
import sys
import time
import itertools
from multiprocessing import Pool, current_process
from multiprocessing import Manager
# BEER specific imports
from flask import current_app as app
# methods to retrieve various types of data
from utils import get_metrics_data
from utils import get_mongo_data
from utils import get_publications_from_query
from utils import chunks
# Get all pertinent configs
from config import config
# Every type of 'metric' is calculated in a 'model'
import metricsmodels
# memory mapped data
manager = Manager()
model_results = manager.list([])
# Helper functions
def sort_list_of_lists(L, index, rvrs=True):
    """
    Sort a list of lists with 'index' as sort key
    """
    return sorted(L, key=operator.itemgetter(index), reverse=rvrs)
# Creation of data vectors for stats calculations
def make_vectors(pubs,ads_data,metrics_dict):
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
    8: dictionary with pre-calculated data
    """
    attr_list = []
    for bibcode in pubs:
        vector = [str(bibcode)]
        vector.append(int(ads_data.get(bibcode,{}).get('refereed',False)))
        vector.append(metrics_dict.get(bibcode,{}).get('citation_num',0))
        vector.append(metrics_dict.get(bibcode,{}).get('refereed_citation_num',0))
        vector.append(metrics_dict.get(bibcode,{}).get('author_num',1))
        vector.append(sum(ads_data.get(bibcode,{}).get('reads',[])))
        vector.append(sum(ads_data.get(bibcode,{}).get('downloads',[])))
        vector.append(ads_data.get(bibcode,{}).get('reads',[]))
        vector.append(metrics_dict.get(bibcode,{}))
        attr_list.append(vector)
    return attr_list
# D. General data accumulation
def get_attributes(args):
    """
    Gather all data necessary for metrics calculations
    """
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
    biblists = list(chunks(bibcodes,config.METRICS_CHUNK_SIZE))
    # Now gather all usage data numbers from the MongoDB 'adsdata' collection,
    # keyed on bibcode
    ads_data = get_mongo_data(bibcodes=bibcodes)
    missing_bibcodes = filter(lambda a: a not in ads_data.keys(), bibcodes)
    app.logger.error("Bibcodes found with missing metadata: %s" % ",".join(missing_bibcodes))
    bibcodes = filter(lambda a: a not in missing_bibcodes, bibcodes)
    # Get precomputed and citation data
    metrics_data = get_metrics_data(bibcodes=bibcodes)
    # Get the number of citing papers
    Nciting = len(list(set(itertools.chain(*map(lambda a: a['citations'], metrics_data.values())))))
    Nciting_ref = len(list(set(itertools.chain(*map(lambda a: a['refereed_citations'], metrics_data.values())))))
    # The attribute vectors will be used to calculate the metrics
    attr_list = make_vectors(bibcodes,ads_data,metrics_data)
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

# Uglify output results into how the old metrics module produced it output
def legacy_format(data):
    entry_mapping = {0:0, 1:2, 2:3, 3:1, 4:4, 5:6, 6:7, 7:5}
    citation_histogram = {}
    for (year,values) in data['citation histogram'].items():
        entries = values.split(':') 
        new_entries = [entries[entry_mapping[i]] for i in range(len(entries))]
        citation_histogram[year] = ":".join(new_entries)
    return data['all stats'],data['refereed stats'],data['all reads'],data['refereed reads'],data['paper histogram'],data['reads histogram'],citation_histogram,data['metrics series']
# General metrics engine
def generate_metrics(**args):
    # First we gather the necessary 'attributes' for all publications involved
    # (see above methods for more details)
    attr_list,num_cit,num_cit_ref = get_attributes(args)
    # What types of metrics are we gather (everything by default)
    stats_models = []
    # Determine the output format (really only used to get the 'legacy format')
    format = args.get('fmt','')
    model_types = args.get('types',config.METRICS_DEFAULT_MODELS)
    # Instantiate the metrics classes, defined in the 'models' module
    for model_class in metricsmodels.data_models(models=model_types.split(',')):
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
    if format == 'legacy':
        return legacy_format(results)
    else:
        return results
