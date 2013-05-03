import os

_basedir = os.path.abspath(os.path.dirname(__file__))

APP_NAME = "adsabs"

class AppConfig(object):
    #flask Setting for debug view in case of errors
    DEBUG = False
    #Flask setting for unittest
    TESTING = False
    #prints the template in the bottom of the page with the link to SOLR
    PRINT_DEBUG_TEMPLATE = False
    
    APP_VERSION = '2013_05_01_v1'
    
    # Override in local_config.py, e.g. DEPLOYMENT_PATH = "/adsabs"
    DEPLOYMENT_PATH = None
    
    ADMINS = frozenset(['youremail@yourdomain.com'])
    SECRET_KEY = 'SecretKeyForSessionSigning'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
    DATABASE_CONNECT_OPTIONS = {}
    
    THREADS_PER_PAGE = 8

    CSRF_ENABLED=True
    CSRF_SESSION_KEY="somethingimpossibletoguess"

    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = 'blahblahblahblahblahblahblahblahblah'
    RECAPTCHA_PRIVATE_KEY = 'blahblahblahblahblahblahprivate'
    RECAPTCHA_OPTIONS = {'theme': 'white'}
    
    ANALYTICS_ENABLED = True
    ANALYTICS_ACCOUNT_ID = 'UA-37369750-1'
    
    MONGOALCHEMY_DATABASE = 'adsabs'
    MONGOALCHEMY_SERVER = 'localhost'
    MONGOALCHEMY_PORT = 27017
    MONGOALCHEMY_SAFE_SESSION = False
    MONGOALCHEMY_SERVER_AUTH = False
    MONGOALCHEMY_USER = 'adsabs'
    MONGOALCHEMY_PASSWORD = ''
    
    COOKIE_ADSABS2_NAME = 'NASA_ADSABS2_ID'
    COOKIE_ADS_CLASSIC_NAME = 'NASA_ADS_ID'
    #cookies configurations
    COOKIES_CONF = {COOKIE_ADS_CLASSIC_NAME :{
                         'domain': ('adsabs.harvard.edu', '.adsabs.harvard.edu'),
                         'max_age': 31356000
                         },  
                     COOKIE_ADSABS2_NAME :{
                         'domain': ('adsabs.harvard.edu', '.adsabs.harvard.edu'),
                         'max_age': 31356000
                         },  
                     }
    
    SOLR_URL = 'http://adswhy:9000/solr/collection1'
    SOLR_TIMEOUT = 300
    SOLR_MAX_RETRIES = 5
    SOLR_SORT_OPTIONS = {'DATE': 'pubdate_sort',
                         'RELEVANCE': 'score',
                         'CITED': 'citation_count',
                         'POPULARITY': 'read_count'
                        }
    #the fields allowed to override the sort parameter. 
    #For now they are only the same but in the future we will implement re-sorting for other fields like author or title
    RE_SORT_OPTIONS = {'DATE': 'pubdate_sort',
                         'RELEVANCE': 'score',
                         'CITED': 'citation_count',
                         'POPULARITY': 'read_count'
                        }
    SEARCH_SECOND_ORDER_OPERATORS_OPTIONS = ['hot', 'useful', 'instructive']
    SOLR_MISC_DEFAULT_PARAMS = [
        ('hl.maxAnalyzedChars', '150000'), 
        #('fq', ['pubdate_sort:[* TO 20140000]']),
        ('indent', 'true')
    ]
    SOLR_DEFAULT_FORMAT = 'json'
    SOLR_ARG_SEPARATOR = '#' # used to thwart the defaul solrpy behavior of replacing '_' with '.' in all solr params
    SOLR_DOCUMENT_ID_FIELD = 'bibcode'
    SOLR_FILTER_QUERY_PARSER = 'aqp'
    
    SEARCH_DEFAULT_ROWS = '20'
    SEARCH_DEFAULT_SORT = 'DATE'
    SEARCH_DEFAULT_SORT_DIRECTION = 'desc'
    
#    SEARCH_DEFAULT_SOLR_FIELDS = ['id','bibcode','bibstem', 'identifier', 'title','author','pub','score','property','abstract','keyword','doi', 'aff',
#                                  'pubdate','citation_count','reference', 'pub_raw', 'copyright', 'links_data', 'ids_data', 'links']
#    
#    SEARCH_DEFAULT_SOLR_FACETS = [
#        ('bibstem_facet', 100, 1),
#        ('author_facet',1000, 1), 

#    SOLR_SEARCH_DEFAULT_FIELDS = ['id','bibcode','bibstem','title','author','pub','score','property','doi','aff','pubdate','citation_count', 'links_data', 'ids_data', 'abstract']
    SOLR_SEARCH_DEFAULT_FIELDS = ['id','bibcode','bibstem', 'identifier', 'title','author','pub','score','property','abstract','keyword','doi', 'aff',
                                  'pubdate','citation_count','reference', 'pub_raw', 'copyright', 'links_data', 'ids_data', 'links']
    SOLR_DOCUMENT_DEFAULT_FIELDS = ['id','bibcode','bibstem','title','author','pub','property','abstract','keyword','doi','aff','pubdate','citation_count', 'links_data', 'ids_data', 'abstract']
    
    SOLR_SEARCH_DEFAULT_FACETS = [
        # tuple format: (solr field name, limit, mincount, output key, prefix)
        ('bibstem_facet', 100, 1),
        ('author_facet_hier', 200, 1, None, "0/"), 
        ('property',100, 1),
        ('keyword_facet',100, 1),
        ('year', -1, 1),
        ('bibgroup_facet',100, 1),
        ('data_facet',100, 1),
        ('vizier_facet',100, 1),
        ('grant_facet_hier', 100, 1, None, "0/"),
        ]
    
    SOLR_SEARCH_DEFAULT_HIGHLIGHTS = [('full', 4),('abstract', 4)]
    SOLR_DOCUMENT_DEFAULT_HIGHLIGHTS = [('abstract', 1, 50000)]
    
    #Dictionary of allowed facets from the web interface and mapping to the real facet field in SOLR
    ALLOWED_FACETS_FROM_WEB_INTERFACE = {'bib_f':'bibstem_facet',
                                         'bibgr_f':'bibgroup_facet',
                                         'aut_f':'author_facet_hier',
                                         'prop_f':'property',
                                         'key_f':'keyword_facet',
                                         'pub_f':'pub',
                                         'year_f':'year',
                                         'grant_f':'grant_facet_hier',
                                         'data_f':'data_facet',
                                         'vizier_f':'vizier_facet',
                                         }
    #Dictionary with the configuration of the facets for the templates
    FACETS_IN_TEMPLATE_CONFIG = {'templ_aut_f' : {'facetid':'aut_f', 'facet_title':'Authors', 'open_by_default':True, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_key_f' : {'facetid':'key_f', 'facet_title':'Keywords', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_bib_f' : {'facetid':'bib_f', 'facet_title':'Publications', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_refereed_f' : {'facetid':'prop_f', 'facet_title':'Refereed status', 'open_by_default':False, 'value_limit_to':['refereed', 'not refereed'], 'facetid_html':'refereed_f'},
                                 'templ_bibgr_f' : {'facetid':'bibgr_f', 'facet_title':'Bib Groups', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_grant_f' : {'facetid':'grant_f', 'facet_title':'Grants', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_data_f' : {'facetid':'data_f', 'facet_title':'Data', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_vizier_f' : {'facetid':'vizier_f', 'facet_title':'Vizier Tables', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_year_f' : {'facetid':'year_f', 'facet_title':'Publication Year', 'open_by_default':True, 'value_limit_to':[], 'facetid_html':None},                                 
                                }
    
    LOGGING_LOG_PATH = os.path.join(_basedir, 'logs/adsabs.log')
    LOGGING_LOG_LEVEL = 'WARN'
    LOGGING_LOG_FORMAT = "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
    # dict of kwargs to use when creating a TimedRotationFileHandler
    LOGGING_ROTATION_SETTINGS = {'when': 'D', 'interval': 7, 'backupCount': 8}
    
    REDIS_ENABLE = True
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DATABASE = 0
    
    INVENIO_BASEURL = 'http://adsx.cfa.harvard.edu'
    ADS_CLASSIC_BASEURL = 'http://adsabs.harvard.edu'

    API_CURRENT_VERSION = '0.1'
    API_DEFAULT_RESPONSE_FORMAT = 'json'
    API_SOLR_DEFAULT_SORT = ('pubdate_sort','desc')
    
    API_SOLR_DEFAULT_FIELDS = ['id','bibcode','title','author','pub','property','abstract','keyword','citation_count',
                               'aff','database','identifier','doi','grants','year','issue','volume','page']
    API_SOLR_EXTRA_FIELDS = ['full','references','ack','score']
    API_SOLR_HIGHLIGHT_FIELDS = ['title','abstract','full','ack']
    
    API_SOLR_FACET_FIELDS = {
        'bibstem': 'bibstem_facet',
        'author': 'author_facet',
        'property': 'property',
        'keyword': 'keyword_facet',
        'pubdate': 'pubdate',
        'year': 'year'
    }
    
    SMTP_HOST = 'localhost'
    API_WELCOME_FROM_EMAIL = 'jluker@cfa.harvard.edu'

try:
    from local_config import LocalConfig
except ImportError:
    LocalConfig = type('LocalConfig', (object,), dict())
    
for attr in filter(lambda x: not x.startswith('__'), dir(LocalConfig)):
    setattr(AppConfig, attr, LocalConfig.__dict__[attr])
    
config = AppConfig
