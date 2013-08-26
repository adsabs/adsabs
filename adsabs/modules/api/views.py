import sys

from flask import Blueprint, request, g, current_app as app
from flask.ext.pushrod import pushrod_view #@UnresolvedImport
from flask.ext.solrquery import solr, signals as solr_signals #@UnresolvedImport

from functools import wraps

import api_errors
import logging
from adsabs.core.logevent import LogEvent
from api_user import AdsApiUser
from api_request import ApiSearchRequest, ApiRecordRequest
from config import config

#definition of the blueprint for the user part
api_blueprint = Blueprint('api', __name__,template_folder="templates", url_prefix='/api')
api_errors.init_error_handlers(api_blueprint)

def api_user_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        dev_key = request.args.get('dev_key', None)
        if not dev_key or len(dev_key) == 0:
            raise api_errors.ApiNotAuthenticatedError("no developer token provided")
        try:
            user = AdsApiUser.from_dev_key(dev_key)
        except Exception, e:
            import traceback
            exc_info = sys.exc_info()
            app.logger.error("User auth failure: %s, %s\n%s" % (exc_info[0], exc_info[1], traceback.format_exc()))
            user = None
        if not user:
            raise api_errors.ApiNotAuthenticatedError("unknown user")
        g.api_user = user
        return func(*args, **kwargs)
    return decorator

def api_ip_allowed(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        user = g.api_user
        if not user.ip_allowed(request.remote_addr):
            raise api_errors.ApiUnauthorizedIpError("api requests not allowed from %s" % request.remote_addr)
        return func(*args, **kwargs)
    return decorator

@api_blueprint.before_request
def get_api_version_header():
    g.api_version = request.headers.get('X-API-Version', config.API_CURRENT_VERSION)
        
@api_blueprint.after_request
def add_api_version_header(response):
    """
    Add default api version header if not already set
    """
    response.headers.setdefault('X-API-Version', g.api_version)
    return response

@api_blueprint.route('/settings/', methods=['GET'])
@api_user_required
@api_ip_allowed
@pushrod_view(xml_template="settings.xml", wrap='settings')
def settings():
    perms = g.api_user.get_dev_perms()
    allowed_fields = g.api_user.get_allowed_fields()
    perms.update({'allowed_fields': allowed_fields})
    return perms

@api_blueprint.route('/search/', methods=['GET'])
@api_user_required
@api_ip_allowed
@pushrod_view(xml_template="search.xml")
def search():
    search_req = ApiSearchRequest(request.args)
    if not search_req.validate():
        raise api_errors.ApiInvalidRequest(search_req.input_errors())
    resp = search_req.execute()
    return resp.search_response()
        
@api_blueprint.route('/record/<path:identifier>', methods=['GET'])
@api_user_required
@api_ip_allowed
@pushrod_view(xml_template="record.xml", wrap='doc')
def record(identifier):
    record_req = ApiRecordRequest(identifier, request.args)
    if not record_req.validate():
        raise api_errors.ApiInvalidRequest(record_req.errors())
    resp = record_req.execute()
    if not resp.get_hits() > 0:
        raise api_errors.ApiRecordNotFound(identifier)
    return resp.record_response()
        
#@api_blueprint.route('/record/<identifier>/<operator>', methods=['GET'])
#@api_user_required
#@pushrod_view(xml_template="record.xml")
#def record_operator(identifier, operator):
#    pass

#@api_blueprint.route('/mlt/', methods=['GET'])
#@api_user_required
#@pushrod_view(xml_template="mlt.xml")
#def mlt():
#    pass

@solr_signals.error_signal.connect
def log_solr_error(sender, **kwargs):
    if hasattr(g, 'user_cookie_id'):
        kwargs['dev_key'] = g.api_user.get_dev_key()
        event = LogEvent.new(request.url, **kwargs)
        logging.getLogger('search').info(event)    

@solr_signals.search_signal.connect
def log_solr_event(sender, **kwargs):
    """
    extracts some data from the solr  for log/analytics purposes
    """
    if hasattr(g, 'api_user'):
        resp = kwargs.pop('response')
        log_data = {
            'q': resp.get_query(),
            'hits': resp.get_hits(),
            'count': resp.get_count(),
            'start': resp.get_start_count(),
            'qtime': resp.get_qtime(),
            'results': resp.get_doc_values('bibcode', 0, config.SEARCH_DEFAULT_ROWS),
            'error_msg': resp.get_error_message(),
            'http_status': resp.get_http_status(),
            'solr_url': resp.request.url,
            'dev_key': g.api_user.get_dev_key()
        }
        log_data.update(kwargs)
        event = LogEvent.new(request.url, **log_data)
        logging.getLogger('api').info(event)