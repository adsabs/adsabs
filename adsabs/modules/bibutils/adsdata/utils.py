'''
Created on Oct 11, 2012

@author: jluker
'''

import os
import sys
from jinja2 import Template
from datetime import datetime

import logging
log = logging.getLogger(__name__)
        
def init_logging(logfile, verbose=False, debug=False):
    logfile = logfile + "." + datetime.now().strftime("%Y%m%d-%H%M%S")
    logging.basicConfig(
        filename = logfile, 
        level = logging.INFO,
        format = '%(asctime)s %(levelname)s %(message)s'
    )
    log = logging.getLogger()
    log.debug("logging to %s" % logfile)
    if verbose:
        log.addHandler(logging.StreamHandler(sys.stdout))
        log.debug("logging to stdout")
    if debug:
        log.setLevel(logging.DEBUG)
        fmt = logging.Formatter('%(asctime)s %(levelname)s %(thread)d %(filename)s %(lineno)d %(message)s')
        for h in log.handlers:
            h.setFormatter(fmt)
        log.debug("debug level logging enabled")
    return log

def commandList():
    """
    decorator that allows scripts to register functions to be used as script commands
    """
    registry = {}
    def registrar(func):
        registry[func.__name__] = func
        return func
    registrar.map = registry
    return registrar

def mongo_uri(host, port, db=None, user=None, passwd=None):
    if user and passwd:
        uri = "mongodb://%s:%s@%s:%d/%s" % (user, passwd, host, port, db)
    else:
        uri = "mongodb://%s:%d" % (host, port)
    return uri

def get_session(**kwargs):
    from config import config
    from session import DataSession
    uri = mongo_uri(config.MONGO_HOST, config.MONGO_PORT, 
                    db=config.MONGO_DATABASE, user=config.MONGO_USER, passwd=config.MONGO_PASSWORD)
    return DataSession(config.MONGO_DATABASE, uri, 
                       config.MONGO_DOCS_COLLECTION, 
                       ref_fields=config.MONGO_DOCS_DEREF_FIELDS,
                       **kwargs) 

def map_reduce_listify(session, source, target_collection_name, group_key, value_field):
    """
    Will take a 1:many key:value collection and aggregate values in a list by unique key
    """
    from bson.code import Code

    map_func = Code("function(){ " \
                + "emit( this.%s, { '%s': [this.%s] } ); " % (group_key, value_field, value_field) \
            + "};")

    reduce_func = Code("function( key , values ){ " \
                + "var ret = { '%s': [] }; " % value_field \
                + "for ( var i = 0; i < values.length; i++ ) " \
                    + "ret['%s'].push.apply(ret['%s'],values[i]['%s']); " % (value_field, value_field, value_field) \
                + " return ret;" \
            + "};")

    log.info("running map-reduce on %s" % source.name)
    source.map_reduce(map_func, reduce_func, target_collection_name)
    
    target = session.get_collection(target_collection_name)
    log.info("cleaning up target collection: %s" % target_collection_name)
    target.update({}, {'$rename': {('value.' + value_field) : value_field}}, multi=True)
    target.update({}, {'$unset': { 'value': 1 }}, multi=True)
    source.drop()

def map_reduce_dictify(session, source, target_collection_name, group_key, value_fields, output_key=None):
    """
    Will take a 1:many key:multiple-values collection and aggregate values in a list of dicts
    by unique key
    """
    from bson.code import Code
    if not output_key:
        output_key = target_collection_name
    
    emit_vals = ','.join(["'%s': this.%s" % (x,x) for x in value_fields])
    map_func = Template("""
        function() {
            emit( this.{{ group_key }}, { '{{ output_key }}': [{ {{ emit_vals }} }] });
        };
    """).render(group_key=group_key, emit_vals=emit_vals, output_key=output_key)
    
    reduce_func = Template("""
        function(key, values) {
            var ret = { '{{ output_key }}': [] };
            for ( var i = 0; i < values.length; i++ ) {
                ret['{{ output_key }}'].push.apply(ret['{{ output_key }}'], values[i]['{{ output_key }}']);
            }
            return ret;
        };
    """).render(output_key=output_key)
    
    log.info("running map-reduce on %s" % source.name)
    source.map_reduce(map_func, reduce_func, target_collection_name)
    
    target = session.get_collection(target_collection_name)
    log.info("cleaning up target collection: %s" % target_collection_name)
    target.update({}, {'$rename': {('value.' + output_key) : output_key}}, multi=True)
    target.update({}, {'$unset': { 'value': 1 }}, multi=True)
    source.drop()
    
