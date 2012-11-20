'''
Module to interface with the back-end authentication system
'''
import urllib
import urllib2
from simplejson import loads

from .models import AdsUserRecord

__all__ = ['AdsUser', 'authenticate' ]

class AdsUser():
    """
    Class that creates a User object given a mongo user object
    """
    AUTHENTICATED = True
    
    @staticmethod
    def from_classic_user(classic_user):
        """
        factory method that retrieved the additional informations about the user from the local database.
        if there is no trace of the user in the current database and it is just logged in, I create one entry
        """
        #I try to extract the data
        user_rec = AdsUserRecord.query.filter(AdsUserRecord.cookie_id==classic_user.get('cookie')).first() #@UndefinedVariable
        #if it is empty I insert the data
        if not user_rec and classic_user.get('loggedin')=='1':
            new_rec = AdsUserRecord(cookie_id=classic_user.get('cookie'),
                                        myads_id=classic_user.get('myadsid'), 
                                        username=classic_user.get('email'), 
                                        firstname=classic_user.get('firstname'), 
                                        lastname=classic_user.get('lastname'), 
                                        active=True, 
                                        anonymous=False)
            new_rec.save(safe=True)
            # then I re-extract the user object
            # (don't think it's necessary to re-fetch the record
            #user_local_info = AdsUser.query.filter(AdsUser.cookie_id==user_obj.get('cookie')).first() #@UndefinedVariable
            return AdsUser(new_rec)
        
        ##################
        #If I want to insert the user or update the values always with the values from ads_classic, I can do the following 
        #I simply upsert the user inside the mongo database
        #I extract the session from the mongo connection
        #s = mongodb.session #@UndefinedVariable
        #ins_update_query = s.query(AdsUser).filter(AdsUser.cookie_id==user_obj.get('cookie')).set(myads_id=user_obj.get('myadsid'), 
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
        return AdsUser(user_rec)

    @staticmethod
    def from_id(id_):
        """
        function needed by the Flask-Login to make the Login work
        given an user id (an actual meaningless id) it returns the user object
        """
        
        #I retrieve the user from the local database
        user_rec = AdsUserRecord.query.filter(AdsUserRecord.cookie_id==id_).first() #@UndefinedVariable
        if user_rec:
            return AdsUser(user_rec)
        return None
        
    @staticmethod
    def from_dev_key(dev_key):
        """
        function that will check if the developer key is a valid one and returns the 
        """
        #I retrieve the user from the local database
        user_rec = AdsUserRecord.query.filter(AdsUserRecord.developer_key==dev_key).first() #@UndefinedVariable
        if user_rec:
            return AdsUser(user_rec)
        return None
     
    #In the init I copy locally the variables coming from the user object
    def __init__(self, user_rec):
        self.user_rec = user_rec
#        self.cookie_id = user_local_info.cookie_id
#        self.myads_id = user_local_info.myads_id
#        self.username = user_local_info.username
#        self.firstname = user_local_info.firstname
#        self.lastname = user_local_info.lastname
#        self.active = user_local_info.active
#        self.anonymous = user_local_info.anonymous
#        self.developer = user_local_info.developer
#        self.developer_key = user_local_info.developer_key
#        self.developer_level = user_local_info.developer_level
#        self.developer_perms = user_local_info.developer_perms
        
        #for the templates
        if self.user_rec.firstname != '' and self.user_rec.lastname != '':
            self.name ='%s %s' % (self.user_rec.firstname , self.user_rec.lastname)
        elif self.user_rec.lastname != '':
            self.name = self.user_rec.lastname
        else:
            self.name = self.user_rec.username
    
    #all this part is needed by flask-login to work
    def __repr__(self):
        return '<User %s>' % self.user_rec.username
    
    def is_authenticated(self):
        return self.AUTHENTICATED

    def is_active(self):
        return self.user_rec.active

    def is_anonymous(self):
        return self.user_rec.anonymous

    def get_id(self):
        return self.user_rec.cookie_id
    
    def is_developer(self):
        return self.user_rec.developer_key and True
    
    def get_dev_key(self):
        return self.user_rec.developer_key
    
    def get_dev_perms(self):
        return self.user_rec.developer_perms

def get_classic_user(login, password):
    """
    function that checks the parameters against ads classic
    """
    ads_login_url = 'http://adsabs.harvard.edu/cgi-bin/manage_account/credentials'
    #I encode the parameters to perform a post request
    parameters = urllib.urlencode({'man_email':login, 'man_passwd':password,  'man_cmd':'elogin'})
    #I create the request object
    req = urllib2.Request(ads_login_url, parameters)
    #I set an user agent
    req.add_header('User-Agent', 'ADS Script Request Agent')
    #I perform the request
    try:
        r = urllib2.urlopen(req)
        user_info = r.read()
        r.close()
    except:
        r = None
        user_info = '{}'
    try:
        user_json = loads(user_info)
    except:
        user_json = {}
    #if the login was successful I return the json object
    if user_json.get('message') == 'LOGGED_IN':
        del user_json['message']
        return user_json
    else:
        return None

def authenticate(login, password):
    """
    function that authenticate an user against a back-end service
    given username and password
    """
    #I try to login against ADS classic
    classic_user = get_classic_user(login, password)
    
    #If I've failed I return a negative response
    if not classic_user:
        return None, False
    
    #otherwise I retrieve the full set of informations from the local database
    return AdsUser.from_classic_user(classic_user), True
