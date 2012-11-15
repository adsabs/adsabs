'''
Created on Nov 5, 2012

@author: jluker
'''

import os
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from werkzeug import Headers #@UnresolvedImport
from simplejson import loads

from adsabs.app import create_app
from adsabs.modules.user import AdsUser
from config import config

class APIBasicTests(unittest.TestCase):

    def setUp(self):
        config.TESTING = True
        config.MONGOALCHEMY_DATABASE = 'test'
        app = create_app(config)
        
        # insert fake api user
        from adsabs.extensions import mongodb
        mongodb.session.db.connection.drop_database('test')
        self.users = mongodb.session.db.ads_users
        
        self.app = app.test_client()
        
    def insert_dev_user(self, username, dev_key, perms={}):    
        self.users.insert({
            "username": username,
            "myads_id": username,
            "developer_key": dev_key,
            "cookie_id": username,
            "developer": True,
            "developer_perm_data" : perms
        })
        return AdsUser.from_dev_key(dev_key)

    def test_empty_requests(self):
        
        rv = self.app.get('/api/')
        self.assertEqual(rv.status_code, 404)
        
        rv = self.app.get('/api/search')
        self.assertEqual(rv.status_code, 301)
    
        rv = self.app.get('/api/search/')
        self.assertEqual(rv.status_code, 401)
        
        rv = self.app.get('/api/record/')
        self.assertEqual(rv.status_code, 404)
        
        
    def test_unauthorized_request(self):
        
        rv = self.app.get('/api/search/?q=black+holes')
        self.assertEqual(rv.status_code, 401)
        self.assertIn("API authentication failed: no developer token provided", rv.data)
        
        rv = self.app.get('/api/search/?q=black+holes&dev_key=foo')
        self.assertEqual(rv.status_code, 401)
        self.assertIn("API authentication failed: unknown user", rv.data)
        
        rv = self.app.get('/api/record/1234')
        self.assertEqual(rv.status_code, 401)
        
    def test_authorized_request(self):
        
        self.insert_dev_user("foo", "baz")
        
        rv = self.app.get('/api/search/?q=black+holes&dev_key=baz')
        self.assertEqual(rv.status_code, 200)
        
        rv = self.app.get('/api/record/1234?dev_key=baz')
        self.assertEqual(rv.status_code, 404)
        
    def test_search_output(self):
        
        self.insert_dev_user("foo", "baz")
        
        rv = self.app.get('/api/search/?q=black+holes&dev_key=baz')
        resp_data = loads(rv.data)
        self.assertIn('meta', resp_data)
        self.assertIn('results', resp_data)
        self.assertTrue(resp_data['results']['count'] > 1)
        self.assertIsInstance(resp_data['results']['docs'], list)
    
    def test_record_output(self):
        
        self.insert_dev_user("foo", "baz")
        
        rv = self.app.get('/api/record/2012ApJ...759...36R?dev_key=baz')
        resp_data = loads(rv.data)
    
    def test_content_types(self):
        
        self.insert_dev_user("foo", "baz")
        
        # default should be json
        rv = self.app.get('/api/search/?q=black+holes&dev_key=baz')
        self.assertIn('application/json', rv.content_type)
    
        rv = self.app.get('/api/search/?q=black+holes&dev_key=baz', headers=Headers({'Accept': 'application/json'}))
        self.assertIn('application/json', rv.content_type)
    
        rv = self.app.get('/api/search/?q=black+holes&dev_key=baz', headers=Headers({'Accept': 'application/xml'}))
        self.assertIn('text/xml', rv.content_type)
    
        rv = self.app.get('/api/search/?q=black+holes&dev_key=baz&format=xml')
        self.assertIn('text/xml', rv.content_type)
        
        rv = self.app.get('/api/search/?q=black+holes&dev_key=baz&format=blah')
        self.assertEqual(rv.status_code, 406)
        self.assertIn('renderer does not exist', rv.data)
    
    def test_permissions(self):
        self.insert_dev_user("a", "1")
        self.insert_dev_user("b", "2")
        self.insert_dev_user("c", "3")
        self.insert_dev_user("d", "4")
        self.insert_dev_user("e", "5")
        self.insert_dev_user("f", "6")
        
    
        
if __name__ == '__main__':
    unittest.main()