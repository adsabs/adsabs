'''
Module to interface with the back-end authentication system
'''
import urllib
import urllib2
try:
    import simplejson as json
except ImportError:
    import json

from adslabs.core.dbmodels.mongo import adsUser
#from adslabs.extensions import mongodb

class localAdsUser():
    """
    Class that creates a User object given a mongo user object
    """
    #In the init I copy locally the variables coming from the user object
    def __init__(self, user_local_info):
        self.cookie_id = user_local_info.cookie_id
        self.myads_id = user_local_info.myads_id
        self.username = user_local_info.username
        self.firstname = user_local_info.firstname
        self.lastname = user_local_info.lastname
        self.active = user_local_info.active
        self.anonymous = user_local_info.anonymous
        self.developer = user_local_info.developer
        self.developer_key = user_local_info.developer_key
        self.developer_level = user_local_info.developer_level
        
        #for the templates
        self.name = self.username
    
    AUTHENTICATED = True
    #all this part is needed by flask-login to work
    def __repr__(self):
        return '<User %s>' % self.username
    
    def is_authenticated(self):
        return self.AUTHENTICATED

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return self.anonymous

    def get_id(self):
        return self.cookie_id
    
    def get_dev_key(self):
        return self.developer_key


def _authenticate_against_ads(login, password):
    """
    function that checks the parameters against ads classic
    """
    ads_login_url = 'http://adsabs.harvard.edu/cgi-bin/manage_account/credentials'
    #I encode the parameters to perform a post request
    parameters = urllib.urlencode({'man_email':login, 'man_passwd':password,  'man_cmd':'elogin'})
    #I create the request object
    req = urllib2.Request(ads_login_url, parameters)
    #I set an user agent
    req.add_header('User-Agent', 'ADSLabs Request Agent')
    #I perform the request
    try:
        r = urllib2.urlopen(req)
        user_info = r.read()
        r.close()
    except:
        r = None
        user_info = '{}'
    try:
        user_json = json.loads(user_info)
    except:
        user_json = {}
    #if the login was successful I return the json object
    if user_json.get('message') == 'LOGGED_IN':
        del user_json['message']
        return user_json
    else:
        return None

def _get_local_user_info(user_obj):
    """
    function that retrieved the additional informations about the user from the local database.
    if there is no trace of the user in the current database and it is just logged in, I create one entry
    """
    #I try to extract the data
    user_local_info = adsUser.query.filter(adsUser.cookie_id==user_obj.get('cookie')).first() #@UndefinedVariable
    #if it is empty I insert the data
    if not user_local_info and user_obj.get('loggedin')=='1':
        new_user_local_info = adsUser(cookie_id=user_obj.get('cookie'),
                                    myads_id=user_obj.get('myadsid'), 
                                    username=user_obj.get('email'), 
                                    firstname=user_obj.get('firstname'), 
                                    lastname=user_obj.get('lastname'), 
                                    active=True, 
                                    anonymous=False)
        new_user_local_info.save(safe=True)
        #then I re-extract the user object
        user_local_info = adsUser.query.filter(adsUser.cookie_id==user_obj.get('cookie')).first() #@UndefinedVariable
    
    ##################
    #If I want to insert the user or update the values always with the values from ads_classic, I can do the following 
    #I simply upsert the user inside the mongo database
    #I extract the session from the mongo connection
    #s = mongodb.session #@UndefinedVariable
    #ins_update_query = s.query(adsUser).filter(adsUser.cookie_id==user_obj.get('cookie')).set(myads_id=user_obj.get('myadsid'), 
    #                                username=user_obj.get('email'), 
    #                                firstname=user_obj.get('firstname'), 
    #                                lastname=user_obj.get('lastname'), 
    #                                active=True, 
    #                                anonymous=False).safe().upsert()
    #s.execute()
    #and then extract the user with a query like before
    #
    #I'm not sure which one is the best approach, but I spent time ti find out how to do it and I saved the code here :-)
    ###################
    
    #then I return an instance of a local style User object
    return localAdsUser(user_local_info)

def authenticate(login, password):
    """
    function that authenticate an user against a back-end service
    given username and password
    """
    #I try to login against ADS classic
    ads_user_obj = _authenticate_against_ads(login, password)
    
    #If I've failed I return a negative response
    if not ads_user_obj:
        return None, False
    #otherwise I retrieve the full set of informations from the local database
    return _get_local_user_info(ads_user_obj), True        

def get_user_by_id(id_):
    """
    function needed by the Flask-Login to make the Login work
    given an user id (an actual meaningless id) it returns the user object
    """
    
    #I retrieve the user from the local database
    user_local_info = adsUser.query.filter(adsUser.cookie_id==id_).first() #@UndefinedVariable
    if user_local_info:
        return localAdsUser(user_local_info)
    else:
        return None
    
def get_user_from_developer_key(dev_key):
    """
    function that will check if the developer key is a valid one and returns the 
    """
    #I retrieve the user from the local database
    user_local_info = adsUser.query.filter(adsUser.developer_key==dev_key).first() #@UndefinedVariable
    if user_local_info:
        return localAdsUser(user_local_info)
    else:
        return None