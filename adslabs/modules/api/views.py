import sys
sys.path.append('..')

from flask import Blueprint, request, render_template
from adslabs.modules.user.backend_interface import get_user_from_developer_key
from adslabs.extensions import invenio_flk

from ret_functions import ret_xml


# For import *
__all__ = ['api_blueprint', 'get_abstract', ]

#definition of the blueprint for the user part
api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/abs/<data_format>', methods=['GET'])
def get_abstract(data_format):
    """
    View to get an abstract given an identifier for the record
    and a developer key 
    a valid url should be like
    /api/abs?dev_key=<dev_key>&ads_id=<ads_id>
    """
    if data_format.lower() == 'marcxml':
        #I extract the parameters
        dev_key = request.args.get('dev_key')
        ads_id = request.args.get('ads_id')
        
        #if one or more parameters are missing I return an error
        if not dev_key or not ads_id:
            return ret_xml('<error>Wrong or missing parameters</error>')
        
        #I get the user (if any) from the developer key
        user = get_user_from_developer_key(dev_key)
        if not user:
            return ret_xml('<error>Authentication error.</error>')
        
        #I get the record from invenio
        record_abstract = invenio_flk.get_abstract_xml_from_ads_id(ads_id)
        
        if not record_abstract:
            return ret_xml('<error>No record found.</error>')
        else:
            return ret_xml(record_abstract)
    else:
        return render_template("errors/400.html"), 400