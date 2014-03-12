from mongogut.postables import Database
from flask import current_app as app
from config import config
from adsabs.extensions import mongoengine

def migrate():
    currentuser=None
    whosdb=Database(mongoengine)
    adsgutuser=whosdb.getUserForNick(currentuser, "adsgut")
    currentuser=adsgutuser
    adsuser=whosdb.getUserForNick(currentuser, "ads")
    anonymouseuser, adspubapp=whosdb.addUserToPostable(adsuser, 'ads/app:publications', 'anonymouse')