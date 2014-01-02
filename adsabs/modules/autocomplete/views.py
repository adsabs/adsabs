import flask.json
from flask import Blueprint, request
from pymongo import MongoClient
import re
from flask.ext.adsdata import adsdata


#Definition of the blueprint
autocomplete_blueprint = Blueprint('autocomplete', __name__, template_folder="templates", 
                             static_folder="static", url_prefix='/autocomplete')


@autocomplete_blueprint.route('/<field>', methods=['GET'])
def autocomplete(field):
    """
    serves json for ajax requests
    """
    if field == 'pub':
        coll = adsdata.get_collection('bibstems_ranked')
        snippet = request.args.get('term', '')
        r = re.compile(".*"+snippet+".*", re.IGNORECASE)
        records = list(coll.find({'label': r}, {'_id':0, 'label':1, 'value':1, 'weight':1}).limit(75).sort('weight',-1))
        return flask.json.dumps(records)
        
    elif field == 'author':
        pass