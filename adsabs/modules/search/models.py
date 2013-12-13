'''
Created on Oct 25, 2012

@author: jluker
'''

import pytz
from datetime import datetime
from adsabs.extensions import mongodb
from flask.ext.mongoalchemy import document #@UnresolvedImport

class BigQuery(mongodb.Document): #@UndefinedVariable
    """
    Model for the local database of ADS users
    """
    config_collection_name = 'big_query'
    
    #fields
    query_id = mongodb.StringField() #@UndefinedVariable
    data = mongodb.StringField() #@UndefinedVariable
    created = mongodb.DateTimeField(default=datetime.utcnow().replace(tzinfo=pytz.utc)) #@UndefinedVariableo
    
    # indexes
    query_id_index = document.Index().descending('query_id').unique()
    
    