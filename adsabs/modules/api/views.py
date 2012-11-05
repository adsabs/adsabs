import sys
sys.path.append('..')

from flask import Blueprint, request, render_template, abort
from flask.ext.pushrod import pushrod_view #@UnresolvedImport

from functools import wraps

import errors
from adsabs.modules.user.backend_interface import get_user_from_developer_key
from adsabs.core import solr
from .request import ApiSearchRequest, ApiRecordRequest
from .response import ApiSearchResponse, ApiRecordResponse

# For import *
__all__ = ['api_blueprint']

#definition of the blueprint for the user part
api_blueprint = Blueprint('api', __name__,template_folder="templates")
errors.init_error_handlers(api_blueprint)

def api_user_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if 'dev_key' not in request.args:
            raise errors.ApiNotAuthenticatedError("no developer token provided")
        user = get_user_from_developer_key(request.args.get('dev_key'))
        if not user:
            raise errors.ApiNotAuthenticatedError("unknown user")
        return func(*args, **kwargs)
    return decorator
        
@api_blueprint.route('/search/', methods=['GET'])
@api_user_required
@pushrod_view(xml_template="search.xml")
def search():
    search_req = ApiSearchRequest(request)
    if search_req.validate():
        solr_resp = solr.query(search_req.query())
        resp = ApiSearchResponse.from_solr_response(solr_resp)
        return resp.data()
    raise errors.ApiInvalidRequest(search_req.errors())
        
        
@api_blueprint.route('/record/<identifier>', methods=['GET'])
@api_blueprint.route('/record/<identifier>/<field>', methods=['GET'])
@api_user_required
@pushrod_view(xml_template="record.xml")
def record(identifier, field=None):
    record_req = ApiRecordRequest(identifier, field=field)
    if record_req.validate():
        solr_resp = solr.query(record_req.query())
        if not solr_resp.get_count() > 0:
            raise errors.ApiRecordNotFound(identifier)
        resp = ApiRecordResponse.from_solr_response(solr_resp)
        return resp.data()
        

