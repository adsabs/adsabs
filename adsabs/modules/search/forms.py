'''
Created on Sep 19, 2012

@author: jluker
'''

from flask.ext.wtf import (Form, SubmitField, TextField, SelectField, HiddenField, IntegerField, BooleanField,#RadioField, #@UnresolvedImport
                          ValidationError, validators, required, optional, equal_to, email, #@UnresolvedImport
                          length) #@UnresolvedImport
from flask.ext.wtf.html5 import RangeInput #@UnresolvedImport

from config import config
#from custom_wtform import SelectFieldCssClass



class QueryForm(Form):
    q = TextField(u'Query', [required(), length(min=2, max=2048)], description=u"Query the ADS database")
    #sort_dir = HiddenField(u'Sort direction', default='desc')
    db_key =  SelectField(u'Database', choices=[('ast', 'Astronomy'), ('phy', 'Physics'), ('all', 'All') ])
    sort_type = SelectField(u'Sort', choices=[('recent','Sort by Most recent'),('relevant','Sort by Most relevant'),
                                                        ('cited','Sort by Most cited'),('popular','Sort by Most popular'),
                                                        #('second_order_operator', 'Use Second order operator'),
                                                        ('hot','Explore What people are reading'),('useful','Explore What experts are citing'),
                                                        ('instructive','Explore Reviews and introductory papers ')] )
    month_from = IntegerField(u'Month From', [optional(), validators.NumberRange(min=1, max=12, message='Month not valid')])
    month_to = IntegerField(u'Month To', [optional(), validators.NumberRange(min=1, max=12, message='Month not valid')])
    year_from = IntegerField(u'Year From', [optional(), validators.NumberRange(min=1, max=2500, message='Year not valid')])
    year_to = IntegerField(u'Year To', [optional(), validators.NumberRange(min=1, max=2500, message='Year not valid')])
    journal_abbr = TextField(u'Bibstems', [optional(), length(min=2, max=2048)], description=u'Journal Abbreviation(s)')
    refereed = BooleanField(u'Refereed', description=u'Refereed only')
    article = BooleanField(u'Articles', description=u'Articles only')
    
    #second_order_type = RadioField(u'Explore the field', choices=[('hot','What people are reading'),('useful','What experts are citing'),
    #                                                   ('instructive','Reviews and introductory papers ')])
    #author = TextField('Author', [length(min=1, max=2048)], description="Author field search")
    #submit = SubmitField('Search', description="Search")
    
class ResultsQueryForm(QueryForm):
    rows = SelectField(u'Results Per Page', 
                       default=config.SOLR_DEFAULT_ROWS, 
                       choices=config.SOLR_ROW_OPTIONS)
    
class AdvancedQueryForm(ResultsQueryForm):
    pass