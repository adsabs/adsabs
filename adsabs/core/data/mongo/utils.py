'''
Created on Oct 11, 2012

@author: jluker
'''

import logging
log = logging.getLogger(__name__)
        
def map_reduce_listify(source, target_collection_name, key_field, value_field):
    from bson.code import Code

    map_func = Code("function(){ " \
                + "emit( this.%s, { '%s': [this.%s] } ); " % (key_field, value_field, value_field) \
            + "};")

    reduce_func = Code("function( key , values ){ " \
                + "var ret = { '%s': [] }; " % value_field \
                + "for ( var i = 0; i < values.length; i++ ) " \
                    + "ret['%s'].push.apply(ret['%s'],values[i]['%s']); " % (value_field, value_field, value_field) \
                + " return ret;" \
            + "};")

    log.info("running map-reduce on %s" % source.name)
    source.map_reduce(map_func, reduce_func, target_collection_name)
    source.update({}, {'$rename': {('value.%s' % value_field) : value_field}}, safe=True, multi=True)
    
