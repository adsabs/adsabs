from flask import Blueprint, g

#I define the blueprint
search_blueprint = Blueprint('search', __name__, template_folder="templates", static_folder="static")

@search_blueprint.route('/', methods=['GET', 'POST'])
def index():
    """
    
    """
    r = g.solr.query("bibcode:1904Natur..71R..46.")
    return str(r.results)