'''
Created on Nov 1, 2012

@author: jluker
'''
from simplejson import dumps

class ApiResponse(object):
    
    @staticmethod
    def from_solr_response(solr_resp):
        results = {
            'count': solr_resp.get_count(),
            'docs': solr_resp.get_docset_data(),
            }
        #TODO: is this a good assumption?
        meta = {
            'http_status': 200,
            }
        return ApiResponse(results, meta)
        
    def __init__(self, results={}, meta={}, error=None):
        self.results = results
        self.meta = meta
        self.http_status = None
        if error:
            self.error(*error)
        
    def set_results(self, results):
        self.results = results
        
    def error(self, msg, status=400):
        self.meta['error'] = msg
        self.http_status = status
        
    def data(self):
        return {
            'meta': self.meta,
            'results': self.results
            }