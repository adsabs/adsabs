'''
Created on Sep 18, 2012

@author: jluker
'''
import os
import sys
import csv
import pytz
import inspect
from bson import DBRef
from stat import ST_MTIME
from datetime import datetime
from mongoalchemy import fields
from mongoalchemy.document import Document, Index

import exceptions as exc
from config import config
from adsdata import utils

import logging
log = logging.getLogger(__name__)
    
def _get_models(cls):
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and cls in obj.__bases__:
            yield obj
    
def data_file_models():
    return _get_models(DataFileCollection)

def doc_source_models():
    return _get_models(DocsDataCollection)
        
class DataLoadTime(Document):
    
    config_collection_name = 'data_load_time'
    
    collection = fields.StringField()
    last_synced = fields.DateTimeField()
    
class DataCollection(Document):
    """
    This super class exists only to make it easy to collect and operate
    on all the various models via one base class
    """
    pass

class DocsDataCollection(DataCollection):
    
    docs_fields = []
    docs_ref_fields = []
    
    @classmethod
    def get_entry(cls, session, bibcode):
        collection = session.get_collection(cls.config_collection_name)
        return collection.find_one({'_id': bibcode})

    @classmethod
    def add_docs_data(cls, doc, session, bibcode):
        entry = cls.get_entry(session, bibcode)
        if entry:
            for field in cls.docs_fields:
                key = field.db_field
                doc[key] = entry.get(key)
            for ref_field in cls.docs_ref_fields:
                key = ref_field.db_field
                doc[key] = DBRef(collection=cls.config_collection_name, id=bibcode)
                
class Fulltext(DocsDataCollection):
    
    bibcode = fields.StringField(_id=True)
    full = fields.StringField()
    ack = fields.StringField(default=None)
    
    config_collection_name = "fulltext"
    docs_ref_fields = [full, ack]
    
    def __str__(self):
        return "Fulltext(%s)" % self.bibcode
    
class DataFileCollection(DataCollection):
    
    field_order = []
    aggregated = False
    restkey = "unwanted"
    
    @classmethod
    def last_synced(cls, session):
        collection_name = cls.config_collection_name
        dlt = session.query(DataLoadTime).filter(DataLoadTime.collection == collection_name).first()
        if not dlt:
            return None
        log.debug("%s last synced: %s" % (collection_name, dlt.last_synced))
        return dlt.last_synced
    
    @classmethod
    def last_modified(cls):
        collection_name = cls.config_collection_name
        source_file = cls.get_source_file()
        log.debug("checking freshness of %s collection vs %s" % (collection_name, source_file))
        modified = datetime.fromtimestamp(os.stat(source_file)[ST_MTIME]).replace(tzinfo=pytz.utc)
        log.debug("%s last modified: %s" % (source_file, modified))
        return modified
        
    @classmethod
    def needs_sync(cls, session):
        """
        compare the modification time of a data source
        to its last_synced time in the data_load_time collection
        """
        collection_name = cls.config_collection_name
        last_modified = cls.last_modified()
        last_synced = cls.last_synced(session)
        
        if not last_synced or last_modified > last_synced:
            log.debug("%s needs updating" % collection_name)
            return True
        else:
            log.debug("%s does not need updating" % collection_name)
            return False
        
    @classmethod
    def get_source_file(cls):
        collection_name = cls.config_collection_name
        try:
            return config.MONGO_DATA_COLLECTIONS[collection_name]
        except:
            raise exc.ConfigurationError("No source file configured for %s" % collection_name)
        
    @classmethod
    def load_data(cls, session, batch_size=1000, source_file=None, partial=False):
        """
        batch load entries from a data file to the corresponding mongo collection
        """
        
        collection_name = cls.config_collection_name
        if cls.aggregated:
            load_collection_name = collection_name + '_load'
        else:
            load_collection_name = collection_name
        collection = session.get_collection(load_collection_name)
        collection.drop()
        log.debug("loading data into %s" % load_collection_name)
        
        if not source_file:
            source_file = cls.get_source_file()
        
        def get_collection_field_name(field):
            if field.is_id and cls.aggregated:
                return "load_key"
            else:
                return field.db_field
            
        try:
            fh = open(source_file, 'r')
        except IOError, e:
            log.error(str(e))
            return

        field_names = [get_collection_field_name(x) for x in cls.field_order]
        reader = csv.DictReader(fh, field_names, delimiter="\t", restkey=cls.restkey, restval="")
        
        cls.insert_records(reader, collection, batch_size)
        
        log.debug("done loading %d records into %s" % (collection.count(), load_collection_name))

        cls.post_load_data(session, collection)
        
        dlt = DataLoadTime(collection=collection_name, last_synced=datetime.utcnow().replace(tzinfo=pytz.utc))
        session.update(dlt, DataLoadTime.collection == collection_name, upsert=True)
        log.debug("%s load time updated to %s" % (collection_name, str(dlt.last_synced)))
        
    @classmethod
    def insert_records(cls, reader, collection, batch_size):
        log.debug("inserting records into %s..." % collection.name)
        
        batch = []
        batch_num = 1
        while True:
            try:
                record = reader.next()
                if record.has_key('unwanted'):
                    del record['unwanted']
            except StopIteration:
                break
            cls.coerce_types(record)
            batch.append(record)
            if len(batch) >= batch_size:
                log.debug("inserting batch %d into %s" % (batch_num, collection.name))
                collection.insert(batch, safe=True)
                batch = []
                batch_num += 1

        if len(batch):
            log.debug("inserting final batch into %s" % collection.name)
            collection.insert(batch, safe=True)

    @classmethod
    def coerce_types(cls, record):
        """
        given a dict produced by the csv DictReader, will transorm the
        any string values to int or float according to the types defined in the model
        """
        convert_types = [int, float]
        
        def get_constructor(field):
            if hasattr(field, 'constructor'):
                return field.constructor
            else:
                if hasattr(field, 'child_type'):
                    item_type = model_field.child_type()
                elif hasattr(field, 'item_type'):
                    item_type = field.item_type
                return item_type.constructor
            return None
                
        for k, v in record.iteritems():
            # assume id's are strings and we don't need to process
            # (_id field is called "load_key" for aggregated collections
            if k in ['_id','load_key']: 
                continue
            if not v: 
                continue
            model_field = cls.get_fields()[k]
            constructor = get_constructor(model_field)
            if constructor and constructor in convert_types:
                if type(v) is list:
                    record[k] = [constructor(x) for x in v]
                else:
                    record[k] = constructor(v)
        
    @classmethod
    def post_load_data(cls, *args, **kwargs):
        """
        this method gets called immediately following the data load.
        subclasses should override to do things like generate
        new collections using map-reduce on the original data
        """
        pass
    

    
class Bibstem(DataFileCollection):
    bibstem = fields.StringField()
    type_code = fields.EnumField(fields.StringField(), "R", "J", "C")
    journal_name = fields.StringField()
    
    config_collection_name = 'bibstems'
    field_order = [bibstem,type_code,journal_name]
    
    def __str__(self):
        return "Bibstem(%s): %s (%s)" % (self.bibstem, self.journal_name, self.type_code)
    
class FulltextLink(DataFileCollection):
    bibcode = fields.StringField(_id=True)
    fulltext_source = fields.StringField()
    database = fields.StringField(default="")
    provider = fields.StringField(default="")
    
    config_collection_name = 'fulltext_links'
    field_order = [bibcode,fulltext_source,database,provider]
    
    def __str__(self):
        return "FulltextLink(%s): %s" % (self.bibcode, self.fulltext_source)

class Readers(DataFileCollection, DocsDataCollection):
    
    bibcode = fields.StringField(_id=True)
    readers = fields.ListField(fields.StringField())
    
    aggregated = True
    config_collection_name = 'readers'
    field_order = [bibcode, readers]
    docs_fields = [readers]
    
    def __str__(self):
        return "Readers(%s): [%s]" % (self.bibcode, self.readers)
    
    @classmethod
    def post_load_data(cls, session, source_collection):
        target_collection_name = cls.config_collection_name
        utils.map_reduce_listify(session, source_collection, target_collection_name, 'load_key', 'readers')
    
class References(DataFileCollection):
    
    bibcode = fields.StringField(_id=True)
    references = fields.ListField(fields.StringField())
    
    aggregated = True
    config_collection_name = 'references'
    field_order = [bibcode, references]
    
    def __str__(self):
        return "References(%s): [%s]" % (self.bibcode, self.references)
    
    @classmethod
    def post_load_data(cls, session, source_collection):
        target_collection_name = cls.config_collection_name
        utils.map_reduce_listify(session, source_collection, target_collection_name, 'load_key', 'references')

class Citations(DataFileCollection):
    
    bibcode = fields.StringField(_id=True)
    citations = fields.ListField(fields.StringField())
    
    aggregated = True
    config_collection_name = 'citations'
    field_order = [bibcode, citations]
    
    def __str__(self):
        return "Citations(%s): [%s]" % (self.bibcode, self.citations)
    
    @classmethod
    def post_load_data(cls, session, source_collection):
        target_collection_name = cls.config_collection_name
        utils.map_reduce_listify(session, source_collection, target_collection_name, 'load_key', 'citations')
    
class Refereed(DataFileCollection, DocsDataCollection):

    bibcode = fields.StringField(_id=True)
    
    config_collection_name = 'refereed'
    field_order = [bibcode]
    docs_fields = [bibcode]
    
    @classmethod
    def add_docs_data(cls, doc, session, bibcode):
        entry = cls.get_entry(session, bibcode)
        if entry:
            doc['refereed'] = True
                
    def __str__(self):
        return "Refereed(%s)" % self.bibcode
    
class DocMetrics(DataFileCollection, DocsDataCollection):
    bibcode = fields.StringField(_id=True)
    boost = fields.FloatField(default=0.0)
    citation_count = fields.IntField(default=0)
    read_count = fields.IntField(default=0)
    
    config_collection_name = 'docmetrics'
    field_order = [bibcode,boost,citation_count,read_count]
    docs_fields = [boost, citation_count, read_count]
    
    def __str__(self):
        return "DocMetrics(%s): %s, %s, %s" % (self.bibcode, self.boost, self.citations, self.reads)
    
class Accno(DataFileCollection):

    bibcode = fields.StringField(_id=True)
    accno = fields.StringField()

    config_collection_name = 'accnos'
    field_order = [bibcode,accno]

    def __str__(self):
        return "Accno(%s): %s" % (self.bibcode, self.accno)
    
class EprintMatches(DataFileCollection):

    ecode = fields.StringField(_id=True)
    bibcode = fields.StringField()

    config_collection_name = 'eprint_matches'
    field_order = [ecode,bibcode]

    def __str__(self):
        return "EprintMatches(%s): %s" % (self.ecode, self.bibcode)

class EprintMapping(DataFileCollection):

    arxivid = fields.StringField(_id=True)
    bibcode = fields.StringField()

    config_collection_name = 'eprint_mapping'
    field_order = [bibcode,arxivid]

    def __str__(self):
        return "EprintMapping(%s): %s" % (self.arxivid, self.bibcode)

class Reads(DataFileCollection, DocsDataCollection):

    bibcode = fields.StringField(_id=True)
    reads   = fields.ListField(fields.IntField())

    restkey = 'reads'

    config_collection_name = 'reads'
    field_order = [bibcode]
    docs_fields = [reads]

    def __str__(self):
        return "Reads(%s)" % self.bibcode
        
class Downloads(DataFileCollection, DocsDataCollection):

    bibcode = fields.StringField(_id=True)
    downloads = fields.ListField(fields.IntField())

    restkey = 'downloads'

    config_collection_name = 'downloads'
    field_order = [bibcode]
    docs_fields = [downloads]

    def __str__(self):
        return "Downloads(%s)" % self.bibcode
    
class Grants(DataFileCollection, DocsDataCollection):
    
    bibcode = fields.StringField(_id=True)
    agency = fields.StringField()
    grant = fields.StringField()
    grants = fields.ListField(fields.DictField(fields.StringField()))
    
    aggregated = True
    config_collection_name = "grants"
    field_order = [bibcode, agency, grant]
    docs_fields = [grants]
    
    @classmethod
    def post_load_data(cls, session, source_collection):
        target_collection_name = cls.config_collection_name
        utils.map_reduce_dictify(session, source_collection, target_collection_name, 'load_key', ['agency','grant'], 'grants')
    
    def __str__(self):
        return "Grants(%s): %s, %s" % (self.bibcode, self.agency, self.grant)


