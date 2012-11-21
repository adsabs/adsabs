'''
Created on Nov 15, 2012

@author: jluker
'''

import re
from flask import g
from flask.ext.login import current_user #@UnresolvedImport

from config import config
from .errors import ApiPermissionError

class DevPermissions(object):
    
    @staticmethod
    def current_user_perms():
        user = g.api_user
        perms = user.get_dev_perms()
        return DevPermissions(perms)
    
    def __init__(self, perms):
        self.perms = perms
        
    def _facets_ok(self, req_facets):
        assert self.perms.get('facets', False), 'facets disabled'
        
        excluded = self.perms.get('ex_fields', [])
        facet_limit_max = self.perms.get('facet_limit_max', 0)
        for facet in req_facets:
            # facet value format str[:limit[:mincount]], e.g., "author:100:10"
            facet = facet.strip().split(':')
            assert facet[0] not in excluded, 'disallowed facet: %s' % facet[0]
            if len(facet) > 1:
                assert facet_limit_max >= int(facet[1]), \
                    'facet limit value %d exceeds max allowed value: %d' % (int(facet[1]), facet_limit_max)
        
    def _max_rows_ok(self, req_rows):
        max_rows = self.perms.get('max_rows', 0)
        assert max_rows >= req_rows, 'rows=%s exceeds max allowed value: %d' % (req_rows, max_rows)
                   
    def _max_start_ok(self, req_start):
        max_start = self.perms.get('max_start', 0)
        assert max_start >= req_start, 'start=%s exceeds max allowed value: %d' % (req_start, max_start)
    
    def _fields_ok(self, req_fields):
        req_fields = set(re.split('[,\s]+', req_fields.strip()))
        allowed = set(config.API_SOLR_FIELDS)
        excluded = set(self.perms.get('ex_fields', []))
        possible = allowed.difference(excluded)
        denied = req_fields.difference(possible)
        assert len(denied) == 0, 'disallowed fields: %s' % ','.join(denied)
                   
    def _highlight_ok(self, hl_fields):
        assert self.perms.get('highlight', False), 'highlighting disabled'
        
        excluded = self.perms.get('ex_highlight_fields', [])
        highlight_max = self.perms.get('highlight_max', 0)
        for hl in hl_fields:
            # highlight field format str[:count], e.g., "abstract:3"
            hl = hl.strip().split(':')
            assert hl[0] not in excluded, 'disallowed highlight field: %s' % hl[0]
            if len(hl) > 1:
                assert highlight_max >= int(hl[1]), \
                    'highlight count %d exceeds max allowed value: %d' % (int(hl[1]), highlight_max)
        
    def check_permissions(self, form):
        
        try:
            if len(form.facet.data):
                self._facets_ok(form.facet.data)
            self._max_rows_ok(form.rows.data)
            self._max_start_ok(form.start.data)
            if len(form.flds.data):
                self._fields_ok(form.flds.data)
            if len(form.hl.data):
                self._highlight_ok(form.hl.data)
        except AssertionError, e:
            raise ApiPermissionError(e.message)
        
        return True
    