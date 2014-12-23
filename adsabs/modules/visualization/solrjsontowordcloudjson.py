from __future__ import division
from nltk import PorterStemmer
import json
import re
import os
import sys
import time

stemmer = PorterStemmer()
stemmer_cache = {}
def stemword(w):
    """
    Memoizes the stemmer for performance reasons
    """
    if not w in stemmer_cache:
        stemmer_cache[w] = stemmer.stem(w)
    return stemmer_cache[w]
    

sw = set(open(os.path.dirname(os.path.abspath(__file__)) +'/solr_stopwords.txt').read().split('\n'))

# so in 250 docs, token has to appear 3 times
MIN_PERCENT_WORD = 0.012
#in all wordclouds, even small ones, a  stemmed token must appear 2 or more times 
MIN_OCCURENCES_OF_WORD = 2

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        sys.stderr.write('%s function took %0.3f ms\n' % (f.func_name, (time2-time1)*1000.0))
        return ret
    return wrap

def list_to_dict(l):
    """
    takes awkward list of list data structure returned in solr json and dictifies it
    """
    d={}
    for index, item in enumerate(l[::2]):
        key=item
        value=l[index*2+1]
        if isinstance(value, list) and value!=[]:
            d[key]=list_to_dict(value)
        else:
            d.setdefault(key, []).append(value)
    return d

#@timing
def idf_dict1(l):
    """
    create an idf dictionary by extracting values from a tvrh response;
    more readable, but several times slower than function below
    """
    idf = {}
    # first look for idf in abstract field
    solrdict = list_to_dict(l)
    for doc in solrdict.itervalues():
        terms = doc.get('abstract',{})
        for w,t in terms.iteritems():
            if not idf.has_key(w):
                idf[w] = t['tf-idf'][0] / t['tf'][0]
    # next add idf values from title field
    for doc in solrdict.itervalues():
        terms = doc.get('title',{})
        for w,t in terms.iteritems():
            if not idf.has_key(w):
                idf[w] = t['tf-idf'][0] / t['tf'][0]
    return idf

#@timing
def idf_dict(l):
    """
    create an idf dictionary by extracting values from a tvrh response
    """
    idf = {}
    # first look for idf in abstract field
    for doc in l[1::2]:
        if len(doc) < 4:
            continue
        words = doc[3]
        for i in range(0, len(words), 2):
            w = words[i]
            if idf.has_key(w):
                continue
            d = dict(zip(*[iter(words[i+1])]*2))
            idf[w] = d['tf-idf'] / d['tf']
    # add any missing words from the title field
    for doc in l[1::2]:
        if len(doc) < 6:
            continue
        words = doc[5]
        for i in range(0, len(words), 2):
            w = words[i]
            if idf.has_key(w):
                continue
            d = dict(zip(*[iter(words[i+1])]*2))
            idf[w] = d['tf-idf'] / d['tf']
    return idf

@timing
def wc_json(solr_json):
    idf_info = idf_dict(solr_json['termVectors'][2:])
    docs = solr_json['response']['docs']
    num_records = len(docs)
    token_freq_dict = {}
    acr_freq_dict= {}
    # these characters indicate word boundaries 
    split_regex = re.compile(r'[\s/.]+')
    markup_regex = re.compile(ur'href=|<sub>.*?</?sub>|<sup>.*?</?sup>|^\W*<?/?sub>?\S?\W*$|^\W*\S?<?/?sub>?\W*$|^\W*<?/?sup>?\S\W*$|^\W*\S?<?/?sup>?\W*$|\bedu\b|\bpng\b|\bjpeg\b|\bcom\b|www|^[\d\W]+$', re.I |re.U)

    def process_entry(a,t): 
        # creating tokens
        a = [w for w in split_regex.split(a) if len(w)>2]
        t = [w for w in split_regex.split(t) if len(w)>2]

        # collapsing words with apostrophes
        a = [w.replace('\'', '') for w in a]
        t = [w.replace('\'', '') for w in t]

        #getting rid of html fragments
        a = [w for w in a if not markup_regex.search(w)]
        t = [w for w in t if not markup_regex.search(w)]

        dash = list(set([w.lower() for w in a if w.count('-')==1]))
        dash.extend(list(set([w.lower() for w in t if w.count('-')==1])))

        nodash = list(set([''.join([l for l in w if l.isalpha()]) for w in a if '-' not in w and not w.isupper()]))
        nodash.extend(list(set([w for w in t if '-' not in w and not w.isupper()])))
        nodash = [n.lower() for n in nodash]

        acr = list(set([w for w in a if w.isupper() and w.isalpha()]))
        acr.extend(list(set([w for w in t if w.isupper() and w.isalpha()])))

        nodash = [''.join([l for l in w if l.isalpha()]) for w in nodash]
        nodash = [n for n in nodash if n not in sw and n]

        # now adding these three lists to their respective freq dict

        # we stem non dashed, non acronyms
        for n in nodash:
            s = stemword(n)
            if s in token_freq_dict:
                token_freq_dict[s][n] = token_freq_dict[s].get(n, 0) + 1
            else:
                token_freq_dict[s] = {n:1}

        for a in acr:
            if a in acr_freq_dict:
                acr_freq_dict[a]['total_occurences']+=1
            else:
                acr_freq_dict[a]={'total_occurences':1}

        # stemming individual components of dashed words and adding them to regular token dict
        for d in dash:
            # creating a stemmed representation
            s = ''.join([stemword(f) for f in d.split('-')])
            if s in token_freq_dict:
                token_freq_dict[s][d] = token_freq_dict[s].get(d, 0) +1
            else:
                token_freq_dict[s] = {d:1}

    # calling process entry on each doc entry
    for d in docs:
        process_entry(d.get('abstract','') + ' ' + d.get('title',[''])[0], '')

    # keeping only stuff in token_freq_dict that appears > MIN_PERCENT_WORD and > MIN_OCCURENCES
    # creating a new dict with the most common incarnation of the token, and the total # of times
    # related stemmed words appeared
    temp_dict = {}
    for t in token_freq_dict:
        most_common_t_list = sorted(token_freq_dict[t].items(), key=lambda x:x[1], reverse=True)
        most_common_t_list = [x for x in most_common_t_list if x[1]==most_common_t_list[0][1]]
        for c in most_common_t_list:
            # if there's a hyphenated version, we choose that
            if '-' in c[0]:
                most_common_t = c[0]
                break
        # otherwise, whatever's shortest
        else:
            most_common_t = sorted(most_common_t_list, key=lambda x:len(x[0]))[0][0]
        num = sum(token_freq_dict[t].values())
        if num/num_records>= MIN_PERCENT_WORD and num > MIN_OCCURENCES_OF_WORD:
            temp_dict[most_common_t] = {'total_occurences':num}

    token_freq_dict = temp_dict

    # now attaching tf/idf of most common example of token to the token_freq_dict
    for t in token_freq_dict:
        term = t.replace('-','')
        token_freq_dict[t]['idf'] = idf_info.get(term,0)

    # now attaching tf/idf of most common example of acronym to acr_freq_dict
    for t in acr_freq_dict:
        term = 'acr::' + t.lower()
        acr_freq_dict[t]['idf'] = idf_info.get(term,0)

    #now also making sure acr_freq_dict only has words that appeared > MIN_PERCENT_WORD times
    temp_dict = {}

    for a in acr_freq_dict:
        if acr_freq_dict[a]['total_occurences']/num_records>= MIN_PERCENT_WORD and acr_freq_dict[a]['total_occurences'] > MIN_OCCURENCES_OF_WORD:
            temp_dict[a]=acr_freq_dict[a]
    acr_freq_dict = temp_dict
 
    token_freq_dict.update(acr_freq_dict)

    return token_freq_dict
