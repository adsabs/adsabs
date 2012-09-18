from adsabs.extensions import mongodb

from flask.ext.mongoalchemy import document #@UnresolvedImport

# For import *
__all__ = ['adsUser']

class adsUser(mongodb.Document): #@UndefinedVariable
    """
    Model for the local database of ADS users
    """
    config_collection_name = 'ads_users'
    
    cookie_id = mongodb.StringField() #@UndefinedVariable
    myads_id = mongodb.StringField(default='', required=False) #@UndefinedVariable
    username = mongodb.StringField() #@UndefinedVariable
    firstname = mongodb.StringField(default='', required=False) #@UndefinedVariable
    lastname = mongodb.StringField(default='', required=False) #@UndefinedVariable
    active = mongodb.BoolField(default=False) #@UndefinedVariable
    anonymous = mongodb.BoolField(default=True) #@UndefinedVariable
    developer = mongodb.BoolField(default=False) #@UndefinedVariable
    developer_key = mongodb.StringField(default='', required=False) #@UndefinedVariable
    developer_level = mongodb.IntField(default=-1) #@UndefinedVariable
    
    cookie_id_index = document.Index().descending('cookie_id').unique()