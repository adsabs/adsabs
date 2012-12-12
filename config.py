import os

_basedir = os.path.abspath(os.path.dirname(__file__))

APP_NAME = "adsabs"

class AppConfig(object):
    
    DEBUG = False
    TESTING = False
    
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
    
    APP_VERSION = '2012-08-21'
    
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
    
    SEARCH_DEFAULT_ROWS = '20'
    SEARCH_DEFAULT_SORT = 'DATE'
    SEARCH_DEFAULT_SORT_DIRECTION = 'desc'
    SEARCH_DEFAULT_FACET_LIMIT = 100
    SEARCH_DEFAULT_FACET_MINCOUNT = 1
    SEARCH_DEFAULT_HIGHLIGHT_COUNT = 5
    SEARCH_DEFAULT_SOLR_FIELDS = ['id','bibcode','bibstem','title','author','pub','score','property','abstract','keyword','doi', 'aff', 'pubdate']
    SEARCH_DEFAULT_SOLR_FACETS = ['bibstem_facet','author_facet','property','keyword','pub','year']
    SEARCH_DEFAULT_HIGHLIGHT_FIELDS = ['full','abstract','ack']
    
    #Dictionary of allowed facets from the web interface and mapping to the real facet field in SOLR
    ALLOWED_FACETS_FROM_WEB_INTERFACE = {'bib_f':'bibstem_facet',
                                         'aut_f':'author_facet',
                                         'prop_f':'property',
                                         'key_f':'keyword',
                                         'pub_f':'pub',
                                         'year_f':'year'}
    
    # copy logging.conf.dist -> logging.conf and uncomment
    LOGGING_CONFIG = os.path.join(_basedir, 'logging.conf')
    
    INVENIO_BASEURL = 'http://adsx.cfa.harvard.edu'
    ADS_CLASSIC_BASEURL = 'http://adsabs.harvard.edu'

    API_DEFAULT_RESPONSE_FORMAT = 'json'
    # this is the full list of fields available
    # Note that most api accounts will not have access to the full list of fields
    API_SOLR_FIELDS = ['id','bibcode','bibstem','title','author','pub','score','property','abstract','keyword','references','aff','full','ack','identifier']
    API_SOLR_FACET_FIELDS = {
        'bibstem': 'bibstem_facet',
        'author': 'author_facet',
        'property': 'property',
        'keyword': 'keyword_facet',
        'pubdate': 'pubdate',
        'pub': 'pub',
        'year': 'year'
    }

try:
    from local_config import LocalConfig
except ImportError:
    LocalConfig = type('LocalConfig', (object,), dict())
    
for attr in filter(lambda x: not x.startswith('__'), dir(LocalConfig)):
    setattr(AppConfig, attr, LocalConfig.__dict__[attr])
    
config = AppConfig