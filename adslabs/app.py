import os

from flask import Flask, render_template, send_from_directory
from config import DefaultConfig, APP_NAME
from blueprint_conf import BLUEPRINTS

# For import *
__all__ = ['create_app']


def create_app(config=None, app_name=None):
    """Create a Flask app."""

    if app_name is None:
        app_name = APP_NAME

    app = Flask(app_name)
    configure_app(app, config)
#    configure_hook(app)
    configure_blueprints(app)
#    configure_extensions(app)
#    configure_logging(app)
#    configure_template_filters(app)
    configure_error_handlers(app)
    configure_misc_handlers(app)

    return app

def configure_app(app, config):
    """
    configuration of the flask application
    """
    app.config.from_object(DefaultConfig)
    if config is not None:
        app.config.from_object(config)
    # Override setting by env var without touching codes.
    app.config.from_envvar('ADSLABS_APP_CONFIG', silent=True)


def configure_blueprints(app):
    """
    Function that registers the blueprints
    """
    for blueprint in BLUEPRINTS:
        #I extract the blueprint
        cur_blueprint = getattr(blueprint[0], blueprint[1])
        #register the blueprint
        app.register_blueprint(cur_blueprint, url_prefix=blueprint[2])
    return


def configure_error_handlers(app):

    @app.errorhandler(403)
    def forbidden_page(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(405)
    def method_not_allowed_page(error):
        return render_template("errors/405.html"), 405

    @app.errorhandler(500)
    def server_error_page(error):
        return render_template("errors/500.html"), 500
    
def configure_misc_handlers(app):
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static', 'images'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')