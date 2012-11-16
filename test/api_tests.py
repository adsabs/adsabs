'''
Created on Nov 5, 2012

@author: jluker
'''

import os
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #@UndefinedVariable

import fixtures
import unittest2
from simplejson import loads
from werkzeug import Headers #@UnresolvedImport
from simplejson import loads

from adsabs.app import create_app
from adsabs.modules.user import AdsUser
from adsabs.core.solr import SolrResponse
from config import config
from test.utils import SolrRawQueryFixture
        
class APIBasicTests(unittest2.TestCase, fixtures.TestWithFixtures):

    def setUp(self):
        config.TESTING = True
        config.MONGOALCHEMY_DATABASE = 'test'
        app = create_app(config)
        
        from adsabs.extensions import mongodb
        mongodb.session.db.connection.drop_database('test') #@UndefinedVariable
        
        from test.utils import user_creator
        self.insert_user = user_creator()
            
        self.client = app.test_client()
        
        
    def test_empty_requests(self):
        
        rv = self.client.get('/api/')
        self.assertEqual(rv.status_code, 404)
        
        rv = self.client.get('/api/search')
        self.assertEqual(rv.status_code, 301)
    
        rv = self.client.get('/api/search/')
        self.assertEqual(rv.status_code, 401)
        
        rv = self.client.get('/api/record/')
        self.assertEqual(rv.status_code, 404)
        
        
    def test_unauthorized_request(self):
        
        rv = self.client.get('/api/search/?q=black+holes')
        self.assertEqual(rv.status_code, 401)
        self.assertIn("API authentication failed: no developer token provided", rv.data)
        
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo')
        self.assertEqual(rv.status_code, 401)
        self.assertIn("API authentication failed: unknown user", rv.data)
        
        rv = self.client.get('/api/record/1234')
        self.assertEqual(rv.status_code, 401)
        
    def test_authorized_request(self):
        
        self.insert_user("foo", developer=True)
        
        fixture = self.useFixture(SolrRawQueryFixture())
        
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key')
        self.assertEqual(rv.status_code, 200)
        
#        rv = self.client.get('/api/record/1234?dev_key=foo_dev_key')
#        self.assertEqual(rv.status_code, 404)
        
#    def test_search_output(self):
#        
#        self.insert_dev_user("foo", "baz")
#        self.solr.set_data({
#            'response': {
#                'numFound': 1,
#                'docs': [],
#            }
#        })
#        rv = self.client.get('/api/search/?q=black+holes&dev_key=baz')
#        resp_data = loads(rv.data)
#        self.assertIn('meta', resp_data)
#        self.assertIn('results', resp_data)
#        self.assertTrue(resp_data['results']['count'] >= 1)
#        self.assertIsInstance(resp_data['results']['docs'], list)
    
#    def test_record_output(self):
#        
#        self.insert_user("foo", "baz")
#        
#        rv = self.client.get('/api/record/2012ApJ...759...36R?dev_key=baz')
#        resp_data = loads(rv.data)
    
    def test_content_types(self):
        
        self.insert_user("foo", developer=True)
        
        fixture = self.useFixture(SolrRawQueryFixture())
        
        # default should be json
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key')
        self.assertIn('application/json', rv.content_type)
    
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key', headers=Headers({'Accept': 'application/json'}))
        self.assertIn('application/json', rv.content_type)
    
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key', headers=Headers({'Accept': 'application/xml'}))
        self.assertIn('text/xml', rv.content_type)
    
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key&format=xml')
        self.assertIn('text/xml', rv.content_type)
        
        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo_dev_key&format=blah')
        self.assertEqual(rv.status_code, 406)
        self.assertIn('renderer does not exist', rv.data)
    
#    def test_facet_output(self):
#        
#        perms = {'facets': False}
#        self.insert_user("facets_off", "foo", perms)
#        self.solr.set_data({
#            'response': {
#                'numFound': 1,
#                'docs': [],
#                'facets': [ ('bar', 1) ]
#            }
#        })
#        
#        rv = self.client.get('/api/search/?q=black+holes&dev_key=foo&facets=true')
#        resp_data = loads(rv.data)
#        self.assertIn('facets', resp_data)
        
    def test_permissions(self):
        self.insert_user("a", "1")
        self.insert_user("b", "2")
        self.insert_user("c", "3")
        self.insert_user("d", "4")
        self.insert_user("e", "5")
        self.insert_user("f", "6")
        
    
        
if __name__ == '__main__':
    unittest2.main()