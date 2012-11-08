'''
Created on Sep 24, 2012

@author: jluker
'''
from flask import Blueprint, request, g, render_template, abort
from adsabs.core import solr

abs_blueprint = Blueprint('abs', __name__, template_folder="templates", static_folder="static")

__all__ = ['abs_blueprint']

@abs_blueprint.route('/<bibcode>', methods=['GET'])
def abstract(bibcode):
    doc = solr.get_document(bibcode)
    if not doc:
        abort(404)
    return render_template('abstract.html', doc=doc)
    
