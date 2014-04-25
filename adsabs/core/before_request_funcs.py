'''
Created on Apr 24, 2013

@author: dimilia
'''

import uuid

from flask import request, g
from flask.ext.login import current_user #@UnresolvedImport
from adsabs.extensions import statsd
from config import config

def set_user_cookie_id():
    """
    Sets the user id in the global object if nothing is there 
    before each request
    This function works together with set_user_cookie in the after requests
    """
    #new fresh user
    if not request.cookies.get(config.COOKIE_ADSABS2_NAME):
        if current_user.is_anonymous():
            g.user_cookie_id = unicode(uuid.uuid4())
        else:
            g.user_cookie_id = current_user.get_id()
    #the user has already visited the web site
    else:
        if current_user.is_anonymous():
            #if the cookie is a valid UUID it's ok
            curr_cookie = request.cookies.get(config.COOKIE_ADSABS2_NAME)
            try:
                uuid.UUID(curr_cookie)
                g.user_cookie_id = curr_cookie
            #otherwise the app generates a new one
            except ValueError:
                g.user_cookie_id = unicode(uuid.uuid4())
        else:
            g.user_cookie_id = current_user.get_id()

def configure_before_request_funcs(app):
    """
    Function to configure all the "before request" functions 
    I want to attach to the application at the global level.
    """
    @app.before_request
    def conf_set_user_cookie_id():
        return set_user_cookie_id()
    
    @app.before_request
    def check_for_maintenance():
        if config.DOWN_FOR_MAINTENANCE:
            return 'Sorry, we\'re down momentarily for a teensey bit of maintenance!', 503
    
    @app.before_request
    def count_uniques():
        statsd.set('unique_users', g.user_cookie_id)
        statsd.set('unique_ips', request.remote_addr)
        
    @app.before_request
    def set_statsd_context():
        g.statsd_context = "%s.%s" % (request.endpoint, request.method)
        g.total_request_timer = statsd.timer(g.statsd_context + ".response_time")
        g.total_request_timer.start()
 