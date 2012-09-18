'''
Created on Aug 29, 2012

@author: jluker
'''
import logging
from config import DefaultConfig as config
from sunburnt import SolrInterface

log = logging.getLogger(__name__)
instance = {'solr': None}

def init_solr(url=None, **kwargs):
    if not url:
        url = config.SOLR_URL
    log.info("Initializing solr connection to %s" % url)
    try:
        instance['solr'] = SolrInterface(url, mode='r', **kwargs)
        return instance['solr']
    except Exception, e:
        raise SolrConnectionError("%s: %s" % (type(e), str(e)))

def get_solr():
    if instance['solr'] is None:
        init_solr()
    return instance['solr']
    
class SolrConnectionError(Exception):
    pass
