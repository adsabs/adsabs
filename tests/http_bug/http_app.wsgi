'''
Created on Feb 19, 2013

@author: jluker
'''
    
import sys, os, pwd
# http://code.google.com/p/modwsgi/wiki/ApplicationIssues#User_HOME_Environment_Variable
os.environ['HOME'] = pwd.getpwuid(os.getuid()).pw_dir

BASE_DIR = os.path.join(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

from flask import Flask
app = Flask(__name__)

from random import choice
import string
import traceback

from config import config
app.config.from_object(config)
from adsabs.extensions import solr
solr.init_app(app)

from adsabs.core.solr import query as solr_query
chars = string.letters + string.digits

@app.route("/")
def query():
    try:
        resp = solr_query(''.join(choice(chars) for _ in range(10)), rows=0)
        return "1"
    except Exception, e:
        print >>sys.stderr, traceback.format_exc()
        return "0"

application = app
