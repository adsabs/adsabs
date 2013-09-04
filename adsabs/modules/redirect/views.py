'''
Created on Aug 27, 2013

@author: dimilia
'''

from flask import (Blueprint, request, abort, redirect, url_for, render_template)
from config import config
from adsabs.core import solr
from adsabs.core.template_filters import quote_url
from adsabs.core.data_formatter import field_to_json


redirect_blueprint = Blueprint('redirect', __name__, template_folder="templates", url_prefix='/redirect')

@redirect_blueprint.after_request
def add_caching_header(response):
    """
    Adds caching headers
    """
    cache_header = 'no-cache'
    response.headers.setdefault('Cache-Control', cache_header)
    return response


### !IMPORTANT
# The redirect url is built in the right way only on the live instance, because only there url_for creates the right path

def url_for_privateLibaryClassic(bibcode):
    """Creates an url for the private libraries"""
    return '%s/cgi-bin/nph-abs_connect?bibcode=%s&library=Add' % (config.ADS_CLASSIC_BASEURL, quote_url(bibcode))

def url_for_twitter(bibcode):
    """Creates an url for twitter"""
    solrdoc = solr.get_document(bibcode)
    if not solrdoc:
        abort(404)
    if solrdoc.author:
        status = '%s: ' % solrdoc.author[0]
    else:
        status = ''
    if solrdoc.title:
        status = '%s%s %s via @adsabs' % (status, solrdoc.title[0], '%s%s' %(config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('abs.abstract', bibcode=bibcode)))
    return 'http://twitter.com/home/?status=%s' % quote_url(status)
    
def url_for_facebook(bibcode):
    """Creates an url for facebook"""
    return 'http://www.facebook.com/share.php?u=%s' % quote_url('%s%s' %(config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('abs.abstract', bibcode=bibcode)))

def url_for_linkedin(bibcode):
    """Creates an url for linkedin"""
    solrdoc = solr.get_document(bibcode)
    if not solrdoc:
        abort(404)
    if solrdoc.author:
        message = '%s: ' % solrdoc.author[0]
    else:
        message = ''
    if solrdoc.title:
        message = '%s%s' % (message, solrdoc.title[0])
    params = 'mini=true&url=%s&title=%s&source=The SAO/NASA Astrophysics Data System' % (quote_url('%s%s' %(config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('abs.abstract', bibcode=bibcode))), quote_url(message))
    return 'http://www.linkedin.com/shareArticle?%s' % params

def url_for_mendeley(bibcode):
    """Creates an url for mendeley"""
    return 'http://www.mendeley.com/import/?url=%s' % quote_url('%s%s' %(config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('abs.abstract', bibcode=bibcode)))

def url_for_sciencewise(bibcode):
    """Creates an url for sciencewise"""
    solrdoc = solr.get_document(bibcode)
    if not solrdoc:
        abort(404)
    ids = solrdoc.getattr_func('ids_data', field_to_json)
    arxiv_id = [] 
    if ids:
        for id_ in ids:
            if id_.get('description') =='arXiv':
                arxiv_id.append(id_.get('identifier'))
    if arxiv_id:
        return 'http://sciencewise.info/bookmarks/%s/add' % quote_url(arxiv_id[0].strip('arXiv:'))
    else:
        abort(404)
        
    

@redirect_blueprint.route('/social_button/<redirect_type>/<bibcode>', methods=['GET'])
def socialbutton(redirect_type, bibcode):
    
    url_to_redirect =None
    
    #each redirect type builds its own url
    if redirect_type == 'private_library':
        url_to_redirect = url_for_privateLibaryClassic(bibcode)
    elif redirect_type == 'twitter':
        url_to_redirect = url_for_twitter(bibcode)
    elif redirect_type == 'facebook':
        url_to_redirect = url_for_facebook(bibcode)
    elif redirect_type == 'linkedin':
        url_to_redirect = url_for_linkedin(bibcode)
    elif redirect_type == 'mendeley':
        url_to_redirect = url_for_mendeley(bibcode)
    elif redirect_type == 'sciencewise':
        url_to_redirect = url_for_sciencewise(bibcode)
    
    if url_to_redirect:
        return redirect(url_to_redirect)
    else:
        return render_template('redirect_error.html')
    