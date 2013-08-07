'''
Created on July 22, 2013

@author: ehenneken
'''
import os
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

#import fixtures
import unittest2

#from adsabs.app import create_app
#from adsabs.core import solr
from config import config
from test_utils import (AdsabsBaseTestCase)

from adsabs.modules.recommender.utils import get_recommendations

import requests

class TestRecommender(AdsabsBaseTestCase):
    def setUp(self):
        super(TestRecommender, self).setUp()
        config.SOLR_MISC_DEFAULT_PARAMS = []

    def test_recommender_server(self):
        from xmlrpclib import Server
        server = Server(config.RECOMMENDER_SERVER)
        self.assertEqual(server.recommend('foo'),'unable to establish paper vector')

    def test_recommendations_json(self):
        with self.app.test_request_context('/recommender'):
            self.app.preprocess_request()
            bibcode = '2314ADS..4305...27Q'
            format = 'json'
            data = {
                 "paper": "2314ADS..4305...27Q",
                 "recommendations": [
                          {
                           "author": "Eichhorn,+",
                           "bibcode": "2000A&AS..143...61E",
                           "title": "The NASA Astrophysics Data System: The search engine and its user interface"
                          },
                          {
                           "author": "Accomazzi,+",
                           "bibcode": "2000A&AS..143...85A",
                           "title": "The NASA Astrophysics Data System: Architecture"
                          },
                          {
                           "author": "Grant,+",
                           "bibcode": "2000A&AS..143..111G",
                           "title": "The NASA Astrophysics Data System: Data holdings"
                          },
                          {
                           "author": "Kurtz,+",
                           "bibcode": "2005JASIS..56...36K",
                           "title": "Worldwide Use and Impact of the NASA Astrophysics Data System Digital Library"
                          },
                          {
                           "author": "Henneken,+",
                           "bibcode": "2012opsa.book..253H",
                           "title": "The ADS in the Information Age - Impact on Discovery"
                          },
                          {
                           "author": "Henneken,+",
                           "bibcode": "2011ApSSP...1..125H",
                           "title": "Finding Your Literature Match - A Recommender System"
                          } 
                        ]
               }
            self.assertEqual(get_recommendations(bibcode=bibcode),data)            

