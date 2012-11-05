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
from config import config

class APITestCase(unittest.TestCase):

    def setUp(self):
        config.TESTING = True
        config.MONGOALCHEMY_DATABASE = 'test'
        app = create_app(config)
        
        # insert fake api user
        from adsabs.extensions import mongodb
        mongodb.session.db.connection.drop_database('test')
        mongodb.session.db.ads_users.insert({
            "username": "jluker",
            "myads_id": "bar",
            "developer_key": "baz",
            "developer_level": 3,
            "cookie_id": "foo",
            "developer": True
        })
        
        self.app = app.test_client()

    def tearDown(self):
        pass

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
        
        rv = self.app.get('/api/search/?q=black+holes&dev_key=baz')
        self.assertEqual(rv.status_code, 200)
        
        rv = self.app.get('/api/record/1234?dev_key=baz')
        self.assertEqual(rv.status_code, 404)
        
    def test_search_output(self):
        
        rv = self.app.get('/api/search/?q=black+holes&dev_key=baz')
        resp_data = loads(rv.data)
        self.assertIn('meta', resp_data)
        self.assertIn('results', resp_data)
        self.assertTrue(resp_data['results']['count'] > 1)
        self.assertIsInstance(resp_data['results']['docs'], list)
    
    def test_record_output(self):
        
        rv = self.app.get('/api/record/2012ApJ...759...36R?dev_key=baz')
        resp_data = loads(rv.data)
    
    def test_content_types(self):
        
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
    
    
        
if __name__ == '__main__':
    unittest.main()