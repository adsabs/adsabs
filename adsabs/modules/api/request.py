'''
Created on Nov 2, 2012

@author: jluker
'''

from flask import g #@UnresolvedImport
from adsabs.core.solr import SolrRequest
from .forms import ApiQueryForm
from .permissions import DevPermissions
from .errors import ApiPermissionError
    
class ApiSearchRequest(object):
    
    def __init__(self, request_vals, user=None):
        self.form = ApiQueryForm(request_vals, csrf_enabled=False)
        if user:
            perms = user.get_dev_perms()
        else:
            perms = g.api_user.get_dev_perms()
        self.perms = DevPermissions(perms)
        
    def validate(self):
        return self.form.validate() and self.perms.check_permissions(self.form)
    
    def execute(self):
        solr_req = SolrRequest(
            self.form.q.data,
            facets=self.form.facets.data
            )
        self.resp = solr_req.get_response()
        return self.resp

    def fields_queried(self):
        return SolrRequest.parse_query_fields(self.form.q.data)
        
    def query(self):
        return self.form.q.data
    
    def errors(self):
        pass
    
class ApiRecordRequest(object):
    
    def __init__(self, identifier, field=None):
        self.query_id = identifier
        self.query_field = field
        
    def query(self):
        return "identifier:%s" % self.query_id
    
    def validate(self):
        return True
