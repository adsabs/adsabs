'''
Created on Jan 7, 2013

@author: jluker
'''

from flask import render_template, request, g, current_app as app

def create_error_handler(app, status_code, template):
    @app.errorhandler(status_code)
    def f(error):    
        app.logger.error("error (%s): %s" % (status_code, str(error)))
        return render_template(template), status_code