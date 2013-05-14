
from config import config
from urllib2 import quote
from urllib import urlencode

from .inveniodoc import InvenioDoc

try:
    from invenio.search_engine import get_record #@UnresolvedImport
    from invenio.bibrecord import record_xml_output #@UnresolvedImport
    from invenio.dbquery import run_sql #@UnresolvedImport
except ImportError:
    import sys
    print >>sys.stderr, "Invenio import failure! Invenio data layer functions will not work!"

__all__ = ['record_url', 'get_abstract_xml_from_ads_id', 'get_records', 'get_metadata', 'get_invenio_metadata']

def record_url(recid, of=None):
    if not of:
        return config.INVENIO_BASEURL + '/record/' + quote(str(recid))
    else:
        return record_url(recid) + '?' + urlencode({'of': of})
        
def get_abstract_xml_from_ads_id(ads_id):
    """
    Simple method that returns the marcxml for a bibcode
    """
    query_record_id = 'SELECT rec03.id_bibrec FROM bibrec_bib03x AS rec03 JOIN bib03x ON rec03.id_bibxxx = bib03x.id \
    WHERE bib03x.value="%(ads_id)s" UNION SELECT rec02.id_bibrec FROM bibrec_bib02x AS rec02 \
    JOIN bib02x ON rec02.id_bibxxx = bib02x.id WHERE bib02x.value="%(ads_id)s"' % {'ads_id': ads_id}
    
    try:
        record_id = run_sql(query_record_id)[0][0]
    except IndexError:
        return None
        
    if record_id:
        return record_xml_output(get_record(record_id)).replace('\n', '')
        
def get_records(invenio_record_id_list):
    """
    Returns a list of bibrecords given a list of record ids
    """
    return [get_record(record_id) for record_id in invenio_record_id_list]
    

def get_metadata(invenio_record_id_list):
    """
    Returns the additional metadata needed for the result list and the abstract
    """
    def author_bibrec_to_dict(author_bibrec):
        """Converts an author in the bibrecord format to a dictionary"""
        author = {'name': None, 'normalized_name':None, 'type':None, 'native_name':None, 'affiliations':[], 'emails':[]}
        for elem in author_bibrec:
            if elem[0] == 'a':
                author['name'] = elem[1].decode('utf8')
            elif elem[0] == 'b':
                author['normalized_name'] = elem[1].decode('utf8')
            elif elem[0] == 'e':
                author['type'] = elem[1]
            elif elem[0] == 'q':
                author['native_name'] = elem[1].decode('utf8')
            elif elem[0] == 'u':
                author['affiliations'].append(elem[1].decode('utf8'))
            elif elem[0] == 'm':
                author['emails'].append(elem[1])
        return author
    
    #I retrieve the medatata
    bibrecords_list = get_records(invenio_record_id_list)
    
    records_metadata = {}
    for bibrecord in bibrecords_list:
        if bibrecord:
            #bibrecord_id
            if bibrecord.get('001'):
                bibrecord_id = long(bibrecord.get('001')[0][3])
            else:
                continue
            #author_list
            author = tuple()
            if bibrecord.get('100'):
                author += (author_bibrec_to_dict(bibrecord.get('100')[0][0]), )
            if bibrecord.get('700'):
                for aut_rec in bibrecord.get('700'):
                    author += (author_bibrec_to_dict(aut_rec[0]), )
            #title
            title = ''
            if bibrecord.get('245'):
                field = bibrecord.get('245')[0][0]
                for elem in field:
                    if elem[0] == 'a':
                        title = elem[1].decode('utf8')
            #bibcode
            bibcode = ''
            if bibrecord.get('970'):
                field = bibrecord.get('970')[0][0]
                for elem in field:
                    if elem[0] == 'a':
                        bibcode = elem[1]
            #keywords
            keyword = {'free':[], 'controlled':{}}
            #first free
            if bibrecord.get('653'):
                for record in bibrecord.get('653'):
                    #the subfields of the keywords are not repeatable, so I can convert them in a dictionary
                    sub_dict = dict(record[0])
                    #the free keyword don't have a schema so they don't need to be split
                    keyword['free'].append({'keyword':sub_dict.get('a').decode('utf8'), 'norm_keyword':sub_dict.get('b').decode('utf8')})
            if bibrecord.get('695'):
                for record in bibrecord.get('695'):
                    #the subfields of the keywords are not repeatable, so I can convert them in a dictionary
                    sub_dict = dict(record[0])
                    keyword['controlled'].setdefault(sub_dict.get('2').decode('utf8'), []).append({'keyword':sub_dict.get('a').decode('utf8'), 'norm_keyword':sub_dict.get('b').decode('utf8')})
            
            #finally I append all the metadata I've retrieved
            records_metadata[bibrecord_id] = {'author':author, 'title':title, 'bibcode':bibcode, 'keyword':keyword}
    return records_metadata
                
            
def get_invenio_metadata(ads_id):
    """
    Returns an inveniodoc object given an ads record id
    """
    query_record_id = 'SELECT rec03.id_bibrec FROM bibrec_bib03x AS rec03 JOIN bib03x ON rec03.id_bibxxx = bib03x.id \
    WHERE bib03x.value="%s"' % ads_id
    try:
        record_id = run_sql(query_record_id)[0][0]
    except IndexError:
        return InvenioDoc({})
    
    metadata = get_metadata([record_id])
    if not metadata.get(record_id):
        return InvenioDoc({})
    return InvenioDoc(metadata.get(record_id))
    
    
    