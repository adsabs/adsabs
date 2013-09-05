'''
Created on Sep 5, 2013

@author: dimilia
'''
from flask import (Blueprint, request, g, render_template, abort)

export_blueprint = Blueprint('export', __name__, template_folder="templates", url_prefix='/export')

@export_blueprint.route('/', methods=['GET', 'POST'])
def export_list_bibcodes():
    """
    view that exports a set of papers
    """
    return 'export'