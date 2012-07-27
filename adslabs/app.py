
from flask import Flask
from config import DefaultConfig, APP_NAME

# For import *
__all__ = ['create_app']

DEFAULT_BLUEPRINTS = []

def create_app(config=None, app_name=None, blueprints=None):
    """Create a Flask app."""

    if config is None:
        config = DefaultConfig
    if app_name is None:
        app_name = APP_NAME
    if blueprints is None:
        blueprints = DEFAULT_BLUEPRINTS

    app = Flask(app_name)
    configure_app(app, config)
#    configure_hook(app)
#    configure_blueprints(app, blueprints)
#    configure_extensions(app)
#    configure_logging(app)
#    configure_template_filters(app)
#    configure_error_handlers(app)

    return app

def configure_app(app, config):
    pass