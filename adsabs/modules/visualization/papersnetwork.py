'''
Created on Mar 4, 2014

@author: ehenneken
'''

# general module imports
import sys
import os
import time
import histeq
from numpy import mat
from numpy import zeros
from numpy import fill_diagonal
from numpy import sqrt

__all__ = ['get_papersnetwork']

# Helper functions
def _get_reference_mapping(data):
    '''
    Construct the reference dictionary for a set of bibcodes
    '''
    refdict = {}
    for doc in data:
        if 'reference' in doc:
            refdict[doc['bibcode']] = doc['reference']
    return refdict

def _get_paper_data(data):
    '''
    Extract article info from Solr data
    '''
    infodict = {}
    for doc in data:
        infodict[doc['bibcode']] = doc
    return infodict

# Main machinery
def get_papernetwork(solr_data, weighted=True, equalization=False):
    '''
    Given a list of bibcodes, this function builds the papers network based on co-citations
    If 'weighted' is true, we will normalize the co-occurence frequency with the total number
    of papers in the set, otherwise we will work with the actual co-occurence frequencies.
    If 'equalization' is true, histogram equalization will be applied to the force values in
    the network
    
    Approach: given a reference dictionary {'paper1':['a','b','c',...], 'paper2':['b','c','g',...], ...}
              we contruct a matrix [[0,1,0,1,...], [0,0,1,...], ...] where every row corresponds with
              a paper in the original paper list and each column corresponds with the papers cited by these
              papers. The paper-citation matrix R is then the transpose of this matrix. The co-occurence
              (paper-paper) matrix is then R_t*R (with R_t the transpose of R). In case we scale with weights,
              represented by a weight matrix W, the scaled co-occurence matrix is R_t*(R-W). Later on we scale
              the force between nodes with a factor proportional to the inverse square root of the product
              of the number of references in the linked nodes.
    '''
    # Get get paper list from the Solr data
    papers_list = map(lambda a: a['bibcode'], solr_data)
    number_of_papers = len(papers_list)
    # First construct the reference dictionary, and a unique list of cited papers
    reference_dictionary = _get_reference_mapping(solr_data)
    # Construct a metadata dictionary
    info_dictionary = _get_paper_data(solr_data)
    # From now on we'll only work with publications that actually have references
    papers = reference_dictionary.keys()
    # Compile a unique list of cited papers
    ref_list = list(set([ref for sublist in reference_dictionary.values() for ref in sublist]))
    # Construct the paper-citation occurence matrix R
    entries = []
    for p in papers:
        entries.append(map(lambda b: int(b), map(lambda a: a in reference_dictionary[p], ref_list)))
    R = mat(entries).T
    # Contruct the weights matrix, in case we are working with normalized strengths
    if weighted:
        weights = []
        for row in R.tolist():
            weight = float(sum(row)/float(len(papers_list)))
            weights.append(map(lambda a: a*weight, row))
        W = mat(weights)
    else:
        W = zeros(shape=R.shape)
    # Now construct the co-occurence matrix
    # In practice we don't need to fill the diagonal with zeros, because we won't be using it
    C = R.T*(R-W)
    fill_diagonal(C, 0)
    # Compile the list of links
    links = []
    link_dict = {}
    for paper1 in papers:
        for paper2 in papers:
            if paper1 != paper2:
                scale = sqrt(len(reference_dictionary[paper1])*len(reference_dictionary[paper2]))
                force = 100*C[papers.index(paper1),papers.index(paper2)] / scale
                if force > 0:
                    links.append({'source':papers.index(paper1), 'target': papers.index(paper2), 'value':int(round(force))})
                link_dict["%s\t%s"%(paper1,paper2)] = int(round(force))
    # If histogram equalization was selected, do this and replace the links list
    if equalization:
        links = []
        HE = histeq.HistEq(link_dict)
        link_dict_eq = HE.hist_eq()
        for paper1 in papers:
            for paper2 in papers:
                force = link_dict_eq["%s\t%s"%(paper1,paper2)]
                if force !=0:
                    links.append({'source':papers.index(paper1), 'target': papers.index(paper2), 'value':force})
    # Compile node information
    nodes = []
    for paper in papers:
        nodes.append({'nodeName':paper, 
                      'nodeWeight':info_dictionary[paper].get('citation_count',1),
                      'citation_count':info_dictionary[paper].get('citation_count',0),
                      'read_count':info_dictionary[paper].get('read_count',0),
                      'title':info_dictionary[paper].get('title','NA')[0],
                      'year':info_dictionary[paper].get('year','NA'),
                      'first_author':info_dictionary[paper].get('first_author','NA')
                  })
    # That's all folks!
    paper_network = {'nodes': nodes, 'links': links}
    return paper_network
                