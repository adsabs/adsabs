from __future__ import division
from nltk import PorterStemmer
import json
import re
import os

stemmer = PorterStemmer()

sw = open(os.path.dirname(os.path.abspath(__file__)) +'/solr_stopwords.txt').read().split('\n')

# so in 250 docs, token has to appear >= 3 times
MIN_OCCURENCES_OF_WORD = 0.012


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



def wc_json(solr_json):
    tf_idf_info = list_to_dict(solr_json['termVectors'][2:])
    docs = solr_json['response']['docs']
    num_records = len(docs)
    token_freq_dict = {}
    acr_freq_dict= {}
    # these characters indicate word boundaries 
    split_regex = re.compile(r'[\s/.]+')

    markup_regex = re.compile(r'href=|<?sub>?.*?<?sub>?|<?sup>?.*?<?sup>?|\.edu|\.com|www', re.I)

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
            s = stemmer.stem(n)
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
            s = ''.join([stemmer.stem(f) for f in d.split('-')])
            if s in token_freq_dict:
                token_freq_dict[s][d] = token_freq_dict[s].get(d, 0) +1
            else:
                token_freq_dict[s] = {d:1}

    # calling process entry on each doc entry
    for d in docs:
        try:
            #for some reason titles come in lists but not abstracts
            process_entry(d['abstract'], d['title'][0])
        except KeyError:
            #missing a field, most likely abstract, so we ignore this entry
            continue

    # keeping only stuff in token_freq_dict that appears > MIN_OCCURENCES_OF_WORD % of the time
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
        if num/num_records>= MIN_OCCURENCES_OF_WORD :
            temp_dict[most_common_t] = {'total_occurences':num}

    token_freq_dict = temp_dict


    # now a function that attaches idf info to token_freq_dict
    def find_idf(term, dic, acr = False):
        if acr==True:
            search_term = 'acr::'+term.lower()
        elif '-' in term:
            search_term=term.replace('-', '')
        else:
            search_term = term
    # iterating through tf-idf json structure
        for t in tf_idf_info:
            if 'abstract' not in tf_idf_info[t]:
                continue
                # doesn't come with abstract info, so we ignore
            elif 'title' not in tf_idf_info[t]:
                # doesn't come with title info, so we ignore
                continue
            else:
                #checking abstract
                for a in tf_idf_info[t]['abstract']:
                    if a == search_term:
                        idf = tf_idf_info[t]['abstract'][a]['tf-idf'][0]/tf_idf_info[t]['abstract'][a]['tf'][0]
                        dic[term]['idf'] = idf
                        return
                #checking title
                for ti in tf_idf_info[t]['title']:
                    if ti == search_term:
                        idf = tf_idf_info[t]['title'][ti]['tf-idf'][0]/tf_idf_info[t]['title'][ti]['tf'][0]
                        dic[term]['idf'] = idf
                        return 


    # now attaching tf/idf of most common example of token to the token_freq_dict
    for t in token_freq_dict:
        find_idf(t, token_freq_dict)

    # now attaching tf/idf of most common example of acronym to acr_freq_dict
    for a in acr_freq_dict:
        find_idf(a, acr_freq_dict, acr=True)
 

    #now calculating scores
    temp_dict = {}
    for t in token_freq_dict:
        if 'idf' not in token_freq_dict[t]:
            continue
        else:
            score = token_freq_dict[t]['idf']*token_freq_dict[t]['total_occurences']
            temp_dict[t]=score

    token_freq_dict = temp_dict

    temp_dict = {}
    for a in acr_freq_dict:
        # we don't care about idf for acronyms since it is a special category
        temp_dict[a] = acr_freq_dict[a]['total_occurences']

    acr_freq_dict = temp_dict


    # now, using a little discretion to create a 50-word word cloud with a number of different types of words
    # we want a distribution of 1/5 dashed words, 1/10 acronyms, and everything else single tokens (so 10 - 5 - 35)
    # we are also changing up the values so acronyms and dashed words don't dominate

    final_dict = {}
    top_un_dashed = sorted([(k,v) for k,v in token_freq_dict.items() if '-' not in k], key = lambda x:x[1], reverse=True)[:40] 
    final_dict.update(dict(top_un_dashed))

    average_undashed_score = sum([x[1] for x in top_un_dashed])/35

    acronyms = sorted(acr_freq_dict.items(), key=lambda x:x[1], reverse=True)[:5]
    average_ac_score = sum([x[1] for x in acronyms])/5

    acronyms = [(x[0], x[1]/average_ac_score*average_undashed_score) for x in acronyms]
    final_dict.update(dict(acronyms))

    top_dashed = sorted([(k,v) for k,v in token_freq_dict.items() if '-' in k], key = lambda x:x[1], reverse=True)[:10]
    average_dashed_score = sum([x[1] for x in top_dashed])/10

    top_dashed = [(x[0], x[1]/average_dashed_score*average_undashed_score) for x in top_dashed]
    final_dict.update(dict(top_dashed))
    return final_dict