'''
Created on Nov 2, 2012

@author: jluker
'''

from flask.ext.pushrod import pushrod_view #@UnresolvedImport
from .response import ApiResponse

class ApiNotAuthenticatedError(Exception):
    pass

class ApiInvalidRequest(Exception):
    pass

def init_error_handlers(app):
    @app.errorhandler(ApiNotAuthenticatedError)
    @pushrod_view()
    def not_authenticated(error):
        resp = ApiResponse()
        resp.error("API authentication failed: %s" % error.message, 401)
        return resp.data(),401,None
    
    @app.errorhandler(ApiInvalidRequest)
    @pushrod_view()
    def invalid_request(error):
        resp = ApiResponse()
        resp.error("API request invalid: %s" % error.message, 400)
        return resp.data(),400,None
