'''
Created on Nov 5, 2012

@author: jluker
'''

import os
import sys
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

from copy import deepcopy

#from adsabs.app import create_app
from config import config
from test_utils import AdsabsBaseTestCase

from flask import request
from werkzeug.datastructures import MultiDict, ImmutableMultiDict, CombinedMultiDict  #@UnresolvedImport
#from adsabs.modules.search.misc_functions import build_basicquery_components, build_singledoc_components
from adsabs.core.solr import QueryBuilderSearch, QueryBuilderSimple
from adsabs.core.solr.query_builder import create_sort_param
from adsabs.modules.search.forms import QueryForm

class SearchTestCase(AdsabsBaseTestCase):

    def setUp(self):
        super(SearchTestCase, self).setUp()
        # store a copy of these so we can restore after each test
        self.query_form_defaults = MultiDict(QueryForm.default_if_missing)
    
    def tearDown(self):
        super(SearchTestCase, self).tearDown()
        QueryForm.default_if_missing = self.query_form_defaults

class TestQueryForm(AdsabsBaseTestCase):
    
    def test_init_with_defaults_01(self):
        """ test that defaults don't override inputs"""
        with self.app.test_request_context():
            QueryForm.default_if_missing = MultiDict([('db_f', '')])
            request_values = CombinedMultiDict([ImmutableMultiDict([('q', u' author:"civano"'), ('db_f', u'astronomy')]), ImmutableMultiDict([])])
            test_query = QueryForm.init_with_defaults(request_values)
            self.assertEqual(test_query.data['db_f'], 'astronomy')
        
    def test_init_with_defaults_02(self):
        """ test that defaults don't override inputs"""
        with self.app.test_request_context():
            QueryForm.default_if_missing = MultiDict([('db_f', 'foo')])
            request_values = CombinedMultiDict([ImmutableMultiDict([('q', u' author:"civano"'), ('db_f', u'astronomy')]), ImmutableMultiDict([])])
            test_query = QueryForm.init_with_defaults(request_values)
            self.assertEqual(test_query.data['db_f'], 'astronomy')
        
    def test_init_with_defaults_03(self):
        """ test that defaults don't override inputs"""
        with self.app.test_request_context():
            QueryForm.default_if_missing = MultiDict([('db_f', 'foo')])
            request_values = CombinedMultiDict([ImmutableMultiDict([('q', u' author:"civano"'), ('db_f', u'')]), ImmutableMultiDict([])])
            test_query = QueryForm.init_with_defaults(request_values)
            self.assertEqual(test_query.data['db_f'], '')
        
    def test_init_with_defaults_04(self):
        """ test that defaults get set """
        with self.app.test_request_context():
            QueryForm.default_if_missing = MultiDict([('db_f', 'foo')])
            request_values = CombinedMultiDict([ImmutableMultiDict([('q', u' author:"civano"')]), ImmutableMultiDict([])])
            test_query = QueryForm.init_with_defaults(request_values)
            self.assertEqual(test_query.data['db_f'], 'foo')
        
class TestQueryBuilderSorting(AdsabsBaseTestCase):
    
    def test_create_sort_param_01(self):
        """no options should produce default values"""
        sort = create_sort_param()
        default_type = config.SEARCH_DEFAULT_SORT
        primary = config.SEARCH_SORT_OPTIONS_MAP[default_type]
        secondary = config.SEARCH_DEFAULT_SECONDARY_SORT
        self.assertEqual(sort, [primary,secondary])
    
    def test_create_sort_param_02(self):
        """sort type input should produce correct values from mapping"""
        for sort_type, primary in config.SEARCH_SORT_OPTIONS_MAP.items():
            sort = create_sort_param(sort_type=sort_type)
            self.assertEqual(sort, [primary, config.SEARCH_DEFAULT_SECONDARY_SORT])

    def test_create_sort_param_03(self):
        """sort direction input handled properly"""
        for sort_type, primary in config.SEARCH_SORT_OPTIONS_MAP.items():
            sort = create_sort_param(sort_type=sort_type, sort_dir='desc')
            self.assertEqual(sort, [(primary[0], 'desc'), config.SEARCH_DEFAULT_SECONDARY_SORT])
            sort = create_sort_param(sort_type=sort_type, sort_dir='asc')
            self.assertEqual(sort, [(primary[0], 'asc'), (config.SEARCH_DEFAULT_SECONDARY_SORT[0], 'asc')])
        
    def test_create_sort_param_04(self):
        """list type that doesn't appear in ABS_SORT_OPTIONS_MAP should get defaults"""
        sort = create_sort_param(list_type='foo')
        default_type = config.SEARCH_DEFAULT_SORT
        primary = config.SEARCH_SORT_OPTIONS_MAP[default_type]
        secondary = config.SEARCH_DEFAULT_SECONDARY_SORT
        self.assertEqual(sort, [primary,secondary])
        
    def test_create_sort_param_05(self):
        """list type in ABS_SORT_OPTIONS_MAP should get produce correct value"""
        for list_type, primary in config.ABS_SORT_OPTIONS_MAP.items():
            sort = create_sort_param(list_type=list_type)
            self.assertEqual(sort, [primary, config.SEARCH_DEFAULT_SECONDARY_SORT])
            
    def test_create_sort_param_06(self):
        """list type shouldn't override form input"""
        for list_type, lt_primary in config.ABS_SORT_OPTIONS_MAP.items():
            for sort_type, primary in config.SEARCH_SORT_OPTIONS_MAP.items():
                sort = create_sort_param(sort_type=sort_type, list_type=list_type)
                self.assertEqual(sort, [primary, config.SEARCH_DEFAULT_SECONDARY_SORT])
        
class BuildBasicQueryComponentsTestCase(AdsabsBaseTestCase):

    def test_only_query(self):
        """basic case"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano")'
            expected['ui_q'] = u' author:"civano"'

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)
         
    def test_query_with_default_params_01(self):
        """including database filter"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano") AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'database:"astronomy"']

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)
      
    def test_query_with_default_params_02(self):
        """including database filter (uppercase)"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=ASTRONOMY'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano") AND database:"ASTRONOMY"'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'database:"ASTRONOMY"']

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_03(self):
        """non-default database filter"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=physics'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano") AND database:"physics"'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'database:"physics"']

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)
          
    def test_query_with_default_params_04(self):
        """2nd order query"""
        with self.app.test_request_context('/search/?q=hot(galaxy+clusters)&db_f=astronomy'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'(hot(galaxy clusters)) AND database:"astronomy"'
            expected['ui_q'] = u'hot(galaxy clusters)'
            expected['ui_filters'] = [u'database:"astronomy"']

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_05(self):
        """with date range"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&month_from=12&year_from=2010'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano") AND pubdate:[2010-12-00 TO 9999-00-00] AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'pubdate:[2010-12-00 TO 9999-00-00]', u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_06(self):
        """with date range"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&month_to=12&year_to=2010'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano") AND pubdate:[0001-00-00 TO 2010-12-00] AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'pubdate:[0001-00-00 TO 2010-12-00]', u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_07(self):
        """with date range"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&month_from=09&year_from=2009&month_to=12&year_to=2010'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano") AND pubdate:[2009-09-00 TO 2010-12-00] AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'pubdate:[2009-09-00 TO 2010-12-00]', u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_08(self):
        """with date range"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&month_from=09&year_from=2009&year_to=2010'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano") AND pubdate:[2009-09-00 TO 2010-12-00] AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'pubdate:[2009-09-00 TO 2010-12-00]', u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_09(self):
        """with journal abbr fitler"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"+bibstem%3A"ApJ"&db_f=astronomy'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano" bibstem:"ApJ") AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano" bibstem:"ApJ"'
            expected['ui_filters'] = [u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_10(self):
        """with journal abbr fitler"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"+bibstem%3A"ApJ"+bibstem%3A"AJ"&db_f=astronomy'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano" bibstem:"ApJ" bibstem:"AJ") AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano" bibstem:"ApJ" bibstem:"AJ"'
            expected['ui_filters'] = [u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_11(self):
        """with journal abbr fitler (wrong syntax)"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"+bibstem%3A"ApJ%3B+AJ"&db_f=astronomy'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano" bibstem:"ApJ; AJ") AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano" bibstem:"ApJ; AJ"'
            expected['ui_filters'] = [u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_12(self):
        """with refereed property"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&prop_f=refereed'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano") AND property:"refereed" AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'property:"refereed"', u'database:"astronomy"']

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_13(self):
        """with article only property"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&article=y'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano") AND NOT property:NONARTICLE AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'database:"astronomy"']

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_14(self):
        """with facet selection"""
        with self.app.test_request_context('/search/?q=author%3A"Civano"&aut_f=0%2FComastri%2C+A&db_f=astronomy&grant_f=0%2FNASA-HQ'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'(author:"Civano") AND grant_facet_hier:"0/NASA-HQ" AND author_facet_hier:"0/Comastri, A" AND database:"astronomy"'
            expected['ui_q'] = u'author:"Civano"'
            expected['ui_filters'] = [u'grant_facet_hier:"0/NASA-HQ"',
                                    u'author_facet_hier:"0/Comastri, A"',
                                    u'database:"astronomy"']

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_15(self):
        """with facet selection"""
        with self.app.test_request_context('/search/?q=author%3A"Civano"&db_f=astronomy&aut_f=(-"1%2FCivano%2C+F%2FCivano%2C Francesca M."+AND+-"1%2FElvis%2C M%2FElvis%2C Martin")'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'(author:"Civano") AND author_facet_hier:(-"1/Civano, F/Civano, Francesca M." AND -"1/Elvis, M/Elvis, Martin") AND database:"astronomy"'
            expected['ui_q'] = u'author:"Civano"'
            expected['ui_filters'] = [u'author_facet_hier:(-"1/Civano, F/Civano, Francesca M." AND -"1/Elvis, M/Elvis, Martin")',
                                   u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_16(self):
        """with facet selection"""
        with self.app.test_request_context('/search/?q=author%3A"Civano"&db_f=astronomy&aut_f=-("1%2FCivano%2C+F%2FCivano%2C Francesca M."+OR+"1%2FElvis%2C M%2FElvis%2C Martin")'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'(author:"Civano") AND NOT author_facet_hier:("1/Civano, F/Civano, Francesca M." OR "1/Elvis, M/Elvis, Martin") AND database:"astronomy"'
            expected['ui_q'] = u'author:"Civano"'
            expected['ui_filters'] = [u'-author_facet_hier:("1/Civano, F/Civano, Francesca M." OR "1/Elvis, M/Elvis, Martin")',
                                    u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_17(self):
        """with facet selection"""
        with self.app.test_request_context('/search/?q=author%3A"Civano"&db_f=astronomy&aut_f=(-"1%2FCivano%2C+F%2FCivano%2C+Francesca+M."+AND+-"1%2FElvis%2C M%2FElvis%2C Martin")&bibgr_f=("CfA"+AND+"CXC")&grant_f=("0%2FNASA-HQ"+OR+"0%2FNASA-GSFC")'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'(author:"Civano") AND grant_facet_hier:("0/NASA-HQ" OR "0/NASA-GSFC") AND author_facet_hier:(-"1/Civano, F/Civano, Francesca M." AND -"1/Elvis, M/Elvis, Martin") AND bibgroup_facet:("CfA" AND "CXC") AND database:"astronomy"'
            expected['ui_q'] = u'author:"Civano"'
            expected['ui_filters'] = [u'grant_facet_hier:("0/NASA-HQ" OR "0/NASA-GSFC")',
                                 u'author_facet_hier:(-"1/Civano, F/Civano, Francesca M." AND -"1/Elvis, M/Elvis, Martin")',
                                 u'bibgroup_facet:("CfA" AND "CXC")',
                                 u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_18(self):
        """with facet selection"""
        with self.app.test_request_context('/search/?q=author%3A"Civano"&db_f=astronomy&aut_f=-("1%2FCivano%2C+F%2FCivano%2C+Francesca+M."+OR+"1%2FElvis%2C M%2FElvis%2C Martin")&bibgr_f=("CfA"+AND+"CXC")&grant_f=-("0%2FNASA-HQ"+OR+"0%2FNASA-GSFC")'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'(author:"Civano") AND NOT grant_facet_hier:("0/NASA-HQ" OR "0/NASA-GSFC") AND NOT author_facet_hier:("1/Civano, F/Civano, Francesca M." OR "1/Elvis, M/Elvis, Martin") AND bibgroup_facet:("CfA" AND "CXC") AND database:"astronomy"'
            expected['ui_q'] = u'author:"Civano"'
            expected['ui_filters'] = [u'-grant_facet_hier:("0/NASA-HQ" OR "0/NASA-GSFC")',
                                   u'-author_facet_hier:("1/Civano, F/Civano, Francesca M." OR "1/Elvis, M/Elvis, Martin")',
                                   u'bibgroup_facet:("CfA" AND "CXC")',
                                   u'database:"astronomy"']

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_19(self):
        """with facet selection"""
        with self.app.test_request_context('/search/?q=*&db_f=astronomy&year_f=[2000 TO 2010]'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'(*) AND year:[2000 TO 2010] AND database:"astronomy"'
            expected['ui_q'] = u'*'
            expected['ui_filters'] = [u'year:[2000 TO 2010]', 
                                   u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            self.assertEqual(QueryBuilderSearch.build(form, request.values), expected)

    def test_query_with_default_params_20(self):
        """with facet components"""
        with self.app.test_request_context('/search/facets?q=author%3A%22civano%22&aut_f=1%2FCivano%2C+F%2FCivano%2C+F.&db_f=astronomy&facet_field=templ_aut_f&facet_prefix=1/Civano,%20F/'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'(author:"civano") AND author_facet_hier:"1/Civano, F/Civano, F." AND database:"astronomy"'
            expected['facets'] = [('author_facet_hier', -1, 1, None, u'1/Civano, F/')]
            expected['facet_field_interf_id'] = u'templ_aut_f'
            expected['ui_q'] = u'author:"civano"'
            expected['ui_filters'] = [u'author_facet_hier:"1/Civano, F/Civano, F."',
                                     u'database:"astronomy"',]

            form = QueryForm.init_with_defaults(request.values)
            actual = QueryBuilderSearch.build(form, request.values, True)
            self.assertEqual(actual, expected)

    def test_query_with_default_params_21(self):
        """with different row count"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&nr=50'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano") AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'database:"astronomy"']
            expected['rows'] = "50"

            form = QueryForm.init_with_defaults(request.values)
            actual = QueryBuilderSearch.build(form, request.values)
            self.assertEqual(actual, expected)

    def test_query_with_default_params_22(self):
        """with different row count"""
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&nr=33'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'( author:"civano") AND database:"astronomy"'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'database:"astronomy"']
            expected['rows'] = "33"

            form = QueryForm.init_with_defaults(request.values)
            actual = QueryBuilderSearch.build(form, request.values)
            self.assertEqual(actual, expected)

    def test_query_with_default_params_23(self):
        """test topn operator"""
        self.maxDiff = None
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&topn=1000'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'topn(1000, (( author:"civano") AND database:"astronomy"), "score")'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'database:"astronomy"']
            expected['sort'] = [('score', 'desc'), config.SEARCH_DEFAULT_SECONDARY_SORT]

            form = QueryForm.init_with_defaults(request.values)
            actual = QueryBuilderSearch.build(form, request.values)
            self.assertEqual(actual, expected)

    def test_query_with_default_params_24(self):
        """test topn operator"""
        self.maxDiff = None
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&re_sort_type=DATE&re_sort_dir=desc&topn=1000'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'topn(1000, (( author:"civano") AND database:"astronomy"), "pubdate_sort desc")'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'database:"astronomy"']
            expected['sort'] = [('pubdate_sort', 'desc'), config.SEARCH_DEFAULT_SECONDARY_SORT]

            form = QueryForm.init_with_defaults(request.values)
            actual = QueryBuilderSearch.build(form, request.values)
            self.assertEqual(actual, expected)

    def test_query_with_default_params_25(self):
        """test topn operator"""
        self.maxDiff = None
        with self.app.test_request_context('/search/?q=+author%3A"civano"&db_f=astronomy&re_sort_type=POPULARITY&re_sort_dir=asc&topn=1000'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'topn(1000, (( author:"civano") AND database:"astronomy"), "read_count asc")'
            expected['ui_q'] = u' author:"civano"'
            expected['ui_filters'] = [u'database:"astronomy"']
            expected['sort'] = [('read_count', 'asc'),(config.SEARCH_DEFAULT_SECONDARY_SORT[0],'asc')]

            form = QueryForm.init_with_defaults(request.values)
            actual = QueryBuilderSearch.build(form, request.values)
            self.assertEqual(actual, expected)

    def test_query_with_default_params_26(self):
        """test no fulltext"""
        with self.app.test_request_context('/search/?q=civano&no_ft=1'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'(civano)'
            expected['ui_q'] = u'civano'
            expected['ui_filters'] = []
            expected['query_fields'] = config.SOLR_SEARCH_DEFAULT_QUERY_FIELDS_METADATA_ONLY

            form = QueryForm.init_with_defaults(request.values)
            actual = QueryBuilderSearch.build(form, request.values)
            self.assertEqual(actual, expected)

    def test_query_with_default_params_27(self):
        """test no fulltext"""
        with self.app.test_request_context('/search/?q=civano&no_ft=full^1.3'):
            expected = deepcopy(QueryBuilderSearch.DEFAULT_COMPONENTS)
            expected['q'] = u'(civano)'
            expected['ui_q'] = u'civano'
            expected['ui_filters'] = []
            expected['query_fields'] = u'full^1.3'

            form = QueryForm.init_with_defaults(request.values)
            actual = QueryBuilderSearch.build(form, request.values)
            self.assertEqual(actual, expected)

class buildSingledocComponentsTestCase(AdsabsBaseTestCase):
       
    def test_no_parameters_from_request(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([]), ImmutableMultiDict([])])
        expected = deepcopy(QueryBuilderSimple.DEFAULT_COMPONENTS)
        actual = QueryBuilderSimple.build(request_values)
        self.assertEqual(actual, expected)
       
    def test_re_sort(self):
        request_values = CombinedMultiDict([ImmutableMultiDict([('re_sort_type', 'RELEVANCE')]), ImmutableMultiDict([])])
        expected = deepcopy(QueryBuilderSimple.DEFAULT_COMPONENTS)
        expected['sort'] = [('score', 'desc'), config.SEARCH_DEFAULT_SECONDARY_SORT]
        actual = QueryBuilderSimple.build(request_values)
        self.assertEqual(actual, expected)
        
    def test_re_sort_and_sort_dir(self):
        
        request_values = CombinedMultiDict([ImmutableMultiDict([('re_sort_type', 'RELEVANCE'), ('re_sort_dir', 'asc')]), ImmutableMultiDict([])])
        expected = deepcopy(QueryBuilderSimple.DEFAULT_COMPONENTS)
        expected['sort'] = [('score','asc'),(config.SEARCH_DEFAULT_SECONDARY_SORT[0],'asc')]
        actual = QueryBuilderSimple.build(request_values)
        self.assertEqual(actual, expected)
           
    def test_start_page(self):
        
        request_values = CombinedMultiDict([ImmutableMultiDict([('page', '2')]), ImmutableMultiDict([])])
        expected = deepcopy(QueryBuilderSimple.DEFAULT_COMPONENTS)
        expected['start'] = str((int(request_values.get('page')) - 1) * int(config.SEARCH_DEFAULT_ROWS))
        actual = QueryBuilderSimple.build(request_values)
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()