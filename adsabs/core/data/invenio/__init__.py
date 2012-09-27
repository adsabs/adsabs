
from config import config
from urllib2 import quote
from urllib import urlencode

import logging
log = logging.getLogger(__name__)

try:
    from invenio.search_engine import get_record #@UnresolvedImport
    from invenio.bibrecord import record_xml_output #@UnresolvedImport
    from invenio.dbquery import run_sql #@UnresolvedImport
except ImportError:
    log.warn("Invenio import failure! Invenio data layer functions will not work!")
    

def record_url(recid, of=None):
    if not of:
        return config.INVENIO_BASEURL + '/record/' + quote(str(recid))
    else:
        return record_url(recid) + '?' + urlencode({'of': of})
        
def get_abstract_xml_from_ads_id(self, ads_id):
    """
    Simple method that returns 
    """
    query_record_id = 'SELECT rec03.id_bibrec FROM bibrec_bib03x AS rec03 JOIN bib03x ON rec03.id_bibxxx = bib03x.id \
    WHERE bib03x.value="%(ads_id)s" UNION SELECT rec02.id_bibrec FROM bibrec_bib02x AS rec02 \
    JOIN bib02x ON rec02.id_bibxxx = bib02x.id WHERE bib02x.value="%(ads_id)s"' % {'ads_id': ads_id}
    
    try:
        record_id = run_sql(query_record_id)[0][0]
    except IndexError:
        record_id = None
        
    if record_id:
        return record_xml_output(get_record(record_id)).replace('\n', '')
    else:
        return None
        