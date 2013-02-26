import os
import pytz

from logging import getLogger
import logging.config
from flask import Flask, render_template, send_from_directory, g, Markup
from config import config, APP_NAME
from wsgi_middleware import DeploymentPathMiddleware
from adsabs.core.template_filters import *
import dicttoxml

# For import *
__all__ = ['create_app']

logger = None

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
    _configure_template_filters(app)
    _configure_error_handlers(app)
    _configure_misc_handlers(app)
    _configure_global_variables(app)
    
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
    
    if app.config.get('LOGGING_CONFIG'):
        logging.config.fileConfig(app.config['LOGGING_CONFIG'])
    global logger
    logger = getLogger()
    
    if config.LOGGING_MONGO_ENABLED:
        from mongolog.handlers import MongoHandler
        handler = MongoHandler(
            db=config.MONGOALCHEMY_DATABASE,
            collection=config.LOGGING_MONGO_COLLECTION,
            host=config.MONGOALCHEMY_SERVER,
            port=config.MONGOALCHEMY_PORT,
            level=getattr(logging, config.LOGGING_MONGO_LEVEL)
        )
        logger.addHandler(handler)
        
def _configure_wsgi_middleware(app):
    app.wsgi_app = DeploymentPathMiddleware(app.wsgi_app)

def _configure_blueprints(app):
    """
    Function that registers the blueprints
    """
    from adsabs.blueprint_conf import BLUEPRINTS
    
    for blueprint in BLUEPRINTS:
        logger.debug("registering blueprint: %s" % blueprint['blueprint'])
        #I extract the blueprint
        cur_blueprint = getattr(blueprint['module'], blueprint['blueprint'])
        #register the blueprint
        app.register_blueprint(cur_blueprint, url_prefix=blueprint['prefix'])
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
    logger.debug("initializing login_manager")
    login_manager.init_app(app) #@UndefinedVariable
    
    #mongo db
    try:
        logger.debug("initializing mongodb")
        mongodb.init_app(app) #@UndefinedVariable
        # The flask-mongoalchemy extension doesn't expose 
        # these options to init_app so we have to do them manually
        mongodb.session.db.write_concern = {'w': 1, 'j': True}
        mongodb.session.tz_aware = True
        mongodb.session.timezone = pytz.utc
    except Exception, e:
        logger.error("Failed to initialize mongoalchemy session: %s" % e.message)
        raise
        
    logger.debug("initializing solr connection")
    solr.init_app(app) #@UndefinedVariable
    
    logger.debug("initializing pushrod")
    pushrod.init_app(app)  #@UndefinedVariable
    
    logger.debug("initializing jinja2 extensions")
    app.jinja_env.add_extension('jinja2.ext.with_')
    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    
def _configure_template_filters(app):
    """
    Configuration of additional filters needed in the templates
    """
    @app.template_filter('urlencode')
    def urlencode_filter(value):
        return quote_url(value)
    
    @app.template_filter('format_ads_date')
    def f_a_d(date_string):
        return format_ads_date(date_string)
    
    @app.template_filter('format_ads_facet_str')
    def f_a_f_s(facet_string):
        return format_ads_facet_str(facet_string)
    
    @app.template_filter('safe_html_unescape')
    def s_h_f(html_string):
        return safe_html_unescape(html_string)
    
    @app.template_filter('ads_url_redirect')
    def a_u_r(adsid, id_type):
        return ads_url_redirect(adsid, id_type)
    
    @app.template_filter('dict2xml')
    def d_2_x(d):
        xml = dicttoxml.dicttoxml(d, root=False)
        return Markup(xml)
    
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
    
#    @app.errorhandler(400)
#    def forbidden_page(error):
#        return render_template("errors/400.html"), 400
#
#    @app.errorhandler(403)
#    def forbidden_page(error):
#        return render_template("errors/403.html"), 403
#
#    @app.errorhandler(404)
#    def page_not_found(error):
#        return render_template("errors/404.html"), 404
#
#    @app.errorhandler(405)
#    def method_not_allowed_page(error):
#        return render_template("errors/405.html"), 405
#
#    @app.errorhandler(500)
#    def server_error_page(error):
#        return render_template("errors/500.html"), 500
    
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
    
def _configure_global_variables(app):
    """
    attaches to the g variable all the parameters from the configuration needed in the templates
    """
    @app.before_request
    def attach_config_params():
        g.conf_params = {}
        g.conf_params['PRINT_DEBUG_TEMPLATE'] = config.PRINT_DEBUG_TEMPLATE
        g.conf_params['APP_VERSION'] = config.APP_VERSION
    