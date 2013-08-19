'''
Created on Nov 5, 2012

@author: jluker
'''

import os
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

#import fixtures
import unittest2

#from adsabs.app import create_app
from config import config
from test_utils import (AdsabsBaseTestCase, SolrRawQueryFixture)

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
        request_values = CombinedMultiDict([ImmutableMultiDict([('q', u' author:"civano"'), ('db_f', u'astronomy')]), ImmutableMultiDict([])])
        out = ImmutableMultiDict([('q', u' author:"civano"'), ('db_f', u'astronomy')])
        self.assertEqual(get_missing_defaults(request_values, QueryForm), out)
        
    def test_all_defaults_present_2(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('q', u' author:"civano"'), ('db_f', u'physics')]), ImmutableMultiDict([])])
        out = ImmutableMultiDict([('q', u' author:"civano"'), ('db_f', u'physics')])
        self.assertEqual(get_missing_defaults(request_values, QueryForm), out)
        
    def test_missing_database(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('q', u' author:"civano"')]), ImmutableMultiDict([])])
        out = ImmutableMultiDict([('q', u' author:"civano"'), ('db_f', u'')])
        self.assertEqual(get_missing_defaults(request_values, QueryForm), out)
        


class BuildBasicQueryComponentsTestCase(AdsabsBaseTestCase):
    
    def test_only_query(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"'):
            out = {'q' : u'( author:"civano")', 
                   'filters': [], 
                   'ui_q': u' author:"civano"',
                   'ui_filters': [], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
        
    def test_query_with_default_params_1(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy'):
            out = {'q' : u'( author:"civano") AND database:"astronomy"', 
                   'filters': [],
                   'ui_q' : u' author:"civano"', 
                   'ui_filters': [u'database:"astronomy"'],
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
    
    def test_query_with_default_params_2(self):        
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=ASTRONOMY'):
            out = {'q' : u'( author:"civano") AND database:"ASTRONOMY"', 
                   'filters': [],
                   'ui_q' : u' author:"civano"', 
                   'ui_filters': [u'database:"ASTRONOMY"'], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
            self.assertFalse(form.validate())
        
    def test_query_non_default_params(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=physics'):
            out = {'q' : u'( author:"civano") AND database:"physics"', 
                   'filters': [], 
                   'ui_q' : u' author:"civano"', 
                   'ui_filters': [u'database:"physics"'], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
            
    def test_query_with_second_order_operator(self):
        with self.app.test_request_context('/search/?q=hot(galaxy+clusters)&db_f=astronomy'):
            out = {'q' : u'(hot(galaxy clusters)) AND database:"astronomy"', 
                   'filters': [],
                   'ui_q' : u'hot(galaxy clusters)', 
                   'ui_filters': [u'database:"astronomy"'],
                   'sort': 'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc', 
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
            
    def test_query_with_date_range_1(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&month_from=12&year_from=2010'):
            out = {'q' : u'( author:"civano") AND pubdate:[2010-12-00 TO 9999-00-00] AND database:"astronomy"', 
                   'filters': [], 
                   'ui_q' : u' author:"civano"', 
                   'ui_filters': [u'pubdate:[2010-12-00 TO 9999-00-00]', u'database:"astronomy"',], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
            
    def test_query_with_date_range_2(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&month_to=12&year_to=2010'):
            out = {'q' : u'( author:"civano") AND pubdate:[0001-00-00 TO 2010-12-00] AND database:"astronomy"', 
                   'filters': [], 
                   'ui_q' : u' author:"civano"', 
                   'ui_filters': [u'pubdate:[0001-00-00 TO 2010-12-00]', u'database:"astronomy"',], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
            
    def test_query_with_date_range_3(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&month_from=09&year_from=2009&month_to=12&year_to=2010'):
            out = {'q' : u'( author:"civano") AND pubdate:[2009-09-00 TO 2010-12-00] AND database:"astronomy"', 
                   'filters': [], 
                   'ui_q' : u' author:"civano"', 
                   'ui_filters': [u'pubdate:[2009-09-00 TO 2010-12-00]', u'database:"astronomy"',], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
            
    def test_query_with_date_range_4(self):
        self.maxDiff = None
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&month_from=09&year_from=2009&year_to=2010'):
            out = {'q' : u'( author:"civano") AND pubdate:[2009-09-00 TO 2010-12-00] AND database:"astronomy"', 
                   'filters': [],
                   'ui_q' : u' author:"civano"', 
                   'ui_filters': [u'pubdate:[2009-09-00 TO 2010-12-00]', u'database:"astronomy"',],
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
       
    def test_journal_abbreviations_1(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"+bibstem%3A"ApJ"&db_f=astronomy'):
            out = {'q' : u'( author:"civano" bibstem:"ApJ") AND database:"astronomy"', 
                   'filters': [],
                   'ui_q' : u' author:"civano" bibstem:"ApJ"', 
                   'ui_filters': [u'database:"astronomy"',], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
            
    def test_journal_abbreviations_2(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"+bibstem%3A"ApJ"+bibstem%3A"AJ"&db_f=astronomy'):
            out = {'q' : u'( author:"civano" bibstem:"ApJ" bibstem:"AJ") AND database:"astronomy"', 
                   'filters': [], 
                   'ui_q' : u' author:"civano" bibstem:"ApJ" bibstem:"AJ"', 
                   'ui_filters': [u'database:"astronomy"'], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
            
    def test_journal_abbreviations_wrong(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"+bibstem%3A"ApJ%3B+AJ"&db_f=astronomy'):
            out = {'q' : u'( author:"civano" bibstem:"ApJ; AJ") AND database:"astronomy"', 
                   'filters': [], 
                   'ui_q' : u' author:"civano" bibstem:"ApJ; AJ"', 
                   'ui_filters': [u'database:"astronomy"'], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
            
    def test_refereed_only(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&prop_f=refereed'):
            out = {'q' : u'( author:"civano") AND property:"refereed" AND database:"astronomy"', 
                   'filters': [], 
                   'ui_q' : u' author:"civano"', 
                   'ui_filters': [u'property:"refereed"', u'database:"astronomy"'], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            comps = build_basicquery_components(form, request.values)
            self.assertEqual(comps, out)
            return
            
    def test_article_only(self):
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&article=y'):
            out = {'q' : u'( author:"civano") AND NOT property:NONARTICLE AND database:"astronomy"', 
                   'filters': [],
                   'ui_q' : u' author:"civano"', 
                   'ui_filters': [u'-property:NONARTICLE', u'database:"astronomy"'],
                   'sort': u'RELEVANCE', 
                   'start': None , 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':config.SEARCH_DEFAULT_ROWS}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values), out)
    
    def test_query_with_facets_1(self):
        with self.app.test_request_context('/search/?q=author%3A"Civano"&aut_f=0%2FComastri%2C+A&db_f=astronomy&grant_f=0%2FNASA-HQ'):
            out = {'filters': [],
                    'q': u'(author:"Civano") AND grant_facet_hier:"0/NASA-HQ" AND author_facet_hier:"0/Comastri, A" AND database:"astronomy"',
                    'ui_filters': [u'grant_facet_hier:"0/NASA-HQ"',
                                   u'author_facet_hier:"0/Comastri, A"',
                                   u'database:"astronomy"'],
                    'ui_q': u'author:"Civano"',
                    'sort': u'RELEVANCE',
                    'sort_direction': 'desc',
                    'start': None,
                    'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                    'rows':config.SEARCH_DEFAULT_ROWS}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
    
    def test_query_with_facets_2(self):
        with self.app.test_request_context('/search/?q=author%3A"Civano"&db_f=astronomy&aut_f=(-"1%2FCivano%2C+F%2FCivano%2C Francesca M."+AND+-"1%2FElvis%2C M%2FElvis%2C Martin")'):
            out = {'filters': [],
                    'q': u'(author:"Civano") AND author_facet_hier:(-"1/Civano, F/Civano, Francesca M." AND -"1/Elvis, M/Elvis, Martin") AND database:"astronomy"',
                    'ui_filters': [u'author_facet_hier:(-"1/Civano, F/Civano, Francesca M." AND -"1/Elvis, M/Elvis, Martin")',
                                   u'database:"astronomy"',],
                    'ui_q': u'author:"Civano"',
                    'sort': u'RELEVANCE',
                    'sort_direction': 'desc',
                    'start': None,
                    'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                    'rows':config.SEARCH_DEFAULT_ROWS}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
     
    def test_query_with_facets_3(self):
        with self.app.test_request_context('/search/?q=author%3A"Civano"&db_f=astronomy&aut_f=-("1%2FCivano%2C+F%2FCivano%2C Francesca M."+OR+"1%2FElvis%2C M%2FElvis%2C Martin")'):
            out = {'filters': [],
                    'q': u'(author:"Civano") AND NOT author_facet_hier:("1/Civano, F/Civano, Francesca M." OR "1/Elvis, M/Elvis, Martin") AND database:"astronomy"',
                    'ui_filters': [u'-author_facet_hier:("1/Civano, F/Civano, Francesca M." OR "1/Elvis, M/Elvis, Martin")',
                                   u'database:"astronomy"',],
                    'ui_q': u'author:"Civano"',
                    'sort': u'RELEVANCE',
                    'sort_direction': 'desc',
                    'start': None,
                    'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                    'rows':config.SEARCH_DEFAULT_ROWS}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
    
    def test_query_with_facets_4(self):   
        with self.app.test_request_context('/search/?q=author%3A"Civano"&db_f=astronomy&aut_f=(-"1%2FCivano%2C+F%2FCivano%2C+Francesca+M."+AND+-"1%2FElvis%2C M%2FElvis%2C Martin")&bibgr_f=("CfA"+AND+"CXC")&grant_f=("0%2FNASA-HQ"+OR+"0%2FNASA-GSFC")'):    
            out = {'filters': [],
                    'q': u'(author:"Civano") AND grant_facet_hier:("0/NASA-HQ" OR "0/NASA-GSFC") AND author_facet_hier:(-"1/Civano, F/Civano, Francesca M." AND -"1/Elvis, M/Elvis, Martin") AND bibgroup_facet:("CfA" AND "CXC") AND database:"astronomy"',
                    'ui_filters': [u'grant_facet_hier:("0/NASA-HQ" OR "0/NASA-GSFC")',
                                u'author_facet_hier:(-"1/Civano, F/Civano, Francesca M." AND -"1/Elvis, M/Elvis, Martin")',
                                u'bibgroup_facet:("CfA" AND "CXC")',
                                u'database:"astronomy"',],
                    'ui_q': u'author:"Civano"',
                    'sort': u'RELEVANCE',
                    'sort_direction': 'desc',
                    'start': None,
                    'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                    'rows':config.SEARCH_DEFAULT_ROWS}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
        
    def test_query_with_facets_5(self):
        with self.app.test_request_context('/search/?q=author%3A"Civano"&db_f=astronomy&aut_f=-("1%2FCivano%2C+F%2FCivano%2C+Francesca+M."+OR+"1%2FElvis%2C M%2FElvis%2C Martin")&bibgr_f=("CfA"+AND+"CXC")&grant_f=-("0%2FNASA-HQ"+OR+"0%2FNASA-GSFC")'):    
            out = {'filters': [],
                    'q': u'(author:"Civano") AND NOT grant_facet_hier:("0/NASA-HQ" OR "0/NASA-GSFC") AND NOT author_facet_hier:("1/Civano, F/Civano, Francesca M." OR "1/Elvis, M/Elvis, Martin") AND bibgroup_facet:("CfA" AND "CXC") AND database:"astronomy"',
                    'ui_filters': [u'-grant_facet_hier:("0/NASA-HQ" OR "0/NASA-GSFC")',
                                  u'-author_facet_hier:("1/Civano, F/Civano, Francesca M." OR "1/Elvis, M/Elvis, Martin")',
                                  u'bibgroup_facet:("CfA" AND "CXC")',
                                  u'database:"astronomy"'],
                    'ui_q': u'author:"Civano"',
                    'sort': u'RELEVANCE',
                    'sort_direction': 'desc',
                    'start': None,
                    'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                    'rows':config.SEARCH_DEFAULT_ROWS}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
        
    def test_query_with_facets_6(self):   
        with self.app.test_request_context('/search/?q=*&db_f=astronomy&year_f=[2000 TO 2010]'):
            out = {'filters': [],
                    'q': u'(*) AND year:[2000 TO 2010] AND database:"astronomy"',
                    'ui_filters': [u'year:[2000 TO 2010]', 
                                   u'database:"astronomy"',],
                    'ui_q': u'*',
                    'sort': u'RELEVANCE',
                    'sort_direction': 'desc',
                    'start': None,
                    'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                    'rows':config.SEARCH_DEFAULT_ROWS}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
            
    def test_facets_components(self):
        self.maxDiff = None
        with self.app.test_request_context('/search/facets?q=author%3A%22civano%22&aut_f=1%2FCivano%2C+F%2FCivano%2C+F.&db_f=astronomy&facet_field=templ_aut_f&facet_prefix=1/Civano,%20F/'):
            out = {'facet_field_interf_id': u'templ_aut_f',
                     'facet_fields': [('author_facet_hier', -1, 1, None, u'1/Civano, F/')],
                     'filters': [],
                     'q': u'(author:"civano") AND author_facet_hier:"1/Civano, F/Civano, F." AND database:"astronomy"',
                     'ui_filters': [u'author_facet_hier:"1/Civano, F/Civano, F."',
                                    u'database:"astronomy"',],
                     'ui_q': u'author:"civano"',
                     'sort': u'RELEVANCE',
                     'sort_direction': 'desc',
                     'start': None,
                     'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                     'rows':config.SEARCH_DEFAULT_ROWS}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=True), out)
            self.assertNotEqual(build_basicquery_components(form, request.values), out)
    
    def test_rows_different_from_default_1(self):
        """Test for a request with a number of result to return different from the default"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&nr=50'):
            out = {'q' : u'( author:"civano") AND database:"astronomy"', 
                   'filters': [], 
                   'ui_q' : u' author:"civano"', 
                   'ui_filters': [u'database:"astronomy"'], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':u'50' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
            self.assertTrue(form.validate())
            
    def test_rows_different_from_default_2(self):
        """Test for a request with a number of result to return not valid (not allowed)"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&nr=33'):
            out = {'q' : u'( author:"civano") AND database:"astronomy"', 
                   'filters': [], 
                   'ui_q' : u' author:"civano"', 
                   'ui_filters': [u'database:"astronomy"'], 
                   'sort': u'RELEVANCE', 
                   'start': None, 
                   'sort_direction': 'desc',
                   'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                   'rows':u'33' }
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
            self.assertFalse(form.validate())
    
    def test_topn_1(self):
        """Test for a request with a number of record to return different from the default (that is all of them)"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&topn=1000'):
            out = {'q': u'topn(1000, (( author:"civano") AND database:"astronomy"))',
                    'filters': [],
                    'rows': config.SEARCH_DEFAULT_ROWS,
                    'sort': u'RELEVANCE',
                    'sort_direction': 'desc',
                    'start': None,
                    'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS,
                    'ui_filters': [u'database:"astronomy"'],
                    'ui_q': u' author:"civano"'}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
            self.assertTrue(form.validate())
            
    def test_no_fulltext_1(self):
        """Test with fulltext disabled"""
        with self.app.test_request_context('/search/?q=civano&no_ft=1'):
            out = {'q': u'(civano)',
                    'filters': [],
                    'rows': config.SEARCH_DEFAULT_ROWS,
                    'sort': u'RELEVANCE',
                    'sort_direction': 'desc',
                    'start': None,
                    'query_fields':config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS_METADATA_ONLY,
                    'ui_filters': [],
                    'ui_q': u'civano'}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
            
    def test_no_fulltext_2(self):
        """Test with fulltext disable with custom value that is used for the QF field in the SOLR request"""
        with self.app.test_request_context('/search/?q=civano&no_ft=full^1.3'):
            out = {'q': u'(civano)',
                    'filters': [],
                    'rows': config.SEARCH_DEFAULT_ROWS,
                    'sort': u'RELEVANCE',
                    'sort_direction': 'desc',
                    'start': None,
                    'query_fields': u'full^1.3',
                    'ui_filters': [],
                    'ui_q': u'civano'}
            form = QueryForm(get_missing_defaults(request.values, QueryForm), csrf_enabled=False)
            self.assertEqual(build_basicquery_components(form, request.values, facets_components=False), out)
            
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