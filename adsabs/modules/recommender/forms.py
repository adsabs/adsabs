'''
Created on Jul 16, 2013

@author: ehenneken
'''

from flask.ext.wtf import Form 
from wtforms import TextAreaField

__all__ = ['CitationHelperInputForm',]

class SuggestionsInputForm(Form):
    """
    Definition of input form for Metrics
    """
    bibcodes = TextAreaField('bibcodes')