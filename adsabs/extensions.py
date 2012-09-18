# -*- coding: utf-8 -*-

# For import *
__all__ = ['login_manager', 'invenio_flk', 'mongodb', 'solr']

#from flask.ext.sqlalchemy import SQLAlchemy #@UnresolvedImport
#db = SQLAlchemy()

#from flask.ext.mail import Mail #@UnresolvedImport
#mail = Mail()

#from flask.ext.cache import Cache #@UnresolvedImport
#cache = Cache()



from flask.ext.login import LoginManager #@UnresolvedImport
login_manager = LoginManager()

from flask.ext.mongoalchemy import MongoAlchemy #@UnresolvedImport
mongodb = MongoAlchemy()

from flask.ext.solrpy import FlaskSolrpy #@UnresolvedImport
solr = FlaskSolrpy()

invenio_flk = None
try:
    import invenio #@UnresolvedImport
    from core.flask_invenio import invenioInterface
    invenio_flk = invenioInterface()
except:
    pass
