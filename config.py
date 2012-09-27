import os

_basedir = os.path.abspath(os.path.dirname(__file__))

APP_NAME = "adsabs"

class DefaultConfig(object):
    
    DEBUG = False

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
    
    MONGOALCHEMY_DATABASE = 'adsabs_mongo'
    MONGOALCHEMY_SERVER = "localhost"
    
    MONGOALCHEMY_COLLECTIONS = {
        'bibstem.Bibstem':         '/proj/ads/abstracts/config/bibstems.dat',
        'fulltext.FulltextItem': '/proj/ads/abstracts/config/links/fulltext/all.links',
        'refereed.RefereedItem': '/proj/ads/abstracts/config/links/refereed/all.links',
        'readers.Readers':         '/proj/ads/abstracts/config/links/alsoread_bib/all.links',
        }
    
    APP_VERSION = '2012-08-21'
    
    SOLR_URL = 'http://adsate:8987/solr/collection1'
    SOLR_ROW_OPTIONS = [('20','20'),('50','50'),('100','100')]
    SOLR_DEFAULT_ROWS = '20'
    SOLR_DEFAULT_FIELDS_SEARCH = ['id','bibcode','title','author','pub','score','property','pubdate_sort']
    SOLR_DEFAULT_SORT = 'pubdate_sort desc'
    SOLR_DEFAULT_PARAMS = [('fq', 'pubdate_sort:[* TO 20130000]')]
    SOLR_DEFAULT_FORMAT = 'json'
    
    # copy logging.conf.dist -> logging.conf and uncomment
    LOGGING_CONFIG = os.path.join(_basedir, 'logging.conf')
    
    INVENIO_BASEURL = 'http://adsx.cfa.harvard.edu'
    ADS_CLASSIC_BASEURL = 'http://adsabs.harvard.edu'

               
class DebugConfig(DefaultConfig):
    DEBUG = True
    
