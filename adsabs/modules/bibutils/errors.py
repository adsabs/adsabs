'''
Created on Jul 16, 2013

@author: ehenneken
'''

class SolrCitationQueryError(Exception):
    pass

class SolrReferenceQueryError(Exception):
    pass

class SolrMetaDataQueryError(Exception):
    pass

class CitationHelperCannotGetResults(Exception):
    pass

class MongoQueryError(Exception):
    pass