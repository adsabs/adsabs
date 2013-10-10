    # -*- coding: UTF-8 -*- #
from __future__ import division
import re


##here are the variables that you can change to affect the words that appear in the word cloud
#how much to bump up acronyms
ACRONYM_WEIGHT=1
SYNONYM_WEIGHT=.75
TITLE_WEIGHT=None
#only count an abstract if it appears in a certain ratio of abstracts
#right now it's at 5%
MIN_ABSTRACT_APPEARANCE=.05
#tokens can be no shorter than this
MIN_LEN_TOKEN=2
#might want to penalize words for having dashes, since they will have higher idf
ONE_DASH_PENALTY_WEIGHT=.75
TWO_DASH_PENALTY_WEIGHT=.75
#max # of times to count a word that appears in a single abstract
INDIVIDUAL_ABSTRACT_LIMIT=3

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

def refine_json(terminfodict):
    """
    takes json, returns less json
    by culling tokens that appear fewer than MIN_ABSTRACT_APPEARANCE
    """
    abstract_prevalence={}
    total_num_abstracts=len(terminfodict)

    for t in terminfodict.keys():
        if 'abstract' not in terminfodict[t]:
            del terminfodict[t]

    for t in terminfodict:
        #building a dictionary of word frequencies on a per-abstract basis
        for wordkey in terminfodict[t]['abstract']:
            abstract_prevalence[wordkey]=abstract_prevalence.get(wordkey, 0)+1

    for t in terminfodict.keys():
        for wordkey in terminfodict[t]['abstract'].keys():
                if abstract_prevalence[wordkey]/total_num_abstracts<=MIN_ABSTRACT_APPEARANCE:
                    del terminfodict[t]['abstract'][wordkey]
                else:
                    #remove position data because we never use it
                    del terminfodict[t]['abstract'][wordkey]['positions']
    return terminfodict

def reduce_tf_for_duplicate(rec1, rec2, terminfodict, a):
    rec1_offsets = terminfodict[a]['abstract'][rec1]['offsets']
    rec2_offsets = terminfodict[a]['abstract'][rec2]['offsets']
    for o in rec2_offsets['start']:
        if o in rec1_offsets['start']:
            #catching the first time a word is altered in its tf to find
            #the idf, which we will use later
            if 'idf' not in terminfodict[a]['abstract'][rec2]:
                tf_idf=terminfodict[a]['abstract'][rec2]['tf-idf'][0]
                tf=terminfodict[a]['abstract'][rec2]['tf'][0]
                terminfodict[a]['abstract'][rec2]['idf']=[tf_idf/tf]
       
  

def find_concatenated_word_instance(wordkey, wordkey1, terminfodict, start_offsets, end_offsets, a):
    #we know wordkey1 itself fits into wordkey. Now we have to look to see if any set of offsets for wordkey1 
    #fit into wordkey. If so, how many? We need to reduce tf for wordkey1 by that amount, and completely reduce
    #wordkey's tf to 0. So for a word like  "non", which presumably only ever appears as a component word, tf
    #should always reach 0
    entries=[]
    for index1, s in enumerate(start_offsets):
        for index2, entry in enumerate(terminfodict[a]['abstract'][wordkey1]['offsets']['start']):
            if entry>=s and terminfodict[a]['abstract'][wordkey1]['offsets']['end'][index2]<=end_offsets[index1]:            
                #these are the start and end indexes of one instance of component word
                indexes=[entry,terminfodict[a]['abstract'][wordkey1]['offsets']['end'][index2]]
                entries.append(indexes)
    if entries:
        if 'idf' not in terminfodict[a]['abstract'][wordkey1] and terminfodict[a]['abstract'][wordkey1]['tf'][0]>0:
            #the tf has not been altered for this particular word
            tf_idf=terminfodict[a]['abstract'][wordkey1]['tf-idf'][0]
            tf=terminfodict[a]['abstract'][wordkey1]['tf'][0]
            terminfodict[a]['abstract'][wordkey1]['idf']=[tf_idf/tf]

        for entry in entries:
            #at least one instance of wordkey1 being a component word of wordkey
            #it's a match:
            terminfodict[a]['abstract'][wordkey1]['tf'][0]-=1
        #and removing wordkey (which looks like "staradslike") from contention
        terminfodict[a]['abstract'][wordkey]['tf-idf'][0]=0
        terminfodict[a]['abstract'][wordkey]['tf'][0]=0
        # it is confirmed that wordkey1 has at least 1 instance of being a component word of wordkey
        return wordkey1, entries[0][0]

def calculate_new_abstract_tfidfs(termrec):
    for t in termrec:
        for a in termrec[t]['abstract']:
            tf=termrec[t]['abstract'][a]['tf'][0]
            if tf<=0:
                #in this case 
                termrec[t]['abstract'][a]['tf-idf']=[0]
            else:
                #penalizing words that lost tf because they were repeats
                if 'idf' in termrec[t]['abstract'][a]:
                    new_tf=termrec[t]['abstract'][a]['tf'][0]

                    new_tf_idf=new_tf*termrec[t]['abstract'][a]['idf'][0]
                    termrec[t]['abstract'][a]['tf-idf']=[new_tf_idf]

                else:
                    #if there was no idf inserted, the tfidf does not need to
                    #be altered
                    pass
    return termrec


def solr_term_clean_up(terminfodict):
    """
    Taking care of acronym duplicates, synonym duplicates, concatenated duplicates, unicode/ascii duplicates,
    and inserting dashes in between concatenated words.
    The loops use a term's tf as a key to know whether or not it should be counted/manipulated--if another
    loop has set the tf to 0, the term should be ignored in succeeding loops from then on

    """
    #getting rid of ascii repeats
    for a in terminfodict:
        new_recs={}
        wordkeys=terminfodict[a]['abstract']
        for wordkey in wordkeys:
            if wordkey[:5]!='acr::' and wordkey[:5] != 'syn::':
                try:
                    wordkey.encode('ascii')
                    #if this matches, it's not a unicode word
                    # so we skip to the next word in the abstract
                    continue
                except UnicodeEncodeError:
                    pass

                start_offsets=terminfodict[a]['abstract'][wordkey]['offsets']['start']
                end_offsets=terminfodict[a]['abstract'][wordkey]['offsets']['end']
                for wordkey1 in wordkeys:
                    #might be multiple instances of this word w/different offsets
                    for index, entry in enumerate(terminfodict[a]['abstract'][wordkey1]['offsets']['start']):
                        if (entry in start_offsets
                            and terminfodict[a]['abstract'][wordkey1]['offsets']['end'][index]in end_offsets
                            and wordkey1!=wordkey
                            and wordkey1[:5]!='acr::'
                            and wordkey1[:5]!='syn::'):

                            reduce_tf_for_duplicate(wordkey, wordkey1, terminfodict=terminfodict, a=a)
                            #you can break out of the offset loop because this function takes
                            #care of all repeats
                            break

        for wordkey in [w for w in wordkeys if terminfodict[a]['abstract'][w]['tf'][0]!=0]:
            #anything that is a syn, acr, or has already had tf placed to zero in this loop, 
            #could be a concatenated word
            if wordkey[:5]!='syn::' and wordkey[:5]!='acr::':
                #check to see if it is a smooshed together word that should have dashes in between
                start_offsets=terminfodict[a]['abstract'][wordkey]['offsets']['start']
                end_offsets=terminfodict[a]['abstract'][wordkey]['offsets']['end']
                #we will need this info if it turns out there is a match
                wordkey_tf=terminfodict[a]['abstract'][wordkey]['tf'][0]
                wordkey_tf_idf=terminfodict[a]['abstract'][wordkey]['tf-idf'][0]
                substrings=[]
                for wordkey1 in wordkeys:
                    if (wordkey1 in wordkey and wordkey!=wordkey1):
                        pos_results=find_concatenated_word_instance(wordkey, wordkey1, terminfodict, start_offsets, end_offsets, a)
                        if pos_results:
                            substrings.append(pos_results)
                if len(substrings)>1:
                    #why if len(substrings)>1 rather than just if substrings? Because parsing errors sometimes lead to a
                    #component word having a slightly wrong offset and being picked up
                    substrings=sorted(substrings, key=lambda x: x[1])
                    #if we found substrings we can be confident this is a concatenated word
                    new_combined_word='-'.join([x[0] for x in substrings])
                    #this doesn't have an offset so it won't be touched by the ensuing two loops
                    new_recs[new_combined_word]={'tf': [wordkey_tf], 'tf-idf':[wordkey_tf_idf]}   

        for n in new_recs:
            terminfodict[a]['abstract'][n] = new_recs[n]
        # end loop through abstract

    terminfodict=calculate_new_abstract_tfidfs(terminfodict)
    return terminfodict

def initialize_final_frequency_dict(terminfodict):
    finalfrequencydict={}

    #calculating tf-idf for each word
    for t in terminfodict:
        for wordkey in terminfodict[t]['abstract']:
                #cutting off tf of words that appear a bunch of times in a single abstract
                tfidf=finalfrequencydict.get(wordkey, 0)
                if terminfodict[t]['abstract'][wordkey]['tf'][0]<=INDIVIDUAL_ABSTRACT_LIMIT:
                    tfidf+=terminfodict[t]['abstract'][wordkey]['tf-idf'][0]
                else:
                    tfidf+=(terminfodict[t]['abstract'][wordkey]['tf-idf'][0]/
                            terminfodict[t]['abstract'][wordkey]['tf'][0]*INDIVIDUAL_ABSTRACT_LIMIT)  
                if tfidf==0:
                    continue
                else:
                    finalfrequencydict[wordkey]=tfidf

    #penalizing concatenated words since they have a way higher idf
    finalfrequencykeys=finalfrequencydict.keys()
    for f in finalfrequencykeys:
        if f.count('-')==1:
            finalfrequencydict[f]*=ONE_DASH_PENALTY_WEIGHT
        elif f.count('-')>1:
            finalfrequencydict[f]*=TWO_DASH_PENALTY_WEIGHT
    return dict(sorted(finalfrequencydict.items(), key=lambda x:x[1], reverse=True))

def post_process(finalfrequencydict):
    """
    culling unwanted words
    """

    for f in finalfrequencydict.keys():       
        if (re.search(r'(.*sub.*sub)|(.*sup.*sup)', f, flags=re.I)
            or re.search(r'\bsub\b|\bsup\b', f.strip(), flags=re.I)):
            del finalfrequencydict[f]
        elif 'www' in f or 'http' in f or 'fig' in f or f=='by':
            del finalfrequencydict[f]
        elif len(f)<MIN_LEN_TOKEN or ('::' in f and len(f[5:])<MIN_LEN_TOKEN):
            del finalfrequencydict[f]
        elif re.search(r'^\d+$', ''.join([w for w in f if w.isalnum()])):
             del finalfrequencydict[f]
        elif '-' in f and len(''.join([w for w in f if w.isalnum()]))<=MIN_LEN_TOKEN:
           del finalfrequencydict[f]
        elif f=='deg' or 'degree' in f or f=='syn::deg' or f=='syn::degree' :
            del finalfrequencydict[f]
        elif re.search(r'acr::sup|acr::sub', f, flags=re.I):
            del finalfrequencydict[f]


    for f in finalfrequencydict.keys():     
        if f[:5]=='syn::':
            val=finalfrequencydict[f]
            del finalfrequencydict[f]
            finalfrequencydict[f[5:]]=val*SYNONYM_WEIGHT

        elif f[:5]=='acr::':
            newf=f[5:].upper()
            data=finalfrequencydict[f]
            del finalfrequencydict[f]
            finalfrequencydict[newf]=data*ACRONYM_WEIGHT

    #finding possible duplicates. Order of precedence goes: dash, acronym, space
    dup_dict={}
    for f in finalfrequencydict.keys():
        f_stripped=''.join([l.lower() for l in f if l.isalpha()])
        dup_dict[f_stripped]=[]

    for d in dup_dict:
        for f in finalfrequencydict.keys():
            f_stripped=''.join([l.lower() for l in f if l.isalpha()])
            if f_stripped==d:
                dup_dict[d].append(f)

    class BreakLoop(Exception):
            pass

    for key in [d for d in dup_dict if len(dup_dict[d])>1]:
        l=dup_dict[key]
        try:
            for word in l:
                if '-' in word:
                    val=0
                    for e in l:
                        val+=finalfrequencydict[e]
                        del finalfrequencydict[e]
                    finalfrequencydict[word]=val
                    raise BreakLoop
            for word in l:
                if word.isupper():
                    val=0
                    for e in l:
                        val+=finalfrequencydict[e]
                        del finalfrequencydict[e]
                    finalfrequencydict[word]=val
                    raise BreakLoop
            for word in l:
                if ' ' in word:
                    val=0
                    for e in l:
                        val+=finalfrequencydict[e]
                        del finalfrequencydict[e]
                    finalfrequencydict[word]=val
        except BreakLoop:
            pass

    finalfrequencydict=dict(sorted(finalfrequencydict.items(), key=lambda x:x[1], reverse=True)[:50])

    return finalfrequencydict


def wc_json(j):
    terminfodict=list_to_dict(j['termVectors'][2:])
    terminfodict=refine_json(terminfodict)

   # filter out entries lacking an abstract
    terminfodict = dict((k,v) for k,v in terminfodict.iteritems() if 'abstract' in v)

    terminfodict=solr_term_clean_up(terminfodict)
    finalfrequencydict=initialize_final_frequency_dict(terminfodict)
    finalfrequencydict=post_process(finalfrequencydict)
 
    return finalfrequencydict
 
