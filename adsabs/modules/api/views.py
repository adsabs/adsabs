import sys
sys.path.append('..')

from flask import Blueprint, request, render_template, abort
from flask.ext.pushrod import pushrod_view #@UnresolvedImport

from functools import wraps

from adsabs.modules.user.backend_interface import get_user_from_developer_key
from adsabs.core import solr
from .errors import init_error_handlers, ApiNotAuthenticatedError, ApiInvalidRequest
from .response import ApiResponse
from .request import ApiRequest

# For import *
__all__ = ['api_blueprint']

#definition of the blueprint for the user part
api_blueprint = Blueprint('api', __name__,template_folder="templates")
init_error_handlers(api_blueprint)

def api_user_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        user = get_user_from_developer_key(request.args.get('dev_key'))
        if not user:
            raise ApiNotAuthenticatedError("unknown user")
        return func(*args, **kwargs)
    return decorator
        
#def allow_format_override(func):
#    @wraps(func)
#    def decorator(*args, **kwargs):
#        if request.args.has_key('format'):
#            kwargs['format'] = request.args.get('format')
#        kwargs['format'] = default_format
#        return func(*args, **kwargs)
#    return decorator
        
@api_blueprint.route('/search', methods=['GET'])
@api_user_required
#@allow_format_override
@pushrod_view(xml_template="search.xml")
def search():
    api_request = ApiRequest(request)
    if api_request.validate():
        solr_resp = solr.query(api_request.query())
        resp = ApiResponse.from_solr_response(solr_resp)
        return resp.data()
    raise ApiInvalidRequest(api_request.errors())
        
        
@api_blueprint.route('/record/<identifier>', methods=['GET'])
@api_blueprint.route('/record/<identifier>/<field>', methods=['GET'])
@api_user_required
#@allow_format_override
@pushrod_view(xml_template="record.xml")
def record(identifier, field=None):
    pass

