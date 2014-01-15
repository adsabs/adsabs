import sys

from flask import Blueprint, request, g, current_app as app
from flask.ext.pushrod import pushrod_view #@UnresolvedImport

from functools import wraps

import api_errors
from api_user import AdsApiUser
from api_request import ApiSearchRequest, ApiRecordRequest
from config import config

from adsabs.modules.bibutils.metrics_functions import generate_metrics
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
            raise api_errors.ApiNotAuthenticatedError("unknown dev_key: %s" % dev_key)
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

@api_blueprint.route('/metrics/', methods=['GET'])
@api_user_required
@api_ip_allowed
@pushrod_view(xml_template="metrics.xml")
def metrics():
    search_req = ApiSearchRequest(request.args)
    if not search_req.validate():
        raise api_errors.ApiInvalidRequest(search_req.input_errors())
    resp = search_req.execute()
    search_response = resp.search_response()
    bibcodes = map(lambda a: a['bibcode'], filter(lambda a: 'bibcode' in a, search_response['results']['docs']))
    metrics = generate_metrics(bibcodes=bibcodes)
    search_response['results'] = metrics
    return search_response

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
