
#invenio imports for the different methods of the interface class
from invenio.search_engine import get_record
from invenio.bibrecord import record_xml_output
from invenio.dbquery import run_sql

class invenioInterface(object):
    """
    Flask extension to interface Invenio
    If we need to extract something from Invenio, we should write a method here and not create connections all around the app
    """
    
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
        
