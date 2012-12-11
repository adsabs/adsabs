'''
Created on Nov 12, 2012

@author: jluker
'''

import fixtures
from simplejson import dumps
from copy import deepcopy

from flask import g
from adsabs.modules.user import AdsUser

def user_creator():
    def func(username, developer=False, dev_perms=None):
        from adsabs.extensions import mongodb
        user_collection = mongodb.session.db.ads_users #@UndefinedVariable
        user_data = {
            "username": username + "_name",
            "myads_id": username + "_myads_id",
            "cookie_id": username + "_cookie_id",
        }
        
        if developer:
            user_data['developer_key'] = username + "_dev_key"
            
        if dev_perms:
            user_data['developer_perms'] = dev_perms
            
        user_collection.insert(user_data)
    return func
    
class GlobalApiUserFixture(fixtures.Fixture):
    
    def __init__(self, dev_key):
        self.dev_key = dev_key
        
    def set_api_user(self):
        g.api_user = AdsUser.from_dev_key(self.dev_key)
        
class SolrRawQueryFixture(fixtures.MonkeyPatch):
    
    @classmethod
    def default_response(cls):
        return deepcopy(cls.DEFAULT_RESPONSE)
    
    DEFAULT_RESPONSE = {
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
                      'bibcode': 'xyz'
                    }],
            'facets': [ ('bar', 1) ]
        }
    }
    
    def __init__(self, data=None, **kwargs):
        if data is None:
            data = self.DEFAULT_RESPONSE
        self.resp_data = data
        
        def raw(*args_, **kwargs_):
            return dumps(self.resp_data)
        
        fixtures.MonkeyPatch.__init__(self, 'solr.SearchHandler.raw', raw)
        
    def set_data(self, data):
        self.resp_data = data
        
class SolrRequestPostMP(fixtures.MonkeyPatch):
    
    def __init__(self, callback):
        fixtures.MonkeyPatch.__init__(self, 'solr.Solr._post', callback)
        