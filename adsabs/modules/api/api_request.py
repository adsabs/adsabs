'''
Created on Nov 2, 2012

@author: jluker
'''
import re
import sys
from flask import g #@UnresolvedImport
from flask.ext.solrquery import solr, SearchRequest #@UnresolvedImport

from config import config
from .forms import ApiQueryForm
from api_errors import ApiPermissionError,ApiSolrException
    
__all__ = ['ApiSearchRequest','ApiRecordRequest']

class ApiSearchRequest(object):
    
    def __init__(self, request_vals):
        self.form = ApiQueryForm(request_vals, csrf_enabled=False)
        self.user = g.api_user
        
    def validate(self):
        valid = self.form.validate()
        perms_ok = self.user.check_permissions(self.form)
        return valid and perms_ok
    
    def input_errors(self):
        return self.form.errors
    
    def _create_search_request(self):
        req = SearchRequest(self.form.q.data)
        
        if self.form.fl.data:
            fields = list(set(self.form.fl.data.split(',') + config.SOLR_SEARCH_REQUIRED_FIELDS))
        else:
            fields = self.user.get_allowed_fields()

        # TODO: this is a short term hack
        if '[citations]' in fields:
            fields.remove('[citations]')

        req.set_fields(fields)
            
        if self.form.rows.data:
            req.set_rows(self.form.rows.data)
        else:
            req.set_rows(config.SEARCH_DEFAULT_ROWS)
            
        if self.form.start.data:
            req.set_start(self.form.start.data)
            
        if self.form.sort.data:
            sort_tokens = re.split('[\s,]+', self.form.sort.data)
            # tupleize the list into field,direction pairs
            sort_tokens = zip(*[iter(sort_tokens)] * 2)
            for sort, direction in sort_tokens:
                sort_field = config.SEARCH_SORT_OPTIONS_MAP[sort][0]
                req.add_sort(sort_field, direction)
        else:
            for field, direction in config.API_SOLR_DEFAULT_SORT:
                req.add_sort(field, direction)
                
        if len(self.form.facet.data):
            for facet in self.form.facet.data:
                facet = facet.split(':')
                api_facet_name = facet[0]
                solr_field_name = config.API_SOLR_FACET_FIELDS[api_facet_name]
                if api_facet_name != solr_field_name:
                    # translate api facet name to solr field name in request *and* response
                    # see http://wiki.apache.org/solr/SimpleFacetParameters#key_:_Changing_the_output_key
                    output_key = api_facet_name
                    facet[0] = solr_field_name
                else:
                    output_key = None
                req.add_facet(*facet, output_key=output_key)
        
        if len(self.form.hl.data):
            for hl in self.form.hl.data:
                req.add_highlight(hl.split(':'))
                
        if len(self.form.filter.data):
            for fltr in self.form.filter.data:
                req.add_filter_query(fltr)
                
        if self.form.hlq.data:
            req.set_hlq(self.form.hlq.data)
            
        return req
                
    def execute(self):
        req = self._create_search_request()
        
        try:
            resp = solr.get_response(req)
        except Exception, e:
            from adsabs.core.solr import AdsabsSolrqueryException
            raise AdsabsSolrqueryException("Error communicating with search service", sys.exc_info())
        
        if resp.is_error():
            raise ApiSolrException(resp.get_error())
        
        resp.add_meta('api-version', g.api_version)
        self.resp = resp
        return self.resp

    def query(self):
        return self.form.q.data
    
class ApiRecordRequest(ApiSearchRequest):
    
    def __init__(self, identifier, request_vals):
        self.record_id = identifier
        ApiSearchRequest.__init__(self, request_vals)
        
    def _create_search_request(self):
        q = "identifier:%s OR doi:%s" % (self.record_id, self.record_id)
        req = SearchRequest(q, rows=1)
        
        if self.form.fl.data:
            fields = list(set(self.form.fl.data.split(',') + config.SOLR_SEARCH_REQUIRED_FIELDS))
            req.set_fields(fields)
        else:
            req.set_fields(self.user.get_allowed_fields())
            
        if len(self.form.hl.data):
            for hl in self.form.hl.data:
                hl = hl.split(':')
                req.add_highlight(*hl)
                
        if self.form.hlq.data:
            req.set_hlq(self.form.hlq.data)
            
        return req
    
