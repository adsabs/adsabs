from views import api_blueprint as blueprint
from renderers import *
from api_request import *
from api_user import *

def setup(app):
    
    from adsabs.core.redis import createLogger
    api_logger = createLogger(app, 'api') 
    app.logger.debug("api logger initialized")