'''
Created on Nov 9, 2012

@author: jluker
'''

from urllib import urlencode
from urllib2 import quote, urlopen
from lxml.etree import fromstring
from simplejson import dumps

from flask import Blueprint, request, g, render_template, abort

from config import config
from adsabs.core.solr import SolrRequest

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
    req = SolrRequest(q)
    req.set_rows(200)
    req.set_fields(['bibcode','title','score'])
    req.set_sort(config.SOLR_SORT_OPTIONS['DATE'],'desc')
    req.add_filter('database:ASTRONOMY')
    resp = req.get_response().search_response()
    return render_template('results.html', results=resp['results'], type='solr', search_url=req.get_raw_request_url())

@searchcompare_blueprint.route('/', methods=['GET'])
def index():
    """
    displays the initial interface
    """
    return render_template('main.html')
