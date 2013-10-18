'''
Created on Sep 19, 2012

@author: jluker
'''

from config import config
from urllib2 import quote
from urllib import urlencode
from simplejson import dumps

from flask.ext.solrquery import solr #@UnresolvedImport

from adsabs.core.invenio import record_url
from adsabs.core.classic import abstract_url

class SolrDocument(object):
        
    def __init__(self, data):
        self.data = data
        
    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]
        return None
    
    def getattr_func(self, attr, func):
        """
        Returns an attribute after processing it with the function
        """
        data = self.__getattr__(attr)
        if data:
            return func(data)
    
    def has_coreads(self):
        """Checks if document has a list of assoc reader ids"""
        if self.reader:
            return True
        else:
            return False
    
    def has_similar(self, mlt_fields=None):
        if mlt_fields is None:
            mlt_fields = config.SOLR_MLT_FIELDS
        for field in mlt_fields:
            if field in self.data:
                return True
        return False
    
    def has_references(self):
        """Checks if references are present and returns a boolean"""
        if '[citations]' in self.data and 'num_references' in self.data['[citations]'] and \
            self.data['[citations]']['num_references'] > 0:
            return True
        return False
    
    def get_references_count(self):
        """Returns the number of references"""
        if self.has_references():
            return self.data['[citations]']['num_references']
        return 0
    
    def has_citations(self):
        """Checks if citations are present and returns a boolean"""
        if '[citations]' in self.data and 'num_citations' in self.data['[citations]'] and \
            self.data['[citations]']['num_citations'] > 0:
            return True
        return False
        
    def get_citation_count(self):
        """Returns the number of citations
           Now it is useless, but if we change the way we compute the citations this method can be pretty useful
        """
        if self.has_citations():
            return self.data['[citations]']['num_citations']
        return 0
    
    def has_toc(self):
        """Checks if abstract has a Table of contents"""
        return self.property and 'TOC' in self.property
    
    def has_assoc_list(self, list_type):
        method = getattr(self, "has_%s" % list_type)
        return method()
    
    def classic_url(self):
        return abstract_url(self.bibcode)
    
    def invenio_url(self):
        return record_url(self.recid)
    
    def invenio_marcxml_url(self):
        return record_url(self.recid, of='xm')
    
    def joined(self, field, sep=','):
        val = self.__getattr__(field)
        if type(val) is list:
            return sep.join(val)
        return val
    
    def to_json(self):
        return dumps(self.data)
        
    def get_references(self, **kwargs):
        """
        Returns the list of references
        """
        q = "references(%s:%s)" % (config.SOLR_DOCUMENT_ID_FIELD, self.data[config.SOLR_DOCUMENT_ID_FIELD])
        return solr.query(q, **kwargs)
        
    def get_citations(self, **kwargs):
        """
        Returns the list of citations
        """
        q = "citations(%s:%s)" % (config.SOLR_DOCUMENT_ID_FIELD, self.data[config.SOLR_DOCUMENT_ID_FIELD])
        return solr.query(q, **kwargs)
    
    def get_toc(self, **kwargs):
        """
        Returns the table of contents
        It queries SOLR for the first 13 characters of the bibcode and "*"
        If the 14th character is a "E" I add also this before the "*"
        """
        bibcode = self.bibcode
        if bibcode[13] == 'E':
            bibquery = bibcode[:14]
        else:
            bibquery = bibcode[:13]
        q = "bibcode:%s*" % bibquery
        return solr.query(q, **kwargs)
    
    def get_coreads(self, **kwargs):
        """returns the results of the 'trending' 2nd order operator"""
        q = "trending(%s:%s)" % (config.SOLR_DOCUMENT_ID_FIELD, self.data[config.SOLR_DOCUMENT_ID_FIELD])
        return solr.query(q, **kwargs)

    def get_similar(self, **kwargs):
        
        from adsabs.core.solr import get_document_similar
        q = "%s:%s" % (config.SOLR_DOCUMENT_ID_FIELD, self.data[config.SOLR_DOCUMENT_ID_FIELD])
        return get_document_similar(q, **kwargs)

    def has_highlights(self, field=None):
        if not self.highlights or len(self.highlights) == 0:
            return False
        if field is not None and self.highlights.get(field) is None:
            return False
        return True
    
    def get_highlights(self, field=None):
        if not self.has_highlights(field):
            return None
        if field is None:
            return self.highlights
        return self.highlights.get(field, None)
            
        
