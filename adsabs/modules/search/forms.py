'''
Created on Sep 19, 2012

@author: jluker
'''
import re
from flask.ext.wtf import Form #@UnresolvedImport
from wtforms import (TextField, SelectField, IntegerField, BooleanField, HiddenField, #SubmitField, RadioField, #@UnresolvedImport
                          validators, widgets) #@UnresolvedImport
from wtforms.validators import (required, optional, length)
from werkzeug.datastructures import ImmutableMultiDict, MultiDict
from config import config


__all__ = ["QueryForm", "AdvancedQueryForm"]

class MultiFacetSelectField(SelectField):

    """
    custom field that is able to correctly validate input coming from multi-facet selection.
    e.g., a user selects both "astronomy" and "phyiscs" database in facets; value of db_f
    field would be '("astronomy" AND "physics")'
    """
    def pre_validate(self, form):
        if not len(self.data):
            return
        values = re.split("(?:OR|AND)", self.data)
        values = map(lambda x: x.strip(' "()'), values)
        choices = [x[0] for x in self.choices]
        for v in values:
            if v not in choices:
                raise ValueError("Not a valid choice")
        
class QueryForm(Form):
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.method = 'GET'
        self.flask_route = 'search.search'
        self.__includes = []
    
    default_if_missing = MultiDict([('db_f', ''), ])

    @classmethod
    def init_with_defaults(cls, request_values):
        """Function that given a form object and a set of parameters coming from the request
        populate the parameters with the default values of the form if they are not in the request"""
        
        #I convert the ImmutableMultiDict into MultiDict
        request_values = MultiDict(request_values)
        defaults = cls.default_if_missing

        for field in defaults.keys():
            if not request_values.has_key(field):
                for elem in defaults.getlist(field):
                    request_values.add(field, elem)

        params = ImmutableMultiDict(request_values)
        return cls(params, csrf_enabled=False)
        
    """Form for the basic search"""
    q = TextField(u'Query', [required(), length(min=1, max=2048)], description=u"Query the ADS database")

    # make this hidden since we'll use database selection from the facets
    db_f =  MultiFacetSelectField(u'Database', choices=[('astronomy', 'astronomy'), ('physics', 'physics'), ('(astronomy OR physics)', 'astronomy & physics'), ('', 'all') ], description=u'Database', default=config.SEARCH_DEFAULT_DATABASE)

    month_from = IntegerField(u'Month From', [optional(), validators.NumberRange(min=1, max=12, message='Starting month not valid: allowed values from 01 to 12')])
    month_to = IntegerField(u'Month To', [optional(), validators.NumberRange(min=1, max=12, message='Ending month not valid: allowed values from 01 to 12')])
    year_from = IntegerField(u'Year From', [optional(), validators.NumberRange(min=1, max=2500, message='Starting year not valid')])
    year_to = IntegerField(u'Year To', [optional(), validators.NumberRange(min=1, max=2500, message='Ending year not valid')])
    article = BooleanField(u'Articles', description=u'Articles only')
    nr = IntegerField(u'Number of Records', [optional(), validators.NumberRange(min=10, max=3000, message="Please enter a number between 10 and 3000")], description='Number of Records') #, default=config.SEARCH_DEFAULT_ROWS)
    topn = IntegerField(u'Return top N results', [optional(), validators.NumberRange(min=1, message='TopN must be an integer bigger than 1')])
    no_ft = BooleanField(u'Disable full text', description=u'Disable fulltext')
    bigquery = HiddenField(u'Custom Query')
    
    def add_rendered_element(self, string):
        self.__includes.append(string)
    
    def has_rendered_elements(self):
        return len(self.__includes) > 0
    
    def get_rendered_elements(self):
        return self.__includes
   
class AdvancedQueryForm(QueryForm):
    pass
