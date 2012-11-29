'''
Created on Nov 29, 2012

@author: jluker
'''

from config import config

class DeploymentPathMiddleware(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = config.DEPLOYMENT_PATH
        return self.app(environ, start_response)
