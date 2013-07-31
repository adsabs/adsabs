'''
Bridge to the Classic users
'''
from flask import current_app as app
import requests
import sys
import traceback
from config import config


__all__ = ['get_classic_user', 'create_classic_user', 'update_classic_user_info', 'update_classic_username', 'update_classic_password', 'reset_classic_password', 'login_exists_classic']

ADS_LOGIN_URL = config.ADS_LOGIN_URL

def perform_classic_user_query(parameters, headers, service_url):
    """
    function that performs a get request and returns a json object
    """
    #add necessary general parameter
    parameters['man_ads2'] = '1'
    #Perform the request
    r = requests.get(service_url, params=parameters, headers=headers)
    #Perform the request
    try:
        r.raise_for_status()
    except Exception, e:
        exc_info = sys.exc_info()
        app.logger.error("Author http request error: %s, %s\n%s" % (exc_info[0], exc_info[1], traceback.format_exc()))
    
    try:
        user_json = r.json()
    except Exception, e:
        exc_info = sys.exc_info()
        app.logger.error("Author JSON decode error: %s, %s\n%s" % (exc_info[0], exc_info[1], traceback.format_exc()))
        r = None
        user_json = {}
    return user_json

def get_classic_user(login, password=None):
    """
    function that checks the parameters against ads classic
    """
    #basic list list of parameters
    parameters = {'man_email':login, 'man_cmd':'elogin'}
    #add password if exists
    if password:
        parameters.update({'man_passwd':password})
    #headers
    headers = {'User-Agent':'ADS Script Request Agent'}
    return perform_classic_user_query(parameters, headers, ADS_LOGIN_URL)

def create_classic_user(username, password, firstname=None, lastname=None):
    """
    function to create an user in ADS Classic
    """
    #first the creation of the actual account
    parameters = {'man_nemail':username, 'man_npasswd': password, 'man_vpasswd':password, 'man_name':'%s|%s' % (firstname, lastname),'man_cmd':'Update Record'}
    #then the creation of the additional info for the user
    #headers
    headers = {'User-Agent':'ADS Script Request Agent'}
    #Perform the request
    return perform_classic_user_query(parameters, headers, ADS_LOGIN_URL)

def update_classic_user_info(curusername, curpassword, firstname, lastname):
    """
    function to update basic user info in ADS Classic
    """
    #parameters to update
    parameters = {'man_name':'%s|%s' % (firstname, lastname),'man_cmd':'Update Record', 'man_email':curusername, 'man_passwd':curpassword}
    #headers
    headers = {'User-Agent':'ADS Script Request Agent'}
    #Perform the request
    return perform_classic_user_query(parameters, headers, ADS_LOGIN_URL)

def update_classic_username(curusername, newusername, curpassword):
    """
    function that updates the email address in the classic ads
    """
    #parameters to update
    parameters = {'man_cmd':'Update Record', 'man_email':curusername, 'man_passwd':curpassword, 'man_nemail':newusername}
    #headers
    headers = {'User-Agent':'ADS Script Request Agent'}
    #Perform the request
    return perform_classic_user_query(parameters, headers, ADS_LOGIN_URL)

def update_classic_password(curusername, curpassword, newpassword):
    """
    function that updates an user's password
    """
    #parameters to update
    parameters = {'man_cmd':'Update Record', 'man_passwd':curpassword, 'man_npasswd':newpassword, 'man_vpasswd':newpassword, 'man_email':curusername}
    #headers
    headers = {'User-Agent':'ADS Script Request Agent'}
    #Perform the request
    return perform_classic_user_query(parameters, headers, ADS_LOGIN_URL)

def reset_classic_password(curusername, newpassword):
    """
    function to update the password without knowing the old one.
    It can be implemented also as a particular case of update_classic_password
    """
    #parameters to update
    parameters = {'man_cmd':'eupdate', 'man_npasswd':newpassword, 'man_vpasswd':newpassword, 'man_email':curusername}
    #headers
    headers = {'User-Agent':'ADS Script Request Agent'}
    #Perform the request
    return perform_classic_user_query(parameters, headers, ADS_LOGIN_URL)


def login_exists_classic(login):
    """
    function that checks if the login exists in ADS Classic
    """
    #check ADS Classic
    classic_user = get_classic_user(login)
    if classic_user.get('message') == 'ACCOUNT_NOTFOUND':
        return False
    else:
        return True
