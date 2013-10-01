from __future__ import division
import re
import json
import copy

#title will be added later



def list_to_dict(l):
    """
    takes awkward list of list data structure returned in solr json and dictifies it
    """
    d={}
    try:
        for index, item in enumerate(l[::2]):
            key=item
            value=l[index*2+1]
            if isinstance(value, list) and value!=[]:
                d[key]=list_to_dict(value)
            else:
                if key in d:
                    d[key].append(value)
                else:
                    d[key]=[value]
    except Exception:
        pass
    return d

def solr_term_clean_up(terminfodict):
    """
    Taking care of acronym duplicates, synonym duplicates, concatenated duplicates, and inserting dashes 
    in between concatenated words. A few complications of the loops: we don't want to remove a concatenated 
    word from consideration just because it's a synonym (though we can count it for a synonym entry as well)
    Also, things are being removed so later iterations through the copy of the dict need to check that it exists
    """
    terminfodictcopy=copy.deepcopy(terminfodict)
    safe_indexes=[]
    #getting rid of ascii repeats
    for t in terminfodictcopy:
        for wordkey in terminfodictcopy[t]['abstract']:
            if wordkey[:5]!='acr::' and wordkey[:5] != 'syn::':
                try:
                    wordkey.encode('ascii')
                    #if this matches, it's not a unicode word
                    # so we skip to the next word in the abstract
                    continue
                except UnicodeEncodeError:
                    pass
                possible_dup=None
                start_offset=terminfodictcopy[t]['abstract'][wordkey]['offsets']['start'][0]
                end_offset=terminfodictcopy[t]['abstract'][wordkey]['offsets']['end'][0]
                for wordkey1 in terminfodictcopy[t]['abstract']:
                    #might be multiple instances of this word w/different offsets
                    for index, entry in enumerate(terminfodictcopy[t]['abstract'][wordkey1]['offsets']['start']):
                        if (entry==start_offset
                            and terminfodictcopy[t]['abstract'][wordkey1]['offsets']['end'][index]==end_offset
                            and wordkey1!=wordkey
                            and wordkey1[:5]!='acr::'
                            and wordkey1[:5]!='syn::'):
                            possible_dup=wordkey1
                if possible_dup:
                    try:
                        del terminfodict[t]['abstract'][possible_dup]
                    except KeyError:
                        #occasionally parsing errors mean that a component of a word (even a single letter) is given the longer
                        #offset of the word itself, which messes everything up. In addition there might be multiple 
                        #instances of this word. So we just catch the error in case it's already gone
                        pass

        #putting dashes in between concatenated words
        for wordkey in terminfodictcopy[t]['abstract']:
            if wordkey[:5]!='acr::' and wordkey[:5] != 'syn::' and wordkey in terminfodict[t]['abstract']:
                    start_offset=terminfodictcopy[t]['abstract'][wordkey]['offsets']['start'][0]
                    end_offset=terminfodictcopy[t]['abstract'][wordkey]['offsets']['end'][0]
                    substrings=[]
                    for wordkey1 in terminfodictcopy[t]['abstract']:
                        #might be multiple instances of this word
                        for index, entry in enumerate(terminfodictcopy[t]['abstract'][wordkey1]['offsets']['start']):
                            if (entry>=start_offset
                                and terminfodictcopy[t]['abstract'][wordkey1]['offsets']['end'][index]<=end_offset
                                and wordkey!=wordkey1
                                and len(wordkey)> len(wordkey1)
                                and wordkey1[:5]!='acr::'
                                and wordkey1[:5]!='syn::'
                                #finally, check to make sure it wasn't removed as an ascii duplicate
                                and wordkey1 in terminfodict[t]['abstract']):

                                substrings.append((wordkey1, entry))
                                #and lets subtract 1 point for all component words (can't delete because it 
                                #may have shown up independently elsewhere)
                                tf=terminfodict[t]['abstract'][wordkey1]['tf'][0]
                                tfidf=terminfodict[t]['abstract'][wordkey1]['tf-idf'][0]
                                new_tf=tf-1

                                terminfodict[t]['abstract'][wordkey1]['tf-idf']= [new_tf * (tfidf/tf)]
                                terminfodict[t]['abstract'][wordkey1]['tf']=[new_tf]
                                if terminfodict[t]['abstract'][wordkey1]['tf'][0]<1:
                                    del terminfodict[t]['abstract'][wordkey1]                     
                    
                    substrings=sorted(substrings, key=lambda x: x[1])
                    #if we found substrings we can be confident this is a concatenated word
                    #we will replace its listing with a dashed word in the terminfodict
                    # we say >1 rather than >0 because parsing errors sometimes screw up offset info
                    if len(substrings)>1:
                        new_combined_word='-'.join([x[0] for x in substrings])
                        data=terminfodictcopy[t]['abstract'][wordkey]
                        del terminfodict[t]['abstract'][wordkey]
                        terminfodict[t]['abstract'][new_combined_word]=data
                        safe_indexes.extend([start_offset])
                
        #flagging synonyms so words don't get double-counted 
        for wordkey in terminfodictcopy[t]['abstract']:
            if wordkey[:5]=='syn::':
                #find offset so you can get rid of individual words with this synonym
                start_offsets= terminfodictcopy[t]['abstract'][wordkey]['offsets']['start']
                for other_word in terminfodictcopy[t]['abstract']:
                    for offset in terminfodictcopy[t]['abstract'][other_word]['offsets']['start']:
                        if (offset in start_offsets
                            and other_word[:5]!='syn::'
                            and other_word[:5]!='acr::'
                            and terminfodictcopy[t]['abstract'][other_word]['offsets']['start'] not in safe_indexes
                            and other_word in terminfodict[t]['abstract']):
                            #flag it
                            terminfodict[t]['abstract'][other_word]['dontcount']=True
                            safe_indexes.extend(start_offsets)

        #making sure that only acronyms, not their tokenized counterparts, are counted
        for wordkey in terminfodictcopy[t]['abstract']:
            if wordkey[:5]=='acr::':
                #first, weight it a bit
                terminfodict[t]['abstract'][wordkey]['tf-idf'][0]*=2
                start_offsets=terminfodictcopy[t]['abstract'][wordkey]['offsets']['start']
                #find at least 1, possibly more, other words with same offset, and delete them
                for other_word in terminfodictcopy[t]['abstract']:
                    for offset in terminfodictcopy[t]['abstract'][other_word]['offsets']['start']:
                        if (offset in start_offsets
                            and other_word[:5]!='syn::'
                            and other_word[:5]!='acr::'
                            and terminfodictcopy[t]['abstract'][other_word]['offsets']['start'] not in safe_indexes
                            and 'dontcount' not in terminfodictcopy[t]['abstract'][other_word]
                            and other_word in terminfodict[t]['abstract']):
                            terminfodict[t]['abstract'][other_word]['dontcount']=True
                            safe_indexes.extend(start_offsets)
    return terminfodict


def delete_unwanted_words(terminfodict):
    """
    culling unwanted words
    """
    terminfodictcopy=copy.deepcopy(terminfodict)

    for t in terminfodictcopy:
        for wordkey in terminfodictcopy[t]['abstract']:
            if terminfodict[t]['abstract'][wordkey]['df'][0]<5:
                terminfodict[t]['abstract'][wordkey]['dontcount']=True
            elif (re.search(r'(.*sub.*sub)|(.*sup.*sup)', wordkey, flags=re.I)
                or re.search(r'(^sub$)|(^sup$)', wordkey.strip(), flags=re.I)):
                terminfodict[t]['abstract'][wordkey]['dontcount']=True
            elif len(wordkey)<3 or ('::' in wordkey and len(wordkey[5:])<2):
                terminfodict[t]['abstract'][wordkey]['dontcount']=True
            elif re.search(r'^\d+$', ''.join([w for w in wordkey if w.isalnum()])):
                terminfodict[t]['abstract'][wordkey]['dontcount']=True
            elif '-' in wordkey and len(''.join([w for w in wordkey if w.isalnum()]))<4:
                terminfodict[t]['abstract'][wordkey]['dontcount']=True
            elif wordkey=='deg' or 'degree' in wordkey or wordkey=='syn::deg' or wordkey=='syn::degree' :
                terminfodict[t]['abstract'][wordkey]['dontcount']=True
            elif re.search(r'acr::sup|acr::sub', wordkey, flags=re.I):
                terminfodict[t]['abstract'][wordkey]['dontcount']=True   

    return terminfodict


def initialize_final_frequency_dict(terminfodict):
    finalfrequencydict={}

    terminfodictcopy=copy.deepcopy(terminfodict)
    #finally, lets see how many abstracts each word appeared in
    abstract_prevalence={}
    total_num_abstracts=len(terminfodict)

    for t in terminfodictcopy:
        for wordkey in terminfodictcopy[t]['abstract']:
            abstract_prevalence[wordkey]=abstract_prevalence.get(wordkey, 0)+1

    #calculating tf-idf for each word
    for t in terminfodictcopy:
        for wordkey in terminfodictcopy[t]['abstract']:
            if 'dontcount' not in terminfodictcopy[t]['abstract'][wordkey]:
                #cutting off tf of words that appear a bunch of times in a single abstract
                #also ignoring words that only occur in one abstract (<.005 times)
                if abstract_prevalence[wordkey]/total_num_abstracts<=.005:
                    continue
                tfidf=finalfrequencydict.get(wordkey, 0)
                if terminfodict[t]['abstract'][wordkey]['tf']<3:
                    tfidf+=terminfodict[t]['abstract'][wordkey]['tf-idf'][0]
                else:
                    tfidf+=(terminfodict[t]['abstract'][wordkey]['tf-idf'][0]/terminfodict[t]['abstract'][wordkey]['tf'][0])*3      
                finalfrequencydict[wordkey]=tfidf

    #penalizing concatenated words since they have a way higher idf
    for f in finalfrequencydict.copy():
        if f.count('-')==1:
            finalfrequencydict[f]=finalfrequencydict[f] *0.35
        elif f.count('-')>1:
            finalfrequencydict[f]=finalfrequencydict[f] *0.0025
        #bad parsing sometimes gets stuff like "subject headings: planets"
        if 'headings' in f:
            del finalfrequencydict[f]
    return dict(sorted(finalfrequencydict.items(), key=lambda x:x[1], reverse=True)[:100])


def post_process(finalfrequencydict, terminfodict):
    """
    finding a better word to represent synonyms by using the most common original word across doc entries
    and capitalizing acronyms
    """
    terminfodictcopy=copy.deepcopy(terminfodict)
    for f in finalfrequencydict.copy():
        if f[:5]=='syn::':
            syn_dict={}
            for t in terminfodictcopy:
                for wordkey in terminfodictcopy[t]['abstract']:
                #check to see if this synonym is in this doc
                    if f==wordkey:
                        #find its start offset so we can locate alternatives
                        start_offsets= terminfodictcopy[t]['abstract'][wordkey]['offsets']['start']
                        for other_word in terminfodictcopy[t]['abstract']:
                            #if it matches, it is one of the synonyms or the synonym itself
                            for i, entry in enumerate(terminfodictcopy[t]['abstract'][other_word]['offsets']['start']):
                                if (entry in start_offsets
                                    and other_word[:5]!='syn::'
                                    and other_word[:5]!='acr::'
                                    #let's not let the synonym be <3 letters
                                    and len(other_word)>2):
                                    syn_dict[other_word]=syn_dict.get(other_word, 0) + \
                                    terminfodictcopy[t]['abstract'][other_word]['tf'][0]
            syn_dict_sorted=sorted(syn_dict.items(), key=lambda x: x[1], reverse=True)
            try:
                preferred_word=syn_dict_sorted[0][0]
                weight=finalfrequencydict[f]
                del finalfrequencydict[f]
                finalfrequencydict[preferred_word]=weight
            except IndexError:
                #for whatever reason, sometimes synonyms exist in the doc info but don't 
                #actually reference the real offsets (?) 
                #also sometimes we've deleted the references because they are components of concatenated words
                del finalfrequencydict[f]
        elif f[:5]=='acr::':
            newf=f[5:].upper()
            data=finalfrequencydict[f]
            del finalfrequencydict[f]
            finalfrequencydict[newf]=data

    finalfrequencydict=dict(sorted(finalfrequencydict.items(), key=lambda x:x[1], reverse=True)[:50])
    return finalfrequencydict

def wc_json(j):
    #terminfodict is a dict with keys=paper ids, values= nested dicts with tf info
    terminfodict=list_to_dict(j['termVectors'][2:])

    terminfodict=solr_term_clean_up(terminfodict)
       
    terminfodict= delete_unwanted_words(terminfodict)

    finalfrequencydict=initialize_final_frequency_dict(terminfodict)

    finalfrequencydict=post_process(finalfrequencydict, terminfodict)

    return finalfrequencydict