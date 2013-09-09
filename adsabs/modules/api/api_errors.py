'''
Created on Nov 2, 2012

@author: jluker
'''

import traceback
from flask import g, current_app
from flask.ext.pushrod import pushrod_view #@UnresolvedImport

from adsabs.core.logevent import log_event
from adsabs.core.solr import AdsabsSolrqueryException

class ApiNotAuthenticatedError(Exception):
    pass

class ApiInvalidRequest(Exception):
    pass

class ApiPermissionError(Exception):
    pass

class ApiRecordNotFound(Exception):
    pass

class ApiUnauthorizedIpError(Exception):
    pass

class ApiSolrException(Exception):
    pass

def init_error_handlers(app):

    @app.errorhandler(AdsabsSolrqueryException)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def solrquery_exception(error):
        msg = "Search service error: %s" % error
        dev_key = hasattr(g, 'api_user') and g.api_user.get_dev_key() or None
        exc_info = error.exc_info
        exc_str = traceback.format_exception(*exc_info)
        current_app.logger.error("%s: (%s, %s) %s" % (msg, exc_info[0], exc_info[1], exc_info[2]))
        log_event('api', msg=msg, dev_key=dev_key, exception=exc_str)
        return {'error': msg},500,None
    
    @app.errorhandler(ApiNotAuthenticatedError)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def not_authenticated(error):
        msg = "API authentication failed: %s" % error
        current_app.logger.error(msg)
        return {'error': msg},401,None
    
    @app.errorhandler(ApiInvalidRequest)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def invalid_request(error):
        msg = "API request invalid: %s" % error
        current_app.logger.error(msg)
        return {'error': msg},401,None
    
    @app.errorhandler(ApiPermissionError)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def permission_error(error):
        msg = "Permission error: %s " % error
        current_app.logger.error(msg)
        return {'error': msg},401,None

    @app.errorhandler(ApiRecordNotFound)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def record_not_found(error):
        msg = "No record found with identifier %s" % error
        current_app.logger.error(msg)
        return {'error': msg},404,None
    
    @app.errorhandler(ApiSolrException)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def solr_exception(error):
        msg = "Search processing error: %s" % error
        current_app.logger.error(msg)
        return {'error': msg},400,None
    
    @app.errorhandler(ApiUnauthorizedIpError)
    @pushrod_view(xml_template="error.xml", wrap="error")
    def unauthorized_ip(error):
        msg = "API access blocked: %s" % error
        current_app.logger.error(msg)
        return {'error': msg},401,None