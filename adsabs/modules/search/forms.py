'''
Created on Sep 19, 2012

@author: jluker
'''

from flask.ext.wtf import (Form, SubmitField, TextField, SelectField, HiddenField, #@UnresolvedImport
                          ValidationError, validators, required, equal_to, email, #@UnresolvedImport
                          length) #@UnresolvedImport

from config import DefaultConfig as config

class QueryForm(Form):
    next = HiddenField()
    q = TextField('Query', [required(), length(min=2, max=2048)])
    rows = HiddenField(default=config.SOLR_DEFAULT_ROWS)
    submit = SubmitField('Search')
    
class ResultsQueryForm(QueryForm):
    rows = SelectField('Results Per Page', 
                       default=config.SOLR_DEFAULT_ROWS, 
                       choices=config.SOLR_ROW_OPTIONS)
    
class AdvancedQueryForm(ResultsQueryForm):
    pass