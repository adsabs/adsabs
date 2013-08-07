'''
Created on Jul 16, 2013

@author: ehenneken
'''

from flask.ext.wtf import Form, TextAreaField, BooleanField, RadioField, SelectField
from flask.ext.wtf import Required

__all__ = ['CitationHelperInputForm',]

class CitationHelperInputForm(Form):
    """
    Definition of input form for Citation Helper
    """
    bibcodes = TextAreaField('bibcodes')
    return_nr = SelectField('return_nr', choices=[('10','10'),('20','20'),('30','30')])

class MetricsInputForm(Form):
    """
    Definition of input form for Metrics
    """
    bibcodes = TextAreaField('bibcodes')