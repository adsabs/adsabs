import os
import pytz

import logging
from flask import Flask, send_from_directory
from config import config, APP_NAME
from wsgi_middleware import DeploymentPathMiddleware
from adsabs.core.template_filters import configure_template_filters
from adsabs.core.before_request_funcs import configure_before_request_funcs
from adsabs.core.after_request_funcs import configure_after_request_funcs


# For import *
__all__ = ['create_app']

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pymongo") 

def create_app(config=config, app_name=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = APP_NAME

    app = Flask(app_name)
    _configure_app(app, config)
    _configure_logging(app)
    if not config.TESTING:
        _configure_wsgi_middleware(app)
#    configure_hook(app)
    _configure_blueprints(app)
    _configure_extensions(app)
    configure_template_filters(app)
    _configure_error_handlers(app)
    _configure_misc_handlers(app)
    configure_before_request_funcs(app)
    configure_after_request_funcs(app)
    
    if config.DEBUG:
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension(app)

    return app

def _configure_app(app, config):
    """
    configuration of the flask application
    """
    app.config.from_object(config)
    if config is not None:
        app.config.from_object(config)
    # Override setting by env var without touch_import)
    pass

def _configure_logging(app):
    
    from logging.handlers import TimedRotatingFileHandler
    
    # create a rotating log handler
    level = getattr(logging, app.config['LOGGING_LOG_LEVEL'])
    app.logger.setLevel(level)
    handler = TimedRotatingFileHandler(app.config['LOGGING_LOG_PATH'], **app.config['LOGGING_ROTATION_SETTINGS'])
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(app.config['LOGGING_LOG_FORMAT']))
    # add it to the flask app logger
    app.logger.addHandler(handler)
    # and the root logger
    logging.getLogger().addHandler(handler)
    # add console output if log level is >= DEBUG
    if level <= logging.DEBUG:
        from logging import StreamHandler
        app.logger.addHandler(StreamHandler())
    
def _configure_wsgi_middleware(app):
    app.wsgi_app = DeploymentPathMiddleware(app.wsgi_app)

def _configure_blueprints(app):
    """
    Function that registers the blueprints
    """
    from adsabs.blueprint_conf import BLUEPRINTS
    
    for module in BLUEPRINTS:
        blueprint = getattr(module, 'blueprint')
        app.logger.debug("registering blueprint: %s" % blueprint.name)
        app.register_blueprint(blueprint)
        module_setup = getattr(module, 'setup', None)
        if module_setup:
            module_setup(app)
    return

def _configure_extensions(app):
    """
    Function to configure the extensions that need to be wrapped inside the application.
    NOTE: connection to the database MUST be created in this way otherwise they will leak
    """
    from adsabs.extensions import login_manager, mongodb, solr, pushrod
    from adsabs.modules.user import AdsUser
    
    # login.
    login_manager.login_view = 'user.login'
    login_manager.refresh_view = 'user.reauth'
    
    @login_manager.user_loader
    def load_user(id):
        return AdsUser.from_id(id)
    app.logger.debug("initializing login_manager")
    login_manager.init_app(app) #@UndefinedVariable
    
    #mongo db
    try:
        app.logger.debug("initializing mongodb")
        mongodb.init_app(app) #@UndefinedVariable
        # The flask-mongoalchemy extension doesn't expose 
        # these options to init_app so we have to do them manually
        mongodb.session.db.write_concern = {'w': 1, 'j': True}
        mongodb.session.tz_aware = True
        mongodb.session.timezone = pytz.utc
    except Exception, e:
        app.logger.error("Failed to initialize mongoalchemy session: %s" % e.message)
        raise
        
    app.logger.debug("initializing solr connection")
    solr.init_app(app) #@UndefinedVariable
    
    app.logger.debug("initializing pushrod")
    pushrod.init_app(app)  #@UndefinedVariable
    
    app.logger.debug("initializing jinja2 extensions")
    app.jinja_env.add_extension('jinja2.ext.with_')
    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    
# def _configure_template_filters(app):
#     """
#     Configuration of additional filters needed in the templates
#     (left a function here in case we need to have multiple configuration functions)
#     """
#     configure_template_filters(app)
    
    
def _configure_error_handlers(app):
    """
    function that configures some basic handlers for errors
    """
    from errors import create_error_handler
    
    create_error_handler(app, 400, 'errors/400.html')
    create_error_handler(app, 403, 'errors/403.html')
    create_error_handler(app, 404, 'errors/404.html')
    create_error_handler(app, 405, 'errors/405.html')
    create_error_handler(app, 500, 'errors/500.html')

    
def _configure_misc_handlers(app):
    """
    function to configure some basic handlers for basic static file to return from the application root
    """
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static', 'images'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    @app.route('/robots.txt')
    def robots():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt', mimetype='text/plain')
    
#def _configure_global_variables(app):
#    """
#    attaches to the g variable all the parameters from the configuration needed in the templates
#    """
#    @app.before_request
#    def attach_config_params():
#        g.conf_params = {}
#        g.conf_params['PRINT_DEBUG_TEMPLATE'] = config.PRINT_DEBUG_TEMPLATE
#        g.conf_params['APP_VERSION'] = config.APP_VERSION
    
