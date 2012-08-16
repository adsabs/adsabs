from flask import Blueprint

#I define the blueprint
search_blueprint = Blueprint('search', __name__, template_folder="templates", static_folder="static")