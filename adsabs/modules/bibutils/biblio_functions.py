'''
Created on Jul 16, 2013

@author: ehenneken
'''

# general module imports
import sys
import os
import operator
from itertools import groupby
# BEER-specific imports
from flask import current_app as app
from config import config
from utils import get_references
from utils import get_citing_papers
from utils import get_meta_data
from adsabs.extensions import statsd
 
__all__ = ['get_suggestions']

def get_suggestions(**args):

    timer = statsd.timer("bibutils.get_suggestions.generate_time")
    timer.start()
    
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
    cits = get_citing_papers(bibcodes=bibcodes)
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
    paperFreq = filter(lambda a: a[1] > config.BIBUTILS_THRESHOLD_FREQUENCY and a[1] < len(bibcodes), paperFreq)
    # get metadata for suggestions
    meta_dict = get_meta_data(results=paperFreq[:Nsuggestions])
    timer.stop()
    # return results in required format
    if output_format == 'score':
        return [{'bibcode':x,'score':y, 'title':meta_dict[x]['title'], 'author':meta_dict[x]['author']} for (x,y) in paperFreq[:Nsuggestions] if x in meta_dict.keys()]
    else:
        return [{'bibcode':x,'score':'NA', 'title':meta_dict[x]['title'], 'author':meta_dict[x]['author']} for (x,y) in paperFreq[:Nsuggestions] if x in meta_dict.keys()]
