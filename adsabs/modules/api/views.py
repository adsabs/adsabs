import sys
sys.path.append('..')

from flask import Blueprint, request, g
from flask.ext.pushrod import pushrod_view #@UnresolvedImport

from functools import wraps

import errors
from adsabs.modules.user import AdsUser
from adsabs.core import solr
from .request import ApiSearchRequest, ApiRecordRequest

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
        user = AdsUser.from_dev_key(request.args.get('dev_key'))
        if not user:
            raise errors.ApiNotAuthenticatedError("unknown user")
        g.api_user = user
        return func(*args, **kwargs)
    return decorator
        
@api_blueprint.route('/search/', methods=['GET'])
@api_user_required
@pushrod_view(xml_template="search.xml")
def search():
    search_req = ApiSearchRequest(request.values)
    if search_req.validate():
        resp = search_req.execute()
        return resp.search_response()
    raise errors.ApiInvalidRequest(search_req.errors())
        
        
@api_blueprint.route('/record/<identifier>', methods=['GET'])
@api_blueprint.route('/record/<identifier>/<operator>', methods=['GET'])
@api_user_required
@pushrod_view(xml_template="record.xml")
def record(identifier, operator=None):
    record_req = ApiRecordRequest(identifier, request.values, operator=operator)
    if record_req.validate():
        resp = record_req.execute()
        if not resp.get_count() > 0:
            raise errors.ApiRecordNotFound(identifier)
        return resp.record_response()
    raise errors.ApiInvalidRequest(record_req.errors())
        

#@api_blueprint.route('/mlt/', methods=['GET'])
#@api_user_required
#@pushrod_view(xml_template="mlt.xml")
#def mlt():
#    pass