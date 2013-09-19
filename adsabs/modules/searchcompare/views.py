'''
Created on Nov 9, 2012

@author: jluker
'''

from urllib import urlencode
from urllib2 import quote, urlopen
from lxml.etree import fromstring
from simplejson import dumps

from flask import Blueprint, request, g, render_template, abort
from flask.ext.solrquery import solr

from config import config

searchcompare_blueprint = Blueprint('searchcompare', __name__, template_folder="templates", 
                                    static_folder="static", url_prefix='/searchcompare')

@searchcompare_blueprint.route('/classic', methods=['GET'])
def classic_search():
    try:
        q = request.args.get('q')
    except:
        abort(400)
    search_url = "http://adsabs.harvard.edu/cgi-bin/topicSearch?" \
                + ("q=%s&qtype=NEW&db_key=AST&db_key=PRE&arxiv_sel=astro-ph&arxiv_sel=gr-qc&data_type=XML" % quote(q))
    u = urlopen(search_url)
    root = fromstring(u.read())
    ns = {'ads': 'http://ads.harvard.edu/schema/abs/1.1/abstracts'}
    docs = [] 
    for rec in root.getchildren():
        docs.append({
            'bibcode': rec.find('ads:bibcode', ns).text,
            'title': rec.find('ads:title', ns).text,
            'score': rec.find('ads:score', ns).text
            })
    results = {
        'count': root.attrib.get('selected'),
        'docs': docs
        }
    return render_template('results.html', results=results, type='classic', search_url=search_url)
#    
@searchcompare_blueprint.route('/solr', methods=['GET'])
def solr_search():
    try:
        q = request.args.get('q')
    except:
        abort(400)
    resp = solr.query(q, rows=200, fields=['bibcode','title','score'], 
                      sort=(config.SEARCH_SORT_OPTIONS_MAP['DATE'], 'desc'),
                      filters=['database:ASTRONOMY'])
    search_results = resp.search_response()
    return render_template('results.html', results=search_results['results'], type='solr', search_url=resp.request.url)

@searchcompare_blueprint.route('/', methods=['GET'])
def index():
    """
    displays the initial interface
    """
    return render_template('main.html')
