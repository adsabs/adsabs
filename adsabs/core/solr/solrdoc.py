'''
Created on Sep 19, 2012

@author: jluker
'''

from config import config
from urllib2 import quote
from urllib import urlencode
from simplejson import dumps

from adsabs.core.invenio import record_url
from adsabs.core.classic import abstract_url

class SolrDocument(object):
        
    def __init__(self, data):
        self.data = data
        
    def __getattr__(self, attr):
        if attr in self.data:
            return self.data[attr]
    
    def getattr_func(self, attr, func):
        """
        Returns an attribute after processing it with the function
        """
        data = self.__getattr__(attr)
        if data:
            return func(data)
    
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
    
    def solr_url(self, wt=None):
        if wt is None:
            return config.SOLR_URL + '/select?q=id:' + quote(str(self.id))
        else:
            return self.document_url() + urlencode({'wt': wt})
        
    def to_json(self):
        return dumps(self.data)
    
