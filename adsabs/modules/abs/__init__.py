from views import abs_blueprint as blueprint

def setup(app):
    
    from adsabs.core.redis import createLogger
    abs_logger = createLogger(app, 'abs') 
    app.logger.debug("abstract logger initialized")