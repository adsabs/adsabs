'''
Created on Nov 2, 2012

@author: jluker
'''

from adsabs.modules.search.forms import QueryForm

class ApiSearchRequest(object):
    
    def __init__(self, flask_request):
        self.flask_request = flask_request
        self.form = QueryForm(flask_request.values, csrf_enabled=False)
        
    def validate(self):
        return self.form.validate()
    
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