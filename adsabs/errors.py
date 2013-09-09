'''
Created on Jan 7, 2013

@author: jluker
'''
import logging
from flask import render_template, request
from adsabs.core.logevent import LogEvent

def create_error_handler(app, status_code, template):
    @app.errorhandler(status_code)
    def f(error):    
        app.logger.error("[error] %s, %s" % (str(error), request.path))
        return render_template(template), status_code

    