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
from adsabs.modules.user import AdsUser
from adsabs.modules.user.models import AdsUserRecord
from .errors import ApiPermissionError

__all__ = ['AdsApiUser', 'create_api_user']

PERMISSION_LEVELS = {
    "basic": {
        "max_rows": 100,
        "max_start": 10000,
        "allowed_fields": config.API_SOLR_DEFAULT_FIELDS[:],
        "facets": False,
        "highlight": False,
    },
    "devel": {
        "max_rows": 200,
        "max_start": 50000,
        "allowed_fields": config.API_SOLR_DEFAULT_FIELDS[:],
        "facets": True,
        "facet_limit_max": 100,
        "highlight": True,
        "highlight_limit_max": 4,
        "highlight_fields": config.API_SOLR_HIGHLIGHT_FIELDS[:]
    },
    "collab": {
        "max_rows": 200,
        "max_start": None,
        "allowed_fields": config.API_SOLR_DEFAULT_FIELDS[:] + config.API_SOLR_EXTRA_FIELDS[:],
        "facets": True,
        "facet_limit_max": 500,
        "highlight": True,
        "highlight_limit_max": 4,
        "highlight_fields": config.API_SOLR_HIGHLIGHT_FIELDS[:]
    }
}

# dev key hashing strategy borrowed from http://crackstation.net/hashing-security.htm
HASH_SALT_BYTES = 24
DEV_KEY_LENGTH = 16
HASH_SECTION_DELIMITER = ":"
HASH_METHOD = "sha512"

def _generate_hash(key, salt, method=HASH_METHOD):
    t_sha = hashlib.new(method)
    t_sha.update(key+salt)
    return t_sha.digest()
    
def _create_dev_key():
    chars = string.letters + string.digits
    dev_key = ''.join(choice(chars) for _ in range(DEV_KEY_LENGTH))
    return dev_key
    
def generate_dev_key_hash():
    dev_key = _create_dev_key()
    salt = base64.b64encode(os.urandom(HASH_SALT_BYTES))
    hashed = _generate_hash(dev_key, salt)
    hash_struct = HASH_SECTION_DELIMITER.join([
        HASH_METHOD,
        salt,
        base64.urlsafe_b64encode(hashed)
        ])
    return (dev_key, hash_struct)

def validate_dev_key(dev_key, hash_struct):
    try:
        method,salt,stored_hash = hash_struct.split(HASH_SECTION_DELIMITER)
        assert method == HASH_METHOD
    except (AssertionError,ValueError):
        return False
    stored_hash = base64.urlsafe_b64decode(stored_hash)
    test_hash = _generate_hash(dev_key, salt, method)
    return stored_hash == test_hash
    
def default_perms(level):
    try:
        perms = PERMISSION_LEVELS[level]
        return perms
    except KeyError:
        raise Exception("Unknown default permission level: %s" % level)

def create_api_user(ads_user, level):
    """
    promote a regular AdsUser object to an AdsApiUser
    """
    api_user = AdsApiUser(ads_user.user_rec)
    if not api_user.is_developer():
        developer_key = _create_dev_key()
        api_user.set_dev_key(developer_key)
    api_user.set_perms(level)
    return api_user
    
class AdsApiUser(AdsUser):
    
    @staticmethod
    def from_dev_key(dev_key):
        """
        function that will check if the developer key is a valid one and returns the api user object
        """
        #I retrieve the user from the local database
        user_rec = AdsUserRecord.query.filter(AdsUserRecord.developer_key==dev_key).first() #@UndefinedVariable
        if user_rec:
            return AdsApiUser(user_rec)
        return None 

    def __init__(self, user_rec):
        super(AdsApiUser, self).__init__(user_rec)
        self.perms = user_rec.developer_perms
        
    def set_dev_key(self, dev_key):
        self.user_rec.developer_key = dev_key
        self.user_rec.save()
        
    def set_perms(self, level=None, new_perms={}):
        if level:
            new_perms.update(default_perms(level).copy())
        self.user_rec.developer_perms = new_perms
        self.user_rec.save()
            
    def is_developer(self):
        return self.user_rec.developer_key and True
    
    def get_dev_key(self):
        return self.user_rec.developer_key
    
    def get_dev_perms(self):
        return self.user_rec.developer_perms
    
    def get_allowed_fields(self):
        return self.user_rec.developer_perms.get('allowed_fields',[])
    
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
    
    def _facets_ok(self, req_facets):
        assert self.perms.get('facets', False), 'facets disabled'
        
        allowed = config.API_SOLR_FACET_FIELDS.keys()
        facet_limit_max = self.perms.get('facet_limit_max', 0)
        for facet in req_facets:
            # facet value format str[:limit[:mincount]], e.g., "author:100:10"
            facet = facet.strip().split(':')
            assert facet[0] in allowed, 'disallowed facet: %s' % facet[0]
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
        req_fields = re.split('[,\s]+', req_fields.strip())
        allowed = self.perms.get('allowed_fields', [])
        for f in req_fields:
            assert f in allowed, 'disallowed field: %s' % f
                   
    def _highlight_ok(self, hl_fields):
        assert self.perms.get('highlight', False), 'highlighting disabled'
        
        allowed = self.perms.get('highlight_fields', [])
        highlight_max = self.perms.get('highlight_limit_max', 0)
        for hl in hl_fields:
            # highlight field format str[:count], e.g., "abstract:3"
            hl = hl.strip().split(':')
            assert hl[0] in allowed, 'disallowed highlight field: %s' % hl[0]
            if len(hl) > 1:
                assert highlight_max >= int(hl[1]), \
                    'highlight count %d exceeds max allowed value: %d' % (int(hl[1]), highlight_max)
        
    