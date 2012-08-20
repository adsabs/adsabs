
from flask import Flask
from config import DefaultConfig, APP_NAME

# For import *
__all__ = ['create_app']


def create_app(config=None, app_name=None):
    """Create a Flask app."""

    if config is None:
        config = DefaultConfig
    if app_name is None:
        app_name = APP_NAME

    app = Flask(app_name)
    configure_app(app, config)
#    configure_hook(app)
    configure_blueprints(app)
#    configure_extensions(app)
#    configure_logging(app)
#    configure_template_filters(app)
#    configure_error_handlers(app)

    return app

def configure_app(app, config):
    """
    
    """
    app.config.from_object(config)


def configure_blueprints(app):
    """
    Function that registers the blueprints
    """
    from blueprint_conf import BLUEPRINTS
    
    for blueprint in BLUEPRINTS:
        #I import the module
        globals()[blueprint[0]] = __import__(blueprint[0], fromlist=['__init__'])
        #I extract the blueprint
        cur_blueprint = getattr(globals()[blueprint[0]], blueprint[1])
        #register the blueprint
        app.register_blueprint(cur_blueprint, url_prefix=blueprint[2])
    return
