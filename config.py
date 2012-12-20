import os

_basedir = os.path.abspath(os.path.dirname(__file__))

APP_NAME = "adsabs"

class AppConfig(object):
    
    DEBUG = False
    TESTING = False
    PRINT_DEBUG_TEMPLATE = False
    
    APP_VERSION = '2012_12_17'
    
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
    
    MONGOALCHEMY_DATABASE = 'adsabs'
    MONGOALCHEMY_SERVER = 'localhost'
    MONGOALCHEMY_PORT = 27017
    MONGOALCHEMY_OPTIONS = "safe=true"
    
    SOLR_URL = 'http://adsate:8987/solr/collection1'
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
    SOLR_MISC_DEFAULT_PARAMS = [('fq', ['pubdate_sort:[* TO 20130000]']),('indent', 'true')]
    SOLR_DEFAULT_FORMAT = 'json'
    SOLR_ARG_SEPARATOR = '#' # used to thwart the defaul solrpy behavior of replacing '_' with '.' in all solr params
    SOLR_DOCUMENT_ID_FIELD = 'bibcode'
    
    SEARCH_DEFAULT_ROWS = '20'
    SEARCH_DEFAULT_SORT = 'DATE'
    SEARCH_DEFAULT_SORT_DIRECTION = 'desc'
    
    SOLR_SEARCH_DEFAULT_FIELDS = ['id','bibcode','bibstem','title','author','pub','score','property','doi','aff','pubdate','citation_count']
    SOLR_DOCUMENT_DEFAULT_FIELDS = ['id','bibcode','bibstem','title','author','pub','property','abstract','keyword','doi','aff','pubdate','citation_count']
    
    SOLR_SEARCH_DEFAULT_FACETS = [
        ('bibstem_facet',),
        ('author_facet',), 
        ('author_facet_hier', 1000, 1), 
        ('property',),
        ('keyword_facet',),
        ('year',), 
        ('bibgroup',)
        ]
    
    SOLR_SEARCH_DEFAULT_HIGHLIGHTS = [('full', 4),('abstract', 4)]
    SOLR_DOCUMENT_DEFAULT_HIGHLIGHTS = [('abstract', 1, 50000)]
    
    #Dictionary of allowed facets from the web interface and mapping to the real facet field in SOLR
    ALLOWED_FACETS_FROM_WEB_INTERFACE = {'bib_f':'bibstem_facet',
                                         'bibgr_f':'bibgroup',
                                         'aut_f':'author_facet_hier',
                                         'prop_f':'property',
                                         'key_f':'keyword_facet',
                                         'pub_f':'pub',
                                         'year_f':'year',
                                         }
    
    # copy logging.conf.dist -> logging.conf and uncomment
    LOGGING_CONFIG = os.path.join(_basedir, 'logging.conf')
    
    INVENIO_BASEURL = 'http://adsx.cfa.harvard.edu'
    ADS_CLASSIC_BASEURL = 'http://adsabs.harvard.edu'

    API_DEFAULT_RESPONSE_FORMAT = 'json'
    
    API_SOLR_DEFAULT_FIELDS = ['id','bibcode','bibstem','title','author','pub','score','property','abstract','keyword','aff','identifier']
    API_SOLR_EXTRA_FIELDS = ['full','references','ack']
    API_SOLR_HIGHTLIGHT_FIELDS = ['title','abstract','full','ack']
    
    API_SOLR_FACET_FIELDS = {
        'bibstem': 'bibstem_facet',
        'author': 'author_facet',
        'property': 'property',
        'keyword': 'keyword_facet',
        'pubdate': 'pubdate',
        'year': 'year'
    }

try:
    from local_config import LocalConfig
except ImportError:
    LocalConfig = type('LocalConfig', (object,), dict())
    
for attr in filter(lambda x: not x.startswith('__'), dir(LocalConfig)):
    setattr(AppConfig, attr, LocalConfig.__dict__[attr])
    
config = AppConfig