from __future__ import division
import re
import json
import copy

#title will be added later

def generate_json_from_solr_output(j):
	'''Takes solr json, returns nice json'''
	terminfodict={}
	docs=j['response']['docs']
	for i, t in enumerate(j['termVectors']):
		#get paper id--avoid lists and non-numbers and hope that what is left over is id
		if isinstance(t, unicode) and re.match(r'\d+', t):
			#termvector info is a list of word, tfidf info for a paper
			termvectorinfo=j['termVectors'][i+1][3:]
			#iterating  through paper entry--both words and list info
			for term in termvectorinfo:
				#list of just words
				words= term[0::2]
				#list of accompanying lists with tfidf info and other stuff
				#we want to turn it into a list of dicts instead of list of lists
				tfinfo= term[1::2]
				list_of_dicts=[]
				for termlist in tfinfo:
					tfinfo_dict=dict(zip(termlist[0::2], termlist[1::2]))
					#creating a dict of tfidf info for each word (in each abstract or t)
					offset_temp=tfinfo_dict['offsets']
					start_offsets=offset_temp[1::4]
					end_offsets=offset_temp[3::4]
					del tfinfo_dict['offsets']
					tfinfo_dict['offsets']={'start': start_offsets, 'end':end_offsets}
	 				list_of_dicts.append(tfinfo_dict)
	  		fullinfo=dict(zip(words, list_of_dicts))
	 		terminfodict[t]={'terminfo': fullinfo}
	return terminfodict


def wc_json(j):
	'''Takes solr-generated json and filename, returns word-cloud-ready json and saves it.
	The function works takes a number of steps: 
	1. Run generate_json_from_solr_output()
	2. Weight certain words more heavily (title words, acronyms)
	3. Cull repeat words for the acronym, synonym, ascii-unicode repeats, and concatenated word categories
	and put a dash between concatenated words. Replace ascii versions with unicode counterparts.
	4. Calculate tf-idf for words across all abstracts, cull words that don't meet certain criteria
	5. Choose a display word for synonyms, and capitalize acronyms'''

	#terminfodict will be a dict with keys=paper ids, values= dict with tf info
	terminfodict=generate_json_from_solr_output(j)
	#this dict just stores word, number info for wordcloud
	finalfrequencydict={}
	
	#Taking care of acronym duplicates, synonym duplicates, concatenated duplicates, and inserting dashes 
	# in between concatenated words. A few complications of the loops: we don't want to remove a concatenated 
	#word from consideration just  because it's a synonym (though we can count it for a synonym entry as well)
	#Also, things are being removed so later iterations through the copy of the dict need to check 
	terminfodictcopy=copy.deepcopy(terminfodict)
	for t in terminfodictcopy:
		#if something is in safe_indexes, it it is a special word and even if it has a synonym or acronym listing,
		#it should not be flagged
		safe_indexes=[]
		#getting rid of ascii repeats
		for wordkey in terminfodictcopy[t]['terminfo']:
			if wordkey[:5]!='acr::' and wordkey[:5] != 'syn::':
				try:
					wordkey.encode('ascii')
					#if this matches, it's not a unicode word
					# so we skip to the next word in the abstract
					continue
				except UnicodeEncodeError:
					pass
				possible_dup=None
				start_offset=terminfodictcopy[t]['terminfo'][wordkey]['offsets']['start'][0]
				end_offset=terminfodictcopy[t]['terminfo'][wordkey]['offsets']['end'][0]
				for wordkey1 in terminfodictcopy[t]['terminfo']:
					#might be multiple instances of this word w/different offsets
					for index, entry in enumerate(terminfodictcopy[t]['terminfo'][wordkey1]['offsets']['start']):
						if (entry==start_offset
							and terminfodictcopy[t]['terminfo'][wordkey1]['offsets']['end'][index]==end_offset
							and wordkey1!=wordkey
							and wordkey1[:5]!='acr::'
							and wordkey1[:5]!='syn::'):
							possible_dup=wordkey1
				if possible_dup:
					try:
						del terminfodict[t]['terminfo'][possible_dup]
					except KeyError:
						#occasionally parsing errors mean that a component of a word (even a single letter) is given the longer
						#offset of the word itself, which messes everything up. In addition there might be multiple instances of this word. So
						#we just catch the error in case it's already gone
						pass

		#putting dashes in between concatenated words
		for wordkey in terminfodictcopy[t]['terminfo']:
			if wordkey[:5]!='acr::' and wordkey[:5] != 'syn::' and wordkey in terminfodict[t]['terminfo']:
					start_offset=terminfodictcopy[t]['terminfo'][wordkey]['offsets']['start'][0]
					end_offset=terminfodictcopy[t]['terminfo'][wordkey]['offsets']['end'][0]
					substrings=[]
					for wordkey1 in terminfodictcopy[t]['terminfo']:
						#might be multiple instances of this word
						for index, entry in enumerate(terminfodictcopy[t]['terminfo'][wordkey1]['offsets']['start']):
							if (entry>=start_offset
								and terminfodictcopy[t]['terminfo'][wordkey1]['offsets']['end'][index]<=end_offset
								and wordkey!=wordkey1
								and len(wordkey)> len(wordkey1)
								and wordkey1[:5]!='acr::'
								and wordkey1[:5]!='syn::'
								#finally, check to make sure it wasn't removed as an ascii duplicate
								and wordkey1 in terminfodict[t]['terminfo']):
								substrings.append((wordkey1, entry))
								#and lets subtract 1 point for all component words (can't delete because it may have shown up independently elsewhere)
								terminfodict[t]['terminfo'][wordkey1]['tf-idf']= ((terminfodict[t]['terminfo'][wordkey1]['tf']-1) * 
								(terminfodict[t]['terminfo'][wordkey1]['tf-idf']/terminfodict[t]['terminfo'][wordkey1]['tf']))
								terminfodict[t]['terminfo'][wordkey1]['tf']=terminfodict[t]['terminfo'][wordkey1]['tf']-1
								if terminfodict[t]['terminfo'][wordkey1]['tf']==0:
									del terminfodict[t]['terminfo'][wordkey1]
				
					substrings=sorted(substrings, key=lambda x: x[1])
					#if we found substrings we can be confident this is a concatenated word
					#we will replace its listing with a dashed word in the terminfodict
					# we say >1 rather than >0 because parsing errors sometimes screw up offset info
					if len(substrings)>1:
						new_combined_word='-'.join([x[0] for x in substrings])
						data=terminfodictcopy[t]['terminfo'][wordkey]
						del terminfodict[t]['terminfo'][wordkey]
						terminfodict[t]['terminfo'][new_combined_word]=data
						safe_indexes.extend([start_offset])
			
		#flagging synonyms so words don't get double-counted 
		for wordkey in terminfodictcopy[t]['terminfo']:
			if wordkey[:5]=='syn::':
				#find offset so you can get rid of individual words with this synonym
			 	start_offsets= terminfodictcopy[t]['terminfo'][wordkey]['offsets']['start']
			 	for other_word in terminfodictcopy[t]['terminfo']:
			 		for offset in terminfodictcopy[t]['terminfo'][other_word]['offsets']['start']:
			 			if (offset in start_offsets
				 			and other_word[:5]!='syn::'
				 			and other_word[:5]!='acr::'
				 			and terminfodictcopy[t]['terminfo'][other_word]['offsets']['start'] not in safe_indexes
				 			and other_word in terminfodict[t]['terminfo']):
							#flag it
							terminfodict[t]['terminfo'][other_word]['dontcount']=True
							safe_indexes.extend(start_offsets)

		#making sure that only acronyms, not their tokenized counterparts, are counted
		for wordkey in terminfodictcopy[t]['terminfo']:
			if wordkey[:5]=='acr::':
				#first, weight it a bit
				terminfodict[t]['terminfo'][wordkey]['tf-idf']*=2
				start_offsets=terminfodictcopy[t]['terminfo'][wordkey]['offsets']['start']
				#find at least 1, possibly more, other words with same offset, and delete them
				for other_word in terminfodictcopy[t]['terminfo']:
					for offset in terminfodictcopy[t]['terminfo'][other_word]['offsets']['start']:
						if (offset in start_offsets
							and other_word[:5]!='syn::'
				 			and other_word[:5]!='acr::'
							and terminfodictcopy[t]['terminfo'][other_word]['offsets']['start'] not in safe_indexes
							and 'dontcount' not in terminfodictcopy[t]['terminfo'][other_word]
							and other_word in terminfodict[t]['terminfo']):
							terminfodict[t]['terminfo'][other_word]['dontcount']=True
							safe_indexes.extend(start_offsets)

	terminfodictcopy=copy.deepcopy(terminfodict)

	#culling unwanted words in several different ways
	for t in terminfodictcopy:
		for wordkey in terminfodictcopy[t]['terminfo']:
			if terminfodict[t]['terminfo'][wordkey]['df']<5:
				terminfodict[t]['terminfo'][wordkey]['dontcount']=True
			elif (re.search(r'(.*sub.*sub)|(.*sup.*sup)', wordkey, flags=re.I)
				or re.search(r'(^sub$)|(^sup$)', wordkey.strip(), flags=re.I)):
				terminfodict[t]['terminfo'][wordkey]['dontcount']=True
			elif len(wordkey)<3 or ('::' in wordkey and len(wordkey[5:])<3):
				terminfodict[t]['terminfo'][wordkey]['dontcount']=True
			elif re.search(r'^\d+$', ''.join([w for w in wordkey if w.isalnum()])):
				terminfodict[t]['terminfo'][wordkey]['dontcount']=True
			elif '-' in wordkey and len(''.join([w for w in wordkey if w.isalnum()]))<4:
				terminfodict[t]['terminfo'][wordkey]['dontcount']=True
			elif wordkey=='deg' or 'degree' in wordkey or wordkey=='syn::deg' or wordkey=='syn::degree' :
				terminfodict[t]['terminfo'][wordkey]['dontcount']=True
			elif re.search(r'acr::sup|acr::sub', wordkey, flags=re.I):
				terminfodict[t]['terminfo'][wordkey]['dontcount']=True		

	#finally, lets see how many abstracts each word appeared in
	abstract_prevalence={}
	total_num_abstracts=len(terminfodict)
	for t in terminfodictcopy:
		for wordkey in terminfodictcopy[t]['terminfo']:
			abstract_prevalence[wordkey]=abstract_prevalence.get(wordkey, 0)+1
	#calculating tf-idf for each word
	for t in terminfodict:
		for wordkey in terminfodict[t]['terminfo']:
			if 'dontcount' not in terminfodict[t]['terminfo'][wordkey]:
				#arbitrarily cutting off words that appear a bunch of times in a single abstract
				#so they don't "unfairly" influence the final count
				#also ignoring words that only occur in one abstract
				if abstract_prevalence[wordkey]/total_num_abstracts<=.005:
					terminfodict[t]['terminfo'][wordkey]['dontcount']=True
					continue
				tfidf=finalfrequencydict.get(wordkey, 0)
				if terminfodict[t]['terminfo'][wordkey]['tf']<3:
					tfidf+=terminfodict[t]['terminfo'][wordkey]['tf-idf']
				else:
					tfidf+=(terminfodict[t]['terminfo'][wordkey]['tf-idf']/terminfodict[t]['terminfo'][wordkey]['tf'])*3		
				finalfrequencydict[wordkey]=tfidf

	#penalizing concatenated words since they have a way higher idf
	for f in finalfrequencydict.copy():
		if f.count('-')==1:
			finalfrequencydict[f]=finalfrequencydict[f] *.1
		elif f.count('-')>1:
			finalfrequencydict[f]=finalfrequencydict[f] *0.00025
		#bad parsing sometimes gets stuff like "subject headings: planets"
		if 'headings' in f:
			del finalfrequencydict[f]
		
	finalfrequencydict=dict(sorted(finalfrequencydict.items(), key=lambda x:x[1], reverse=True)[:100])

	#finding a better word to represent synonyms--using the most common original word across doc entries
	for f in finalfrequencydict.copy():
		if f[:5]=='syn::':
			syn_dict={}
			for t in terminfodictcopy:
				for wordkey in terminfodictcopy[t]['terminfo']:
				#check to see if this synonym is in this doc
					if f==wordkey:
						#find its start offset so we can locate alternatives
						start_offsets= terminfodictcopy[t]['terminfo'][wordkey]['offsets']['start']
						for other_word in terminfodictcopy[t]['terminfo']:
			 				#if it matches, it is one of the synonyms or the synonym itself
			 				for i, entry in enumerate(terminfodictcopy[t]['terminfo'][other_word]['offsets']['start']):
			 					if (entry in start_offsets
				 					and other_word[:5]!='syn::'
				 					and other_word[:5]!='acr::'
				 					#let's not let the synonym be <3 letters
				 					and len(other_word)>2):
			 						syn_dict[other_word]=syn_dict.get(other_word, 0) + \
			 						terminfodictcopy[t]['terminfo'][other_word]['tf']
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
			#checking to make sure it wasn't just bad html parsing
			newf=f[5:].upper()
			data=finalfrequencydict[f]
			del finalfrequencydict[f]
			finalfrequencydict[newf]=data

	finalfrequencydict=sorted(finalfrequencydict.items(), key=lambda x:x[1], reverse=True)[:50]
	finalfrequencydict=dict(finalfrequencydict)

	return finalfrequencydict