
from config import DefaultConfig as config
from urllib2 import quote

def abstract_url(bibcode):
    return config.ADS_CLASSIC_BASEURL + '/abs/' + quote(bibcode)
        
