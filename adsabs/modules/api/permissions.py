'''
Created on Nov 15, 2012

@author: jluker
'''

from flask.ext.login import current_user #@UnresolvedImport

from .errors import ApiPermissionError

class DevPermissions(object):
    
    def __init__(self, perms):
        self.perms = perms
        
    def check_facets(self):
        assert self.perms.get('facets', False), 'facets disabled'
        
    def check_max_rows(self, req_max_rows):
        max_rows = self.perms.get('max_rows', 0)
        assert max_rows >= req_max_rows, 'maximum rows allowed is %d' % max_rows
                   
    def check_max_start(self, req_max_start):
        max_start = self.perms.get('max_start', 0)
        assert max_start >= req_max_start, 'maximum start allowed is %d' % max_start
                   
    def check_permissions(self, form):
        
        try:
            if form.facets.data:
                self.check_facets(form.facets.data)
            self.check_max_rows(form.rows.data)
            self.check_max_start(form.start.data)
        except AssertionError, e:
            raise ApiPermissionError(e.message)
        
        return True
    