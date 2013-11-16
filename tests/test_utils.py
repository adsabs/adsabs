'''
Created on Nov 12, 2012

@author: jluker
'''
import sys
if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

import mongobox
import atexit
import fixtures
from simplejson import dumps
from copy import deepcopy
from datetime import datetime
from mock import patch
from contextlib import contextmanager

from flask import g
from adsabs.modules.api.api_user import AdsApiUser, PERMISSION_LEVELS
from config import config
from adsabs.app import create_app

class AdsabsBaseTestCase(fixtures.TestWithFixtures, unittest.TestCase):
    
    def setUp(self):
        self.box = mongobox.MongoBox(scripting=True, auth=True)
        self.box.start()
        self.boxclient = self.box.client()
        self.boxclient['admin'].add_user('foo','bar')
        self.boxclient['admin'].authenticate('foo','bar')
        self.boxclient['test'].add_user('test','test')
        
        @atexit.register
        def cleanupMongo():
            try: self.box.stop()
            except: pass
        
        config.TESTING = True
        config.MONGOALCHEMY_SERVER = 'localhost'
        config.MONGOALCHEMY_PORT = self.box.port
        config.MONGOALCHEMY_DATABASE = 'test'
        config.MONGOALCHEMY_USER = 'test'
        config.MONGOALCHEMY_PASSWORD = 'test'
        config.LOGGING_LOG_LEVEL = 'WARN'
        config.CSRF_ENABLED = False
        config.DEBUG = False
        config.PRINT_DEBUG_TEMPLATE = False
        config.REDIS_ENABLE = False
        config.SECRET_KEY = 'abcd1234'
        
        try:
            self.app = create_app(config)
            self.client = self.app.test_client()
            self.insert_user = user_creator
        except:
            # otherwise exceptions in create_app could leave a ton of mongobox procs layting around
            self.box.stop()
            raise
        
    def tearDown(self):
        self.box.stop()
        
def user_creator(username, developer=False, dev_perms=None, level=None, user_data=None):
    from adsabs.extensions import mongodb
    user_collection = mongodb.session.db.ads_users #@UndefinedVariable
    if not user_data:
        user_data = {
            "username": username + "_name",
            "myads_id": username + "_myads_id",
            "cookie_id": username + "_cookie_id",
            "registered": datetime.utcnow(),
        }
        if developer:
            user_data['developer_key'] = username + "_dev_key"
            
        if dev_perms:
            user_data['developer_perms'] = dev_perms
        elif level:
            user_data['developer_perms'] = PERMISSION_LEVELS[level].copy()
        
    user_collection.insert(user_data)
    
class GlobalApiUserFixture(fixtures.Fixture):
    
    def __init__(self, dev_key):
        self.dev_key = dev_key
        
    def set_api_user(self):
        g.api_user = AdsApiUser.from_dev_key(self.dev_key)

@contextmanager
def global_api_user(dev_key):
    g.api_user = AdsApiUser.from_dev_key(dev_key)
    yield
    g.api_user = None

class FakeSolrHttpResponse(object):
    
    DEFAULT_DATA = {
             "responseHeader":{
               "status":0,
               "QTime":1,
               "params":{ "indent":"true", "wt":"json", "q":"foo"}},
             "response":{
                "numFound":13,
                "start":0,
                "docs":[ 
                        { "id": 1 }, 
                        { "id": 2 }, 
                        { "id": 3 }, 
                        { "id": 4 }, 
                        { "id": 5 }, 
                        { "id": 6 }, 
                        { "id": 7 }, 
                        { "id": 8 }, 
                        { "id": 9 }, 
                        { "id": 10 }, 
                        { "id": 11 }, 
                        { "id": 12 }, 
                        { "id": 13 }, 
            ]}}

    def __init__(self, data=None, status_code=200):
        self.status_code = status_code
        self.data = data
        if self.data is None:
            self.data = self.DEFAULT_DATA

    def json(self):
        return self.data

class CannedSolrResponse(object):
    
    DEFAULT_DATA = {
        'responseHeader': {
            'QTime': 100,
            'status': 0,
            'params': {
                'q': 'abc',
            }
        },
        'response': {
            'start': 0,
            'numFound': 1,
            'docs': [{
                      'id': '1234',
                      'bibcode': 'xyz',
                      'abstract': 'lorem ipsum'
                    }],
        },
        'facet_counts': {
            "facet_queries": {
                 "year:[2000 TO 2003]": 13,
             },
            "facet_fields": {
                "year": [ 
                    "2009", 3,
                    "2008", 5,
                ],
                "bibstem_facet": [
                    "ApJ", 10,
                    "ArXiv", 8,
                ]
            }
        },
        'highlighting': {
            "1234": {
                "abstract": [
                    "lorem <em>ipsum</em> lorem",
                ]
            }
        }
    }
    
    def __init__(self, data=None, status_code=200):
        self.status_code = status_code
        self.data = data
        if self.data is None:
            self.data = self.DEFAULT_DATA

    def json(self):
        return self.data
        
@contextmanager
def canned_solr_response_data(data=None, status_code=200):
    def fake_send(*args, **kwargs):
        return CannedSolrResponse(data, status_code)
    mocked_send = patch("flask_solrquery.requests.sessions.Session.send", fake_send)
    mocked_send.start()
    yield
    mocked_send.stop()        

class SolrNotAvailableFixture(fixtures.MonkeyPatch):
    
    def __init__(self, exc_class, exc_msg=None):
        self.exc_class = exc_class
        self.exc_msg = exc_msg
        
        def raise_ex(*args, **kwargs):
            raise self.exc_class(self.exc_msg)
        
        fixtures.MonkeyPatch.__init__(self, 'adsabs.core.solr.request.SolrRequest._get_solr_response', raise_ex)
        
class ClassicADSSignonFixture(fixtures.MonkeyPatch):
    
    DEFAULT_USER_DATA = {
         'cookie': 'abc123',
         'email': 'foo@example.com',
         'firstname': '',
         'lastname': '',
         'fullname': 'Foo|Bar',
         'loggedin': '1',
         'message': 'LOGGED_IN',
         'myadsid': '123456',
         'openurl_icon': '',
         'openurl_srv': '',
         'request': {'man_cmd': '4',
                      'man_cookie': '',
                      'man_email': 'foo@example.com',
                      'man_name': '',
                      'man_nemail': '',
                      'man_npasswd': '',
                      'man_passwd': '******',
                      'man_url': 'http://adsduo.cfa.harvard.edu',
                      'man_vpasswd': ''}
    }

    def __init__(self, user_data=None):
        if user_data is None:
            user_data = self.DEFAULT_USER_DATA
        self.user_data = user_data
        
        def get_classic_user(u, p):
            return deepcopy(self.user_data)
        
        fixtures.MonkeyPatch.__init__(self, 'adsabs.modules.user.user.get_classic_user', get_classic_user)      
        

