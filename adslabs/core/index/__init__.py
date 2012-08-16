from flask import Blueprint

#I define the blueprint
index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/', methods=['GET', 'POST'])
def index():
    """
    
    """
    return 'Global index'