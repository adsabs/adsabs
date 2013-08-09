'''
Created on Aug 12, 2013

@author: jluker
'''

import os
import sys

import requests
import urlparse
from flask import current_app as app, url_for
from flask.ext.script import Manager, prompt_bool #@UnresolvedImport
from config import config

manager = Manager("Perform page content repository operations", with_default_commands=False)

@manager.command
def refresh():
    """refresh the local page content repository with the lastest changes"""

    if not prompt_bool("Refresh page content"): 
        sys.exit()

    dep_path = config.DEPLOYMENT_PATH
    refresh_url = url_for('pages.refresh_content', key=config.PAGES_REFRESH_ACCESS_KEY)
    url = '/'.join(s.strip('/') for s in [config.PAGES_REFRESH_BASE_URL, dep_path, refresh_url] if s is not None)

    r = requests.post(url)

    if r.status_code is 200:
        app.logger.info("content refreshed. HEAD now at %s" % r.text)
    else:
        app.logger.info("Something went wrong: http response code = %d" % r.status_code)
        app.logger.info(r.text)
        