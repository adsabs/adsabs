'''
Created on Feb 19, 2013

@author: jluker
'''
    
from flask import Flask
app = Flask(__name__)

from random import choice
import string
import sys

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
        print >>sys.stderr, str(e)
        return "0"
    
    return "Hello World!"

if __name__ == "__main__":
    app.run(port=5001)