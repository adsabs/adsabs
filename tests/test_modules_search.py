'''
Created on Nov 5, 2012

@author: jluker
'''

import os
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

import fixtures
import unittest2

from adsabs.app import create_app
from config import config
from test_utils import *

from flask import request
from werkzeug.datastructures import ImmutableMultiDict, CombinedMultiDict  #@UnresolvedImport
from adsabs.modules.search.misc_functions import build_basicquery_components, build_singledoc_components
from adsabs.modules.search.forms import get_missing_defaults, QueryForm

class SearchTestCase(AdsabsBaseTestCase):

    def test_basic_search_results(self):
        fixture = self.useFixture(SolrRawQueryFixture())
        rv = self.client.get('/search/?q=black+holes')
        self.assertIn('1 to 1 of', rv.data)

class GetMissingDefaultsTestCase(AdsabsBaseTestCase):
    
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
        


class BuildBasicQueryComponentsTestCase(AdsabsBaseTestCase):
    
    def test_only_query(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY'], 'sort': u'DATE', 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
        
    def test_query_with_default_params(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY'], 'sort': u'DATE', 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
        
    def test_query_non_default_params(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=PHYSICS&sort_type=CITED'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:PHYSICS'], 'sort': u'CITED', 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_query_with_second_order_operator(self):
        with self.app.test_request_context('/search/?q=galaxy+clusters&db_key=ASTRONOMY&sort_type=hot'):
            out = {'q' : u'hot(galaxy clusters)', 'filters': [u'database:ASTRONOMY'], 'sort': None, 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_query_with_date_range_1(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&month_from=12&year_from=2010'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'pubdate_sort:[20101200 TO *]'], 'sort': u'DATE', 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_query_with_date_range_2(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&month_to=12&year_to=2010'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'pubdate_sort:[* TO 20101200]'], 'sort': u'DATE', 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_query_with_date_range_3(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&month_from=09&year_from=2009&month_to=12&year_to=2010'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'pubdate_sort:[20090900 TO 20101200]'], 'sort': u'DATE', 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_query_with_date_range_4(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&month_from=09&year_from=2009&year_to=2010'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'pubdate_sort:[20090900 TO 20101300]'], 'sort': u'DATE', 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
       
    def test_journal_abbreviations_1(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&journal_abbr=ApJ'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'bibstem:ApJ'], 'sort': u'DATE', 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_journal_abbreviations_2(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&journal_abbr=ApJ%2C+AJ'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'bibstem:ApJ OR bibstem:AJ'], 'sort': u'DATE', 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_journal_abbreviations_wrong_separator(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&journal_abbr=ApJ%3B+AJ'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'bibstem:ApJ; AJ'], 'sort': u'DATE', 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
            
    def test_refereed_only(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&refereed=y'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'property:REFEREED'], 'sort': u'DATE', 'start': None, 'sort_direction': 'desc' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            comps = build_basicquery_components(form)
            self.assertEqual(comps, out)
            return
            
    def test_article_only(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_key=ASTRONOMY&sort_type=DATE&article=y'):
            out = {'q' : u' author:"civano"', 'filters': [u'database:ASTRONOMY', u'-property:NONARTICLE'], 'sort': u'DATE', 'start': None , 'sort_direction': 'desc'}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form), out)
    
    def test_query_with_facets(self):
        with self.app.test_request_context('/search/?q=author%3A"Civano"&aut_f=0%2FComastri%2C+A&sort_type=DATE&db_key=ASTRONOMY&grant_f=0%2FNASA-HQ'):
            out = {'filters': [u'database:ASTRONOMY',
                    u'author_facet_hier:"0/Comastri, A"',
                    u'grant_facet_hier:"0/NASA-HQ"'],
                    'q': u'author:"Civano"',
                    'sort': u'DATE',
                    'sort_direction': 'desc',
                    'start': None}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
    
    def test_query_with_facets_2(self):
        with self.app.test_request_context('/search/?q=author%3A"Civano"&sort_type=DATE&db_key=ASTRONOMY&aut_f=(-"1%2FCivano%2C+F%2FCivano%2C Francesca M."+AND+-"1%2FElvis%2C M%2FElvis%2C Martin")'):
            out = {'filters': [u'database:ASTRONOMY',
                    u'author_facet_hier:(-"1/Civano, F/Civano, Francesca M." AND -"1/Elvis, M/Elvis, Martin")'],
                    'q': u'author:"Civano"',
                    'sort': u'DATE',
                    'sort_direction': 'desc',
                    'start': None}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
            
        with self.app.test_request_context('/search/?q=author%3A"Civano"&sort_type=DATE&db_key=ASTRONOMY&aut_f=(-"1%2FCivano%2C+F%2FCivano%2C+Francesca+M."+AND+-"1%2FElvis%2C M%2FElvis%2C Martin")&bibgr_f=("CfA"+AND+"CXC")&grant_f=("0%2FNASA-HQ"+OR+"0%2FNASA-GSFC")'):    
            out = {'filters': [u'database:ASTRONOMY',
                    u'bibgroup_facet:("CfA" AND "CXC")',
                    u'author_facet_hier:(-"1/Civano, F/Civano, Francesca M." AND -"1/Elvis, M/Elvis, Martin")',
                    u'grant_facet_hier:("0/NASA-HQ" OR "0/NASA-GSFC")'],
                    'q': u'author:"Civano"',
                    'sort': u'DATE',
                    'sort_direction': 'desc',
                    'start': None}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
        with self.app.test_request_context('/search/?q=*&sort_type=DATE&db_key=ASTRONOMY&year_f=[2000 TO 2010]'):
            out = {'filters': [u'database:ASTRONOMY',
                               u'year:[2000 TO 2010]'],
                    'q': u'*',
                    'sort': u'DATE',
                    'sort_direction': 'desc',
                    'start': None}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
            
    def test_facets_components(self):
        with self.app.test_request_context('/search/facets?q=author%3A%22civano%22&aut_f=1%2FCivano%2C+F%2FCivano%2C+F.&sort_type=DATE&db_key=ASTRONOMY&facet_field=templ_aut_f&facet_prefix=1/Civano,%20F/'):
            out = {'facet_field_interf_id': u'templ_aut_f',
                     'facet_fields': [('author_facet_hier', -1, 1, None, u'1/Civano, F/')],
                     'filters': [u'database:ASTRONOMY',
                      u'author_facet_hier:"1/Civano, F/Civano, F."'],
                     'q': u'author:"civano"',
                     'sort': u'DATE',
                     'sort_direction': 'desc',
                     'start': None}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=True), out)
            self.assertNotEqual(build_basicquery_components(form, request.values), out)
    
            
class buildSingledocComponentsTestCase(AdsabsBaseTestCase):
    
    def test_no_parameters_from_request(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([])])
        out = {'sort': config.SEARCH_DEFAULT_SORT, 'start': None, 'sort_direction':config.SEARCH_DEFAULT_SORT_DIRECTION,}
        self.assertEqual(build_singledoc_components(request_values), out)
    
    def test_re_sort(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('re_sort_type', 'RELEVANCE')]), ImmutableMultiDict([])])
        out = {'sort': 'RELEVANCE', 'start': None, 'sort_direction':config.SEARCH_DEFAULT_SORT_DIRECTION,}
        self.assertEqual(build_singledoc_components(request_values), out)
    
    def test_re_sort_and_sort_dir(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('re_sort_type', 'RELEVANCE'), ('re_sort_dir', 'asc')]), ImmutableMultiDict([])])
        out = {'sort': 'RELEVANCE', 'start': None, 'sort_direction':'asc',}
        self.assertEqual(build_singledoc_components(request_values), out)
        
    def test_start_page(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('page', '2')]), ImmutableMultiDict([])])
        out = {'sort': config.SEARCH_DEFAULT_SORT, 'start': str((int(request_values.get('page')) - 1) * int(config.SEARCH_DEFAULT_ROWS)), 'sort_direction':config.SEARCH_DEFAULT_SORT_DIRECTION,}
        self.assertEqual(build_singledoc_components(request_values), out)
    
    def test_wrong_re_sort(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('re_sort_type', 'RELEvance')]), ImmutableMultiDict([])])
        out = {'sort': config.SEARCH_DEFAULT_SORT, 'start': None, 'sort_direction':config.SEARCH_DEFAULT_SORT_DIRECTION,}
        self.assertEqual(build_singledoc_components(request_values), out)
    
    def test_wrong_re_sort_and_search_dir(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('re_sort_type', 'RELEvance'), ('re_sort_dir', 'aSC')]), ImmutableMultiDict([])])
        out = {'sort': config.SEARCH_DEFAULT_SORT, 'start': None, 'sort_direction':config.SEARCH_DEFAULT_SORT_DIRECTION,}
        self.assertEqual(build_singledoc_components(request_values), out)
    
    def test_wrong_start_page(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('page', '2a')]), ImmutableMultiDict([])])
        out = {'sort': config.SEARCH_DEFAULT_SORT, 'start': None, 'sort_direction':config.SEARCH_DEFAULT_SORT_DIRECTION,}
        self.assertEqual(build_singledoc_components(request_values), out)
        
if __name__ == '__main__':
    unittest2.main()