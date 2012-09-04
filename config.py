import os

_basedir = os.path.abspath(os.path.dirname(__file__))

APP_NAME = "adslabs"

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
    
    APP_VERSION = '2012-08-21'
    
    SOLR_URL = 'http://adsate:8987/solr/collection1'
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
                       'verbose': {
                           'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
                       },
                       'simple': {
                           'format': '%(levelname)s %(message)s'
                       },
                    },
        'handlers': {
                     'console': {
                            'level': 'DEBUG',
                            'class': 'logging.StreamHandler',
                            'formatter': 'simple'
                            },
                     'file': {
                             'level': 'DEBUG',
                             'class': 'logging.FileHandler',
                             'formatter': 'simple',
                             'filename' : os.path.join(_basedir, 'logs/') + APP_NAME + '.log'
                             }
                     },
        'loggers': {
                    'adsabs.core.solr': {
                        'handlers': ['console','file'],
                        }
                    },
        'root': {
                 'level': 'DEBUG',
                 'handlers': ['console','file'],
                 }
           }

class DebugConfig(DefaultConfig):
    DEBUG = True
    