'''
Created on Nov 5, 2012

@author: jluker
'''

import os
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #@UndefinedVariable

import fixtures
import unittest2

from adsabs.app import create_app
from config import config
from tests.utils import SolrRawQueryFixture

from flask import request
from werkzeug.datastructures import ImmutableMultiDict, CombinedMultiDict  #@UnresolvedImport
from adsabs.modules.search.misc_functions import build_basicquery_components
from adsabs.modules.search.forms import get_missing_defaults, QueryForm

class SearchTestCase(unittest2.TestCase, fixtures.TestWithFixtures):

    def setUp(self):
        config.TESTING = True
        app = create_app(config)
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_basic_search_page(self):
        rv = self.app.get('/search/')
        assert 'Query the ADS database' in rv.data
        
    def test_basic_search_results(self):
        fixture = self.useFixture(SolrRawQueryFixture())
        rv = self.app.get('/search/?q=black+holes')
        self.assertIn('1 to 1 of', rv.data)

class GetMissingDefaultsTestCase(unittest2.TestCase):
    def test_all_defaults_present_1(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('q', u' author:"civano"'), ('sort_type', u'DATE'), ('db_key', u'ASTRONOMY')]), ImmutableMultiDict([])])
        out = ImmutableMultiDict([('q', u' author:"civano"'), ('sort_type', u'DATE'), ('db_key', u'ASTRONOMY')])
        self.assertEqual(get_missing_defaults(request_values, QueryForm), out)
        
    def test_all_defaults_present_2(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('q', u' author:"civano"'), ('sort_type', u'RELEVANCE'), ('db_key', u'PHYSICS')]), ImmutableMultiDict([])])
        out = ImmutableMultiDict([('q', u' author:"civano"'), ('sort_type', u'RELEVANCE'), ('db_key', u'PHYSICS')])
        self.assertEqual(get_missing_defaults(request_values, QueryForm), out)
        
    def test_missing_database(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('q', u' author:"civano"'), ('sort_type', u'RELEVANCE')]), ImmutableMultiDict([])])
        out = ImmutableMultiDict([('q', u' author:"civano"'), ('sort_type', u'RELEVANCE'), ('db_key', u'ASTRONOMY')])
        self.assertEqual(get_missing_defaults(request_values, QueryForm), out)
        
    def test_missing_sorting(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('q', u' author:"civano"'), ('db_key', u'PHYSICS')]), ImmutableMultiDict([])])
        out = ImmutableMultiDict([('q', u' author:"civano"'), ('sort_type', u'DATE'), ('db_key', u'PHYSICS')])
        self.assertEqual(get_missing_defaults(request_values, QueryForm), out)
        


class BuildBasicQueryComponentsTestCase(unittest2.TestCase):
    def setUp(self):
        config.TESTING = True
        self.app = create_app(config)

    def tearDown(self):
        pass
    
    def test_only_query(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY'], 'sort': u'DATE', 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
        
    def test_query_with_default_params(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY'], 'sort': u'DATE', 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
        
    def test_query_non_default_params(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=PHYSICS&sort_type=CITED'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:PHYSICS'], 'sort': u'CITED', 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_query_with_second_order_operator(self):
        with self.app.test_request_context('/search/?q=galaxy+clusters&db_key=ASTRONOMY&sort_type=hot'):
            out = {'q' : u'hot(galaxy clusters)', 'filters': [u'database:ASTRONOMY'], 'sort': None, 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_query_with_date_range_1(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&month_from=12&year_from=2010'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'pubdate_sort:[20101200 TO *]'], 'sort': u'DATE', 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_query_with_date_range_2(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&month_to=12&year_to=2010'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'pubdate_sort:[* TO 20101200]'], 'sort': u'DATE', 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_query_with_date_range_3(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&month_from=09&year_from=2009&month_to=12&year_to=2010'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'pubdate_sort:[20090900 TO 20101200]'], 'sort': u'DATE', 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
       
    def test_journal_abbreviations_1(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&journal_abbr=ApJ'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'bibstem:ApJ'], 'sort': u'DATE', 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_journal_abbreviations_2(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&journal_abbr=ApJ%2C+AJ'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'bibstem:ApJ OR bibstem:AJ'], 'sort': u'DATE', 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_journal_abbreviations_wrong_separator(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&journal_abbr=ApJ%3B+AJ'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'bibstem:ApJ; AJ'], 'sort': u'DATE', 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_refereed_only(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&refereed=y'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'property:REFEREED'], 'sort': u'DATE', 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            comps = build_basicquery_components(form)
            self.assertEqual(comps, out)
            return
            
    def test_article_only(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&article=y'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'-property:NONARTICLE'], 'sort': u'DATE', 'start': None }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
    
        
if __name__ == '__main__':
    unittest2.main()