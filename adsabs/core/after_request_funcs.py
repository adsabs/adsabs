'''
Created on Apr 23, 2013

@author: dimilia
'''
from flask import request, g
from flask.ext.login import current_user #@UnresolvedImport
from config import config


def after_this_request(func):
    """
    Decorator that can be used in the single views to
    run a "per view" request
    """
    if not hasattr(g, 'call_after_request'):
        g.call_after_request = []
    g.call_after_request.append(func)
    return func

def set_user_cookie(response):
    """
    Function that checks if the user has already a cookie and if he doesn't
    it assigns a unique one
    This function relies on the fact that before each request a g.user_cookie_id is created properly
    """
    #extraction of parameters used multiple times
    is_user_authenticated = current_user.is_authenticated()
    adsabs2_cookie = request.cookies.get(config.COOKIE_ADSABS2_NAME) #cookie of the new ads
    ads_cookie = request.cookies.get(config.COOKIE_ADS_CLASSIC_NAME) #cookie of ads classic
#    print 'new- %s ; old- %s' % (adsabs2_cookie, ads_cookie)

    
    #case 1: no authentication and no cookies (first time the user arrive in the website)
    if not is_user_authenticated and not adsabs2_cookie:
        for domain in config.COOKIES_CONF[config.COOKIE_ADSABS2_NAME]['domain']:
            response.set_cookie(config.COOKIE_ADSABS2_NAME, g.user_cookie_id, max_age=config.COOKIES_CONF[config.COOKIE_ADSABS2_NAME].get('max_age', 31356000), domain=domain)
    #case 2: no authentication but cookies set (not first time the user arrives in the website): NOTHING TO DO
    #case 3: user authenticated and cookies set
    if is_user_authenticated and adsabs2_cookie:
        #need to check if the cookie is the same of the user id and if not set it
        if current_user.get_id() != adsabs2_cookie:
            #the user just authenticated
            for domain in config.COOKIES_CONF[config.COOKIE_ADSABS2_NAME]['domain']:
                response.set_cookie(config.COOKIE_ADSABS2_NAME, current_user.get_id(), max_age=config.COOKIES_CONF[config.COOKIE_ADSABS2_NAME].get('max_age', 31356000), domain=domain)        
    #case 4: user authenticated and no cookies set (should happen only if the cookies expire or the user delete them)
    if is_user_authenticated and not adsabs2_cookie:
        for domain in config.COOKIES_CONF[config.COOKIE_ADSABS2_NAME]['domain']:
            response.set_cookie(config.COOKIE_ADSABS2_NAME, current_user.get_id(), max_age=config.COOKIES_CONF[config.COOKIE_ADSABS2_NAME].get('max_age', 31356000), domain=domain)
    #case 5: use authenticated and not ADS Classic cookie set
    if is_user_authenticated and not ads_cookie:
        for domain in config.COOKIES_CONF[config.COOKIE_ADS_CLASSIC_NAME]['domain']:
            response.set_cookie(config.COOKIE_ADS_CLASSIC_NAME, current_user.get_id(), max_age=config.COOKIES_CONF[config.COOKIE_ADS_CLASSIC_NAME].get('max_age', 31356000), domain=domain)
    #case 6: user authenticated and Classic ADS cookie set
    if is_user_authenticated and ads_cookie:
        if current_user.get_id() != ads_cookie:
            for domain in config.COOKIES_CONF[config.COOKIE_ADS_CLASSIC_NAME]['domain']:
                response.set_cookie(config.COOKIE_ADS_CLASSIC_NAME, current_user.get_id(), max_age=config.COOKIES_CONF[config.COOKIE_ADS_CLASSIC_NAME].get('max_age', 31356000), domain=domain)
    
    return response

def configure_after_request_funcs(app):
    """
    Function to configure all the "after request" functions 
    I want to attach to the application at the global level.
    """
        
    @app.after_request
    def per_request_callbacks(response):
        """
        Function that processes all the "per request"  callbacks 
        """
        for func in getattr(g, 'call_after_request', ()):
            response = func(response)
        return response
    
    @app.after_request
    def conf_set_user_cookie(response):
        return set_user_cookie(response)