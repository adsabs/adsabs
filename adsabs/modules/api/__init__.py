from views import api_blueprint as blueprint
from renderers import *
from request import *
from user import *
from manager import manager

def setup(app):
    
    from adsabs.core.redis import createLogger
    api_logger = createLogger(app, 'api') 
    app.logger.debug("api logger initialized")