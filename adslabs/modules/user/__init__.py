
from flask import Blueprint

user_blueprint = Blueprint('user', __name__, template_folder="templates", static_folder="static")

@user_blueprint.route('/', methods=['GET'])
def index():
    """
    
    """
    return 'user infos index'

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    """
    return 'login'

@user_blueprint.route('/logout', methods=['GET'])
def logout():
    """
    """
    return 'logout'