'''
Created on Nov 1, 2012

@author: jluker
'''
from simplejson import dumps

class ApiResponse(object):
    pass

class ApiSearchResponse(ApiResponse):
    
    @staticmethod
    def from_solr_response(solr_resp):
        results = {
            'count': solr_resp.get_count(),
            'docs': solr_resp.get_docs(),
            }
        #TODO: is this a good assumption?
        meta = {
            'error': None,
            }
        return ApiSearchResponse(results, meta)
        
    def __init__(self, results={}, meta={}, error=None):
        self.results = results
        self.meta = meta
        self.http_status = None
        if error:
            self.error(*error)
        
    def set_results(self, results):
        self.results = results
        
    def set_error(self, msg):
        self.meta['error'] = msg
        
    def data(self):
        return {
            'meta': self.meta,
            'results': self.results
            }
        
class ApiRecordResponse(ApiResponse):
    
    @staticmethod
    def from_solr_response(solr_response):
        doc = solr_response.next()
        return ApiRecordResponse(doc)
        
    def __init__(self, doc):
        self.doc = doc
        
    def data(self):
        return self.doc
    
        
    pass