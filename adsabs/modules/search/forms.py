'''
Created on Sep 19, 2012

@author: jluker
'''

from flask.ext.wtf import (Form, SubmitField, TextField, SelectField, HiddenField, IntegerField, BooleanField,#RadioField, #@UnresolvedImport
                          ValidationError, validators, required, optional, equal_to, email, #@UnresolvedImport
                          length) #@UnresolvedImport
from werkzeug.datastructures import ImmutableMultiDict, MultiDict
#from flask.ext.wtf.html5 import RangeInput #@UnresolvedImport

from config import config
#from custom_wtform import SelectFieldCssClass

__all__ = ["get_missing_defaults", "QueryForm", "AdvancedQueryForm"]

def get_missing_defaults(req_val_lists, form):
    """Function that given a form object and a set of parameters coming from the request
    populate the parameters with the default values of the form if they are not in the request"""
    
    #I convert the ImmutableMultiDict into MultiDict
    req_val_lists = MultiDict(req_val_lists)
    try:
        form_defaults = form.default_if_missing
    except AttributeError:
        return ImmutableMultiDict(req_val_lists)
    for field in form_defaults.keys():
        if not req_val_lists.has_key(field):
            for elem in form_defaults.getlist(field):
                req_val_lists.add(field, elem)
    return ImmutableMultiDict(req_val_lists)
    


class QueryForm(Form):
    """Form for the basic search"""
    q = TextField(u'Query', [required(), length(min=1, max=2048)], description=u"Query the ADS database")
    #sort_dir = HiddenField(u'Sort direction', default='desc')
    db_key =  SelectField(u'Database', choices=[('ASTRONOMY', 'Astronomy'), ('PHYSICS', 'Physics'), ('ALL', 'All') ])
    sort_type = SelectField(u'Sort', choices=[('DATE','Sort by Most recent'),('RELEVANCE','Sort by Most relevant'),
                                                ('CITED','Sort by Most cited'),('POPULARITY','Sort by Most popular'),
                                                #('second_order_operator', 'Use Second order operator'),
                                                #('hot','Explore What people are reading'),('useful','Explore What experts are citing'),
                                                #('instructive','Explore Reviews and introductory papers ')
                                                ] )
    month_from = IntegerField(u'Month From', [optional(), validators.NumberRange(min=1, max=12, message='Starting month not valid: allowed values from 01 to 12')])
    month_to = IntegerField(u'Month To', [optional(), validators.NumberRange(min=1, max=12, message='Ending month not valid: allowed values from 01 to 12')])
    year_from = IntegerField(u'Year From', [optional(), validators.NumberRange(min=1, max=2500, message='Starting year not valid')])
    year_to = IntegerField(u'Year To', [optional(), validators.NumberRange(min=1, max=2500, message='Ending year not valid')])
    journal_abbr = TextField(u'Bibstems', [optional(), length(min=2, max=2048)], description=u'Journal Abbreviation(s)')
    refereed = BooleanField(u'Refereed', description=u'Refereed only')
    article = BooleanField(u'Articles', description=u'Articles only')
    
    default_if_missing = MultiDict([('db_key', 'ASTRONOMY'), ('sort_type', 'DATE')])
    
    
    #second_order_type = RadioField(u'Explore the field', choices=[('hot','What people are reading'),('useful','What experts are citing'),
    #                                                   ('instructive','Reviews and introductory papers ')])
    #author = TextField('Author', [length(min=1, max=2048)], description="Author field search")
    #submit = SubmitField('Search', description="Search")
    
class AdvancedQueryForm(QueryForm):
    pass