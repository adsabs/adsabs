'''
Created on May 10, 2013

@author: dimilia
'''
from flask import request

def is_submitted_cust(form):
    """
    Custom version of is_submitted.
    The default one in flask-wtf works only with POST and PUT
    while some of the ADS forms work with GET
    The idea is that if at least one of the inputs of the form 
    is in the flask request object, then the form has been submitted
    """
    for field in form.data:
        if request.values.get(field):
            return True
    return False