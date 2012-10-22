from flask import Blueprint, render_template, request

from adsabs.modules.search.forms import QueryForm

#I define the blueprint
index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/', methods=['GET', 'POST'])
def index():
    """
    Entry point of the web site
    """
    search_form = QueryForm(request.values, csrf_enabled=False)
    
    return render_template('index/main_page.html', form=search_form)
