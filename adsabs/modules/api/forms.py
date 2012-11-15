'''
Created on Sep 19, 2012

@author: jluker
'''

from flask.ext.wtf import Form, fields, validators #@UnresolvedImport

from config import config

def api_defaults(*args, **kwargs):
    pass

class ApiQueryForm(Form):
    q = fields.TextField('query', validators=[validators.required(), validators.length(min=2, max=2048)])
    dev_key = fields.TextField('dev_key', default=None)
    rows = fields.IntegerField('rows', default=api_defaults)
    start = fields.IntegerField('start', default=api_defaults)
    sort = fields.TextField('sort', default=api_defaults)
    format = fields.TextField('format', default=api_defaults)
    facets = fields.BooleanField('facets', default=api_defaults)
    highlights = fields.BooleanField('highlights', default=api_defaults)
    