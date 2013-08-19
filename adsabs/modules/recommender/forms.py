'''
Created on Jul 16, 2013

@author: ehenneken
'''

from flask.ext.wtf import Form, TextAreaField, BooleanField, RadioField, SelectField
from flask.ext.wtf import Required

__all__ = ['CitationHelperInputForm',]

class SuggestionsInputForm(Form):
    """
    Definition of input form for Metrics
    """
    bibcodes = TextAreaField('bibcodes')