'''
Created on Nov 15, 2012

@author: jluker
'''

import re
import os
import string
import base64
import hashlib
from random import sample, choice

from flask import g
from flask.ext.login import current_user #@UnresolvedImport

from config import config
from .errors import ApiPermissionError

PERMISSION_LEVELS = {
    "basic": {
        "max_rows": 20,
        "max_start": 300,
        "ex_fields": ['full','reader','citations'],
        "facets": False,
        "highlights": False,
    },
    "devel": {
        "max_rows": 100,
        "max_start": 5000,
        "ex_fields": ['full','reader','citations'],
        "facets": True,
        "facet_limit_max": 100,
        "highlights": True,
        "highlight_limit_max": 3,
    },
    "collab": {},
}

# dev key hashing strategy borrowed from http://crackstation.net/hashing-security.htm
HASH_SALT_BYTES = 24
DEV_KEY_LENGTH = 16
HASH_SECTION_DELIMITER = ":"
HASH_SECTION_COUNT = 3
HASHLIB_METHOD = "sha512"

def _generate_hash(key, salt):
    t_sha = hashlib.new(HASHLIB_METHOD)
    t_sha.update(key+salt)
    return t_sha.digest()
    
def create_dev_key():
    chars = string.letters + string.digits
    dev_key = ''.join(choice(chars) for _ in range(DEV_KEY_LENGTH))
    salt = os.urandom(HASH_SALT_BYTES)
    hashed = _generate_hash(dev_key, salt)
    t_sha = hashlib.new(HASHLIB_METHOD)
    t_sha.update(dev_key+salt)
    hash_struct = HASH_SECTION_DELIMITER.join(
        HASHLIB_METHOD,
        salt,
        base64.urlsafe_b64encode(hashed)
        )
    return (dev_key, hash_struct)

def validate_dev_key(dev_key, hash_struct):
    try:
        method,salt,stored_hash = hash_struct.split(HASH_SECTION_DELIMITER)
    except ValueError:
        return False
    stored_hash = base64.urlsafe_b64decode(stored_hash)
    test_hash = _generate_hash(dev_key, salt)
    return stored_hash == test_hash
    
def create_perms(level="basic"):
    pass

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
            if len(form.fl.data):
                self._fields_ok(form.fl.data)
            if len(form.hl.data):
                self._highlight_ok(form.hl.data)
        except AssertionError, e:
            raise ApiPermissionError(e.message)
        
        return True
    