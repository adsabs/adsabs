'''
Created on Nov 2, 2012

@author: jluker
'''

from flask.ext.pushrod import pushrod_view #@UnresolvedImport

class ApiNotAuthenticatedError(Exception):
    pass

class ApiInvalidRequest(Exception):
    pass

class ApiPermissionError(Exception):
    pass

class ApiRecordNotFound(Exception):
    pass

class ApiSolrException(Exception):
    pass

def init_error_handlers(app):
    @app.errorhandler(ApiNotAuthenticatedError)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def not_authenticated(error):
        msg = "API authentication failed: %s" % error
        return {'error': msg},401,None
    
    @app.errorhandler(ApiInvalidRequest)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def invalid_request(error):
        msg = "API request invalid: %s" % error
        return {'error': msg},401,None
    
    @app.errorhandler(ApiPermissionError)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def permission_error(error):
        msg = "Permission error: %s " % error
        return {'error': msg},401,None

    @app.errorhandler(ApiRecordNotFound)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def record_not_found(error):
        msg = "No record found with identifier %s" % error
        return {'error': msg},404,None
    
    @app.errorhandler(ApiSolrException)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def solr_exception(error):
        msg = "Search processing error: %s" % error
        return {'error': msg},400,None