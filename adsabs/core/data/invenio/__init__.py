
from config import DefaultConfig as config
from urllib2 import quote
from urllib import urlencode

def record_url(recid, of=None):
    if not of:
        return config.INVENIO_BASEURL + '/record/' + quote(str(recid))
    else:
        return record_url(recid) + '?' + urlencode({'of': of})
        
