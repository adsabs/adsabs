'''
Created on Jan 7, 2013

@author: jluker
'''

from flask import render_template, request, g

def create_error_handler(app, status_code, template):
    @app.errorhandler(status_code)
    def f(error):    
        return render_template(template), status_code