# -*- coding: utf-8 -*-

from config import config

from flask.ext.login import LoginManager 
login_manager = LoginManager()

from flask.ext.mongoalchemy import MongoAlchemy 
mongodb = MongoAlchemy()

from flask.ext.pushrod import Pushrod 
pushrod = Pushrod(default_renderer=config.API_DEFAULT_RESPONSE_FORMAT)

from flask.ext.mail import Mail 
mail = Mail()

from flask.ext.cache import Cache   
cache = Cache()

from flask.ext.solrquery import FlaskSolrQuery 
solr = FlaskSolrQuery()

from flask.ext.adsdata import FlaskAdsdata 
adsdata = FlaskAdsdata()

from flask.ext.mongoengine import MongoEngine 
mongoengine=MongoEngine()

from flask.ext.statsd import StatsD 
statsd = StatsD()