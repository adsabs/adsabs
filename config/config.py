import os

_basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

APP_NAME = "adsabs"

class AppConfig(object):
    #flask Setting for debug view in case of errors
    DEBUG = False
    #Flask setting for unittest
    TESTING = False
    #prints the template in the bottom of the page with the link to SOLR
    PRINT_DEBUG_TEMPLATE = False
    PRINT_DEBUG_TEMPLATE_PARAM = None
    
    APP_VERSION = '2013_12_27_v1'
    
    # Override in local_config.py, e.g. DEPLOYMENT_PATH = "/adsabs"
    DEPLOYMENT_PATH = None
    
    # run shell.py create_local_config to generate this value in local_config.py
    # or generate_secret_key to do it manually
    SECRET_KEY = None
    
    # account verification secret key. Generate it in the same way you generate SECRET KEY
    ACCOUNT_VERIFICATION_SECRET = None
    
    #if True, this turns off compression and minification of js and css
    ASSETS_DEBUG = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')
    DATABASE_CONNECT_OPTIONS = {}
    
    THREADS_PER_PAGE = 8

    CSRF_ENABLED=True

    ANALYTICS_ENABLED = True
    ANALYTICS_ACCOUNT_ID = 'UA-37369750-1'
    
    GRANT_NUMBER = 'NNX12AG54G'

    MONGOALCHEMY_DATABASE = 'adsabs'
    MONGOALCHEMY_SERVER = 'localhost'
    MONGOALCHEMY_PORT = 27017
    MONGOALCHEMY_SAFE_SESSION = False
    MONGOALCHEMY_SERVER_AUTH = False
    MONGOALCHEMY_USER = None
    MONGOALCHEMY_PASSWORD = None
    
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
    USER_MIN_PASSWORD_LENGTH = 1
    USER_MAX_PASSWORD_LENGTH = 100
    
    SOLRQUERY_URL = 'http://adswhy:9000/solr/collection1/select'
    SOLRQUERY_TIMEOUT = 300
    SOLRQUERY_KEEPALIVE = False
    SOLRQUERY_HTTP_METHOD = 'POST'
    SOLRQUERY_EXTRA_PARAMS = [
        ('hl.maxAnalyzedChars', '150000'), 
        ('hl.requireFieldMatch', 'true'),
        ('hl.usePhraseHighlighter', 'true'),
        #('fq', ['pubdate_sort:[* TO 20140000]']),
        ('indent', 'true')
    ]

    SOLR_DOCUMENT_ID_FIELD = 'bibcode'
    SOLR_FILTER_QUERY_PARSER = 'aqp'
    SOLR_HIGHLIGHTER_QUERY_PARSER = 'aqp'
    SOLR_HAPROXY_SESSION_COOKIE_NAME = 'JSESSIONID'

    # this operator wraps the user query if sort by relevance is selected
    # and no additional operators are used
    SOLR_RELEVANCE_FUNCTION = 'classic_relevance(%s,0.4)'
    
    SEARCH_DEFAULT_ROWS = 20
#    SEARCH_DEFAULT_SORT = 'RELEVANCE'
    SEARCH_DEFAULT_SORT = 'DATE'
#    SEARCH_DEFAULT_SORT_DIRECTION = 'desc'
    SEARCH_DEFAULT_DATABASE = '(astronomy OR physics)'
#    SEARCH_DEFAULT_DATABASE = 'astronomy'
    
    SEARCH_SORT_OPTIONS_MAP = {
        'DATE': ('pubdate_sort', 'desc'),
        'RELEVANCE': ('score', 'desc'),
        'CITED': ('citation_count', 'desc'),
        'POPULARITY': ('read_count', 'desc'),
    }
    ABS_SORT_OPTIONS_MAP = {
        'references': ('first_author_norm', 'asc'),
        'citations': ('pubdate_sort', 'desc')
    }
    SEARCH_DEFAULT_SECONDARY_SORT = ('bibcode', 'desc')

    AUTHOR_NETWORK_DEFAULT_FIRST_RESULTS = 1000
    WORD_CLOUD_DEFAULT_FIRST_RESULTS = 250
    
    SOLR_SEARCH_DEFAULT_FIELDS = ['id','bibcode','bibstem', 'identifier', 'title','author','pub','score','property','abstract','keyword','doi', 'aff',
                                  'pubdate','reference', 'pub_raw', 'copyright', 'links_data', 'ids_data', 'links', 'reader', '[citations]']
    
    SOLR_SEARCH_DEFAULT_QUERY_FIELDS = None # None=use the defaults configured by our search service
    SOLR_SEARCH_DEFAULT_QUERY_FIELDS_METADATA_ONLY = "first_author^3.0 author^2 title^1.4 abstract^1.3 keyword^1.4 keyword_norm^1.4 all year"


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
        ('database',-1, 1),
        ]
    
    SOLR_SEARCH_DEFAULT_HIGHLIGHTS = [('body', 4),('abstract', 4),('ack', 4)]
    SOLR_DOCUMENT_DEFAULT_HIGHLIGHTS = [('abstract', 1, 50000)]
    SOLR_SEARCH_REQUIRED_FIELDS = ['id','bibcode']
    
    SOLR_MLT_FIELDS = ["abstract","title"]
    SOLR_MLT_PARAMS = [
            ('mlt.boost', 'true'),
            ('mlt.interestingTerms', 'details'),
            ('mlt.mintf',1),
            ('mlt.mindf',20),
            ('mlt.minwl',2),
            ('mlt.maxwl',40),
            ('mlt.maxqt',20)
        ]
    #dictionary of how the facets are mapped by default to the query or filter_query fields for the actual query to the solr
    #added also a default function to use
    FACET_TO_SOLR_QUERY = {
                                'bib_f':{'default_mode':'q', 'default_function':'_append_to_query'},
                                'bibgr_f':{'default_mode':'q', 'default_function':'_append_to_query'},
                                'aut_f':{'default_mode':'q', 'default_function':'_append_to_query'},
                                'prop_f':{'default_mode':'q', 'default_function':'_append_to_query'},
                                'key_f':{'default_mode':'q', 'default_function':'_append_to_query'},
                                'pub_f':{'default_mode':'q', 'default_function':'_append_to_query'},
                                'year_f':{'default_mode':'q', 'default_function':'_append_to_query'},
                                'grant_f':{'default_mode':'q', 'default_function':'_append_to_query'},
                                'data_f':{'default_mode':'q', 'default_function':'_append_to_query'},
                                'vizier_f':{'default_mode':'q', 'default_function':'_append_to_query'},
                                'db_f':{'default_mode':'fq', 'default_function':'_append_to_list'},
                                }
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
                                         'db_f':'database',
                                         }
    #Dictionary with the configuration of the facets for the templates
    FACETS_IN_TEMPLATE_CONFIG = {'templ_aut_f' : {'facetid':'aut_f', 'facet_title':'Authors', 'open_by_default':True, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_key_f' : {'facetid':'key_f', 'facet_title':'Keywords', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_bib_f' : {'facetid':'bib_f', 'facet_title':'Publications', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_refereed_f' : {'facetid':'prop_f', 'facet_title':'Refereed status', 'open_by_default':False, 'value_limit_to':['refereed', 'notrefereed'], 'facetid_html':'refereed_f'},
                                 'templ_bibgr_f' : {'facetid':'bibgr_f', 'facet_title':'Bib Groups', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_grant_f' : {'facetid':'grant_f', 'facet_title':'Grants', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_data_f' : {'facetid':'data_f', 'facet_title':'Data', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_vizier_f' : {'facetid':'vizier_f', 'facet_title':'Vizier Tables', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_year_f' : {'facetid':'year_f', 'facet_title':'Publication Year', 'open_by_default':True, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_topn_f' : {'facetid':'topn', 'facet_title':'Top papers', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                 'templ_db_f' : {'facetid':'db_f', 'facet_title':'Database', 'open_by_default':False, 'value_limit_to':[], 'facetid_html':None},
                                }
    
    LOGGING_LOG_LEVEL = 'WARN'
    LOGGING_LOG_TO_FILE = True
    LOGGING_LOG_TO_CONSOLE = False
    LOGGING_LOG_PATH = os.path.join(_basedir, 'logs/adsabs.log')
    LOGGING_LOG_FORMAT = "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
    # dict of kwargs to use when creating a TimedRotationFileHandler
    LOGGING_ROTATION_SETTINGS = {'when': 'D', 'interval': 7, 'backupCount': 8}
    
    REDIS_ENABLE = True
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DATABASE = 0
    
    INVENIO_BASEURL = 'http://adsx.cfa.harvard.edu'
    ADS_CLASSIC_BASEURL = 'http://adsabs.harvard.edu'
    ADS_CLASSIC_LINKOUT_BASEURL = 'http://adsabs.harvard.edu/cgi-bin/nph-data_query/noredirect'
    ADS_CLASSIC_LINKOUT_LINK_TYPE_MAP = {'coreads': 'AR'}
    ADS_LOGIN_URL = None

    API_CURRENT_VERSION = '0.1.1'
    API_DEFAULT_RESPONSE_FORMAT = 'json'
    API_SOLR_DEFAULT_SORT = [('pubdate_sort','desc'),('bibcode','desc')]
    
    API_SOLR_DEFAULT_FIELDS = ['id','bibcode','title','author','pub','property','abstract','keyword','citation_count','bibstem',
                               'aff','database','identifier','doi','grants','year','issue','volume','page','pubdate','[citations]']
    API_SOLR_EXTRA_FIELDS = ['body','references','ack','score']
    API_SOLR_HIGHLIGHT_FIELDS = ['title','abstract','body','ack']
    
    API_SOLR_FACET_FIELDS = {
        'bibstem': 'bibstem_facet',
        'author': 'author_facet',
        'property': 'property',
        'keyword': 'keyword_facet',
        'pubdate': 'pubdate',
        'year': 'year'
    }
    
    #sendmail configuration
    SMTP_HOST = 'localhost'
    API_WELCOME_FROM_EMAIL = 'adshelp@cfa.harvard.edu'
    API_SIGNUP_SPREADSHEET_KEY = None
    API_SIGNUP_SPREADSHEET_LOGIN = None    

    #flask-mail configuration
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    DEFAULT_MAIL_SENDER = None
    
    MAIL_CONTENT_REDIRECT_BASE_URL = 'http://adslabs.org'
    FEEDBACK_RECIPIENTS = ['name@ema.il',]
    
    RECAPTCHA_USE_SSL = True
    RECAPTCHA_PUBLIC_KEY = ''
    RECAPTCHA_PRIVATE_KEY = ''
    RECAPTCHA_OPTIONS = {'theme' : 'white'}

    PAGES_GIT_URL = "git@github.com:adsabs/adsabs-pages.git"
    PAGES_CONTENT_DIR = os.path.join(_basedir, "page_content")
    PAGES_URL_PREFIX = "/page"
    PAGES_FILE_EXT = ".md"
    PAGES_REFRESH_ALLOWED_IPS = []
    PAGES_REFRESH_ACCESS_KEY = None
    PAGES_REFRESH_BASE_URL = "http://localhost:5000"
    PAGES_DEFAULT_INDEX = "Index"
    
    CACHE_TYPE = 'redis'
    CACHE_KEY_PREFIX = 'cache:adsabs:'

    # configuration parameters for bibutils module
    BIBUTILS_MAX_HITS = 10000
    BIBUTILS_MAX_INPUT= 500
    BIBUTILS_THREADS = 4
    BIBUTILS_THRESHOLD_FREQUENCY = 1
    BIBUTILS_DEFAULT_SUGGESTIONS = 10
    BIBUTILS_DEFAULT_FORMAT = 'score'
    BIBUTILS_CITATION_SOURCE = 'MONGO'
    # configuration parameters for the metrics module
    METRICS_DEFAULT_MODELS = 'statistics,histograms,metrics,series'
    METRICS_THREADS = 8
    METRICS_MIN_BIBLIO_LENGTH = 5
    METRICS_CHUNK_SIZE = 100
    METRICS_MAX_HITS = 100000
    METRICS_TMP_DIR = '/tmp'
    METRICS_MONGO_HOST = 'localhost'
    METRICS_MONGO_PORT = 27017
    METRICS_DATABASE = 'metrics'
    METRICS_COLLECTION = 'metrics_data'
    METRICS_MONGO_USER = 'metrics'
    METRICS_MONGO_PASSWORD = ''
    # config for the adsdata extension
    ADSDATA_MONGO_DATABASE = 'adsdata'
    ADSDATA_MONGO_HOST = "localhost"
    ADSDATA_MONGO_PORT = 27017
    ADSDATA_MONGO_SAFE = True
    ADSDATA_MONGO_USER = 'adsdata'
    ADSDATA_MONGO_PASSWORD = ''

    # configuration parameters for the recommender
    RECOMMENDER_SERVER = 'http://adszee.cfa.harvard.edu:9887'
    RECOMMENDER_RECENTS_URL = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?library=Recent&data_type=XML&libid=%s'

    # configuration parameters for maximum number of records used for various services (metrics, citation helper, exports, ...)
    EXPORT_DEFAULT_ROWS = 300
    MAX_EXPORTS = {'metrics':3000, 
                   'wordcloud':1000, 
                   'ADSClassic':3000,
                   'authnetwork':1000,
                   'skymap':1000,
                   'export_other':3000,
                   'export_library': 500,
                   }
    DEFAULT_EXPORTS = {'metrics':300, 
                   'wordcloud':750, 
                   'ADSClassic':300,
                   'authnetwork':750,
                   'skymap':750,
                   'export_library': 100,
                   'export_other':300,
                   }
    #ADSGUT
    MONGODB_SETTINGS= {'HOST': 'mongodb://user:pass@localhost/adsgut', 'DB': 'adsgut'}
    
try:
    from local_config import LocalConfig
except ImportError:
    LocalConfig = type('LocalConfig', (object,), dict())
    
for attr in filter(lambda x: not x.startswith('__'), dir(LocalConfig)):
    setattr(AppConfig, attr, LocalConfig.__dict__[attr])
    
config = AppConfig
