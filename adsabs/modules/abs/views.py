'''
Created on Sep 24, 2012

@author: jluker
'''
from flask import Blueprint, request, g, render_template, abort
from adsabs.core import solr
from adsabs.core import invenio

abs_blueprint = Blueprint('abs', __name__, template_folder="templates", static_folder="static")

__all__ = ['abs_blueprint']

@abs_blueprint.route('/<bibcode>', methods=['GET'])
def abstract(bibcode):
    solrdoc = solr.get_document(bibcode)
    inveniodoc = invenio.get_invenio_metadata(bibcode)
    if not solrdoc:
        abort(404)
    return render_template('abstract_tabs.html', solrdoc=solrdoc, inveniodoc=inveniodoc, curview='abstract')
    
@abs_blueprint.route('/<bibcode>/references', methods=['GET'])
def references(bibcode):
    solrdoc = solr.get_document(bibcode)
    inveniodoc = invenio.get_invenio_metadata(bibcode)
    if not solrdoc:
        abort(404)
    return render_template('abstract_tabs.html', solrdoc=solrdoc, inveniodoc=inveniodoc, curview='references')

@abs_blueprint.route('/<bibcode>/citations', methods=['GET'])
def citations(bibcode):
    solrdoc = solr.get_document(bibcode)
    inveniodoc = invenio.get_invenio_metadata(bibcode)
    if not solrdoc:
        abort(404)
    return render_template('abstract_tabs.html', solrdoc=solrdoc, inveniodoc=inveniodoc, curview='citations')

@abs_blueprint.route('/<bibcode>/toc', methods=['GET'])
def toc(bibcode):
    solrdoc = solr.get_document(bibcode)
    inveniodoc = invenio.get_invenio_metadata(bibcode)
    if not solrdoc:
        abort(404)
    return render_template('abstract_tabs.html', solrdoc=solrdoc, inveniodoc=inveniodoc, curview='toc')