'''
Created on Sep 19, 2012

@author: jluker
'''

from flask import g
from flask.ext.wtf import Form, fields, validators, ValidationError #@UnresolvedImport

from adsabs.core.solr import SolrRequest
from config import config

MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 2048

def api_defaults(*args, **kwargs):
    pass

def validate_query(form, field):
    if len(field.data) < MIN_QUERY_LENGTH:
        raise ValidationError("'q' input must be at least %s characters" % MIN_QUERY_LENGTH)
    if len(field.data) > MAX_QUERY_LENGTH:
        raise ValidationError("'q' input must be at no more than %s characters" % MIN_QUERY_LENGTH)
    fields_queried = SolrRequest.parse_query_fields(field.data)
    
class ApiQueryForm(Form):
    q = fields.TextField('query', [validators.Required(), validate_query])
    dev_key = fields.TextField('dev_key', default=None)
    rows = fields.IntegerField('rows', default=api_defaults)
    start = fields.IntegerField('start', default=api_defaults)
    sort = fields.TextField('sort', default=api_defaults)
    format = fields.TextField('format', default=api_defaults)
    facets = fields.BooleanField('facets', default=api_defaults)
    highlights = fields.BooleanField('highlights', default=api_defaults)
    