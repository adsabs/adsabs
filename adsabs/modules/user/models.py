'''
Created on Oct 25, 2012

@author: jluker
'''

import pytz
from datetime import datetime
from adsabs.extensions import mongodb
from flask.ext.mongoalchemy import document,fields #@UnresolvedImport

class AdsUserRecord(mongodb.Document): #@UndefinedVariable
    """
    Model for the local database of ADS users
    """
    config_collection_name = 'ads_users'
    
    #fields
    cookie_id = mongodb.StringField() #@UndefinedVariable
    myads_id = mongodb.StringField(default='', required=False) #@UndefinedVariable
    username = mongodb.StringField() #@UndefinedVariable
    firstname = mongodb.StringField(default='', required=False) #@UndefinedVariable
    lastname = mongodb.StringField(default='', required=False) #@UndefinedVariable
    active = mongodb.BoolField(default=False) #@UndefinedVariable
    anonymous = mongodb.BoolField(default=True) #@UndefinedVariable
    developer_key = mongodb.StringField(default='', required=False) #@UndefinedVariable
    developer_perms = mongodb.AnythingField(default={}, required=False) #@UndefinedVariableo
    registered = mongodb.DateTimeField(default=datetime.utcnow().replace(tzinfo=pytz.utc)) #@UndefinedVariableo
    last_signon = mongodb.DateTimeField(default=None, required=False) #@UndefinedVariableo
    
    # indexes
    cookie_id_index = document.Index().descending('cookie_id').unique()
    
    