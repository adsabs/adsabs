'''
Created on Jun 3, 2013

@author: jluker
'''

import requests
from flask import g
from config import config

class SolrRequestAdapter(requests.adapters.HTTPAdapter):
    """
    send user's cookie id value as the JSESSIONID to enable
    HAProxy sticky sessions
    """
    
    def __init__(self):
        super(SolrRequestAdapter, self).__init__();
    
    def send(self, request, **kwargs):
        cookie = { config.SOLR_HAPROXY_SESSION_COOKIE_NAME: g.user_cookie_id }
        request.prepare_cookies(cookie)
        return super(SolrRequestAdapter, self).send(request, **kwargs)