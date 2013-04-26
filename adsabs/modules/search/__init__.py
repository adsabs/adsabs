from views import *

# import this separately so we can assign it to the generic 'blueprint' attr
from views import search_blueprint as blueprint

def setup(app):
    
    from adsabs.core.redis import createLogger
    search_logger = createLogger(app, 'search') 
    app.logger.debug("search logger initialized")
    