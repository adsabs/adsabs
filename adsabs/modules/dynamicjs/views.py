'''
Created on Feb 27, 2013

@author: dimilia
'''
from flask import Blueprint, g, render_template, make_response
from config import config

dynjs_blueprint = Blueprint('dynamicjs', __name__, template_folder="templates")

__all__ = ['dynjs_blueprint']

@dynjs_blueprint.after_request
def add_caching_header(response):
    """
    Adds caching headers
    """
    if not config.DEBUG:
        cache_header = 'max-age=3600, must-revalidate'
    else:
        cache_header = 'no-cache'
    response.headers.setdefault('Cache-Control', cache_header)
    return response

@dynjs_blueprint.route('/global_variables.js', methods=['GET'])
def dynamic_global_variables():
    """
    Serves JS content containing global dynamic variables 
    """
    response = make_response(render_template('global_variables.js'))
    response.headers['Content-Type'] = 'application/javascript'
    return response