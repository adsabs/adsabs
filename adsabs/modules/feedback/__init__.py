from views import *

# import this separately so we can assign it to the generic 'blueprint' attr
from views import feedback_blueprint as blueprint

def setup(app):
    from adsabs.core.redis import createLogger
    feedback_logger = createLogger(app, 'feedback') 
    app.logger.debug("feedback logger initialized")
    