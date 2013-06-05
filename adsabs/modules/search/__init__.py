from views import *
from views import search_blueprint as blueprint # import separately and asssign to generic 'blueprint' attr

from flask import g
from config import config

def setup(app):
    
    from adsabs.core.redis import createLogger
    search_logger = createLogger(app, 'search') 
    app.logger.debug("search logger initialized")
    
