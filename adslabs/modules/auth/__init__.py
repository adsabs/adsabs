
from flask import Blueprint

auth_blueprint = Blueprint('auth', __name__, template_folder="templates", static_folder="static")

@auth_blueprint.route('/', methods=['GET', 'POST'])
def index():
    """
    
    """
    return 'author index'