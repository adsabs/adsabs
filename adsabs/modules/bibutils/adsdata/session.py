'''
Created on Oct 25, 2012

@author: jluker
'''

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pymongo") 

import pytz
import logging
import hashlib
import simplejson
from bson import DBRef
from datetime import datetime
from mongoalchemy.session import Session
from pymongo.son_manipulator import SONManipulator


class DataSession(object):
    """
    Wraps a mongoalchemy.Session object and provides methods for 
    directly accessing the internal pymongo client and for querying
    the data collections in models.py
    """
    def __init__(self, db, uri, docs_collection, safe=False, create_ok=False, 
                 inc_manipulators=True, ref_fields=[]):
        
        self.malchemy = Session.connect(db, host=uri, timezone=pytz.utc)
        self.create_ok = create_ok
        self.db = self.malchemy.db
        self.docs = self.db[docs_collection]
        self.docs.ensure_index('_digest')
        self.pymongo = self.db.connection
        if safe:
            self.pymongo.db.write_concern = {'w': 1, 'j': True}
        if inc_manipulators:
            # NOTE: order is important here
            self.add_manipulator(DigestInjector(docs_collection))
            self.add_manipulator(DatetimeInjector(docs_collection))
            if len(ref_fields):
                self.add_manipulator(DereferenceManipulator(ref_fields))
    
    def add_manipulator(self, manipulator):
        self.db.add_son_manipulator(manipulator)
        
    def drop_database(self, database_name):
        self.pymongo.drop_database(database_name)
        
    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    def query(self, *args, **kwargs):
        return self.malchemy.query(*args, **kwargs)
    
    def insert(self, *args, **kwargs):
        return self.malchemy.insert(*args, **kwargs)
    
    def update(self, *args, **kwargs):
        return self.malchemy.update(*args, **kwargs)
    
    def iterate(self, model):
        q = self.malchemy.query(model)
        return self.malchemy.execute_query(q, self.malchemy)
    
    def get_doc(self, bibcode, manipulate=True):
        spec = {'_id': bibcode}
        return self.docs.find_one(spec, manipulate=manipulate)
        
    def docs_sources(self):
        if not hasattr(self, 'doc_source_models'):
            from adsdata.models import doc_source_models
            self.doc_source_models = list(doc_source_models())
        return self.doc_source_models
    
    def generate_doc(self, bibcode):
        doc = {'_id': bibcode}
        for model_class in self.docs_sources():
            model_class.add_docs_data(doc, self, bibcode)
        return doc
    
    def store_doc(self, doc):
        
        log = logging.getLogger()
        
        doc["_digest"] = doc_digest(doc, self.db)
        spec = {'_id': doc['_id'] } #, '_digest': digest}
        
        # look for existing doc 
        existing = self.docs.find_one(spec, manipulate=False)
        if existing:
            # do the digest values match?
            if existing.has_key("_digest") and existing["_digest"] == doc["_digest"]:
                # no change; do nothing
                log.debug("Digest match. No change to %s" % str(spec))
                return
            elif existing.has_key("_digest"):
                # add existing digest value to spec to avoid race conditions
                spec['_digest'] = existing["_digest"]
        
        # NOTE: even for cases where there was no existing doc we need to do an 
        # upsert to avoid race conditions
        return self.docs.update(spec, doc, manipulate=True, upsert=True)
            
class DatetimeInjector(SONManipulator):
    """
    Used for injecting/removing the datetime values of records in
    the docs collection
    """
    def __init__(self, collections=[]):
        self.collections = collections
        
    def transform_incoming(self, son, collection):
        if collection.name in self.collections:
            son['_dt'] = datetime.utcnow().replace(tzinfo=pytz.utc)
        return son
    
    def transform_outgoing(self, son, collection):
        if collection.name in self.collections:
            if son.has_key('_dt'):
                del son['_dt']
        return son
    
class DigestInjector(SONManipulator):
    """
    Inserts a digest hash of the contents of the doc being inserted
    """
    def __init__(self, collections=[]):
        self.collections = collections
        
    def transform_incoming(self, son, collection):
        if collection.name in self.collections:
            if not son.has_key('_digest'):
                son['_digest'] = doc_digest(son, collection.database)
        return son
    
    def transform_outgoing(self, son, collection):
        if collection.name in self.collections:
            if son.has_key('_digest'):
                del son['_digest']
        return son 
    
class DereferenceManipulator(SONManipulator):
    """
    Automatically de-references DBRef links to other docs
    """
    def __init__(self, ref_fields=[]):
        """
        ref_fields - a list of tuples in the form (collection, fieldname)
        where collection is the name of a collection to work on and fieldname
        is the document field that contains the DBRef values
        """
        self.ref_fields = {}
        for collection, field in ref_fields:
            self.ref_fields.setdefault(collection, [])
            self.ref_fields[collection].append(field)
        
    def transform_outgoing(self, son, collection):
        if collection.name in self.ref_fields:
            for field_name in self.ref_fields[collection.name]:
                dereference(son, collection.database, field_name)
        return son
    
def doc_digest(doc, db, hashtype='sha1'):
    """
    generate a digest hash from a 'docs' dictionary
    """
    # first make a copy
    digest_doc = doc.copy()
    
    # remove any 'meta' values
    for k in digest_doc.keys():
        if k.startswith('_'):
            del digest_doc[k]
        elif isinstance(digest_doc[k], DBRef):
            dereference(digest_doc, db, k)
            
    h = hashlib.new(hashtype)
    # sort_keys=True should make this deterministic?
    json = simplejson.dumps(digest_doc, sort_keys=True)
    h.update(json)
    return h.hexdigest()                

def dereference(son, db, field_name):
    """
    convert the DBRef value in 'field_name' to it's dereferenced value
    """
    db_ref = son.get(field_name)
    if not isinstance(db_ref, DBRef):
        return
    ref_doc = db.dereference(db_ref)
    son[field_name] = ref_doc.get(field_name)
    
