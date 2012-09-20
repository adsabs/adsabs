'''
Created on Sep 18, 2012

@author: jluker
'''
import os
from stat import ST_MTIME
from datetime import datetime

from adsabs.extensions import mongodb
from flask.ext.mongoalchemy import document #@UnresolvedImport

class AdsUser(mongodb.Document): #@UndefinedVariable
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
    
class DataLoadTime(mongodb.Document):
    collection = mongodb.StringField()
    last_loaded = mongodb.DateTimeField()
    
class DataCollection(mongodb.Document):
    
    field_order = None
    
    def get_fields_ordered(self):
        fields = self.get_fields()
        if not self.field_order:
            return fields
        ordered_fields = []
        for field_name in self.field_order:
            ordered_fields.append(fields[field_name])
            del fields[field_name]
        ordered_fields.extend(fields.items())
        return ordered_fields
        
    def needs_update(self, source_file):
        last_modified = datetime.fromtimestamp(os.stat(source_file)[ST_MTIME])
        dlt = DataLoadTime(collection=self.get_collection_name())
        if not dlt:
            return True
        
    def load_data(self, source_file):
        pass
    
class Bibstem(DataCollection):
    bibstem = mongodb.StringField()
    dunno = mongodb.EnumField(mongodb.StringField(), "R", "J", "C")
    journal_name = mongodb.StringField()
    
    config_collection_name = 'bibstem'
    field_order = ['bibstem','dunno','journal_name']
    
    def __str__(self):
        return "%s (%s): %s" % (self.bibstem, self.dunno, self.journal_name)
    
class FulltextItem(DataCollection):
    bibcode = mongodb.StringField(_id=True)
    fulltext_source = mongodb.ListField(mongodb.StringField())
    database = mongodb.SetField(mongodb.StringField())
    provider = mongodb.StringField()
    
    config_collection_name = 'fulltext'
    field_order = ['bibcode','fulltext_source','database','provider']
    
    def __str__(self):
        return "%s: %s" % (self.bibcode, self.fulltext_source)
    

class Readers(DataCollection):
    
    bibcode = mongodb.StringField(_id=True)
    readers = mongodb.ListField(mongodb.StringField())
    
    config_collection_name = 'readers'
    field_order = ['bibcode', 'readers']
    
    def __str__(self):
        return "%s: [%s]" % (self.bibcode, self.readers)
    
class RefereedItem(DataCollection):
    bibcode = mongodb.StringField(_id=True)
    
    config_collection_name = 'refereed'