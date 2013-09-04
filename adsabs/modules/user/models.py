'''
Created on Oct 25, 2012

@author: jluker
'''

import pytz
from datetime import datetime
from adsabs.extensions import mongodb
from flask.ext.mongoalchemy import document #@UnresolvedImport

class AdsUserRecord(mongodb.Document): #@UndefinedVariable
    """
    Model for the local database of ADS users
    """
    config_collection_name = 'ads_users'
    
    #fields
    cookie_id = mongodb.StringField() #@UndefinedVariable
    myads_id = mongodb.StringField(default='', required=False) #@UndefinedVariable
    username = mongodb.StringField() #@UndefinedVariable
    password = mongodb.StringField(default=None, required=False) #@UndefinedVariable   #this field is used only to store the password temporary
    firstname = mongodb.StringField(default='', required=False) #@UndefinedVariable
    lastname = mongodb.StringField(default='', required=False) #@UndefinedVariable
    active = mongodb.BoolField(default=False) #@UndefinedVariable
    anonymous = mongodb.BoolField(default=True) #@UndefinedVariable
    developer_key = mongodb.StringField(default='', required=False) #@UndefinedVariable
    developer_perms = mongodb.AnythingField(default={}, required=False) #@UndefinedVariableo
    registered = mongodb.DateTimeField(default=datetime.utcnow().replace(tzinfo=pytz.utc)) #@UndefinedVariableo
    last_signon = mongodb.DateTimeField(default=None, required=False) #@UndefinedVariableo
    remote_login_system = mongodb.StringField(default='', required=False) #@UndefinedVariable
    alternate_usernames = mongodb.SetField(mongodb.StringField(), required=False) #@UndefinedVariable
    openurl_icon = mongodb.StringField(default=None, required=False) #@UndefinedVariable
    
    # indexes
    cookie_id_index = document.Index().descending('cookie_id').unique()
    username_index = document.Index().descending('username').unique()
    alt_username_index = document.Index().descending('alternate_usernames')
    
    