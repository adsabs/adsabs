'''
Created on Nov 2, 2012

@author: jluker
'''

from flask import g #@UnresolvedImport
from adsabs.core.solr import SolrRequest
from .forms import ApiQueryForm
from .permissions import DevPermissions
from .errors import ApiPermissionError
    
__all__ = ['ApiSearchRequest','ApiRecordRequest']

class ApiSearchRequest(object):
    
    def __init__(self, request_vals):
        self.form = ApiQueryForm(request_vals, csrf_enabled=False)
        self.perms = DevPermissions.current_user_perms()
        
    def validate(self):
        valid = self.form.validate()
        perms_ok = self.perms.check_permissions(self.form)
        return valid and perms_ok
    
    def errors(self):
        pass
    
    def create_solr_request(self):
        req = SolrRequest(self.form.q.data)
        
        if self.form.flds.data:
            req.set_fields(self.form.flds.data)
            
        if self.form.rows.data:
            req.set_rows(self.form.rows.data)
            
        if self.form.start.data:
            req.set_start(self.form.start.data)
            
        if self.form.sort.data:
            req.set_sort(self.form.sort.data)
            
        if len(self.form.facet.data):
            for facet in self.form.facet.data:
                req.add_facet(facet.split(':'))
        
        if len(self.form.hl.data):
            for hl in self.form.hl.data:
                req.add_highlight(hl.split(':'))
                
        if len(self.form.filter.data):
            for fltr in self.form.filter.data:
                req.add_filter(fltr)
                
        if self.form.hlq.data:
            req.set_hlq(self.form.hlq.data)
            
        return req
                
    def execute(self):
        solr_req = self.create_solr_request()
        self.resp = solr_req.get_response()
        return self.resp

    def query(self):
        return self.form.q.data
    
class ApiRecordRequest(ApiSearchRequest):
    
    def __init__(self, identifier, request_vals, operator=None):
        self.query_id = identifier
        self.query_op = operator
        ApiSearchRequest.__init__(self, request_vals)
        
    def execute(self):
        q = "identifier:%s" % self.query_id
        if self.query_op:
            q = "%s(%s)" % (self.query_op, q)
        solr_req = SolrRequest(q, rows=1)
        self.resp = solr_req.get_response()
        return self.resp
    