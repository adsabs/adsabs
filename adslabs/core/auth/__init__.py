
from flask import Blueprint

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/', methods=['GET'])
def index():
    """
    
    """
    return 'author index'