from mongoengine import connect
from mongogut.postables import Database

if __name__=="__main__":
    import sys
    if len(sys.argv)==1:
        db_session=connect("adsgut")
    elif len(sys.argv)==3:
        db_session=connect("adsgut", host="mongodb://%s:%s@localhost/adsgut" % (sys.argv[1], sys.argv[2]))
    else:
        print "Not right number of arguments. Exiting"
    currentuser=None
    whosdb=Database(db_session)
    adsgutuser=whosdb.getUserForNick(currentuser, "adsgut")
    currentuser=adsgutuser
    adsuser=whosdb.getUserForNick(currentuser, "ads")
    anonymouseuser, adspubapp=whosdb.addUserToPostable(adsuser, 'ads/app:publications', 'anonymouse')