'''
Module to interface with the back-end authentication system
'''
from flask import (current_app as app, g, url_for)
from flask.ext.login import current_user                    
import pytz
from datetime import datetime, timedelta
import os
from itsdangerous import (URLSafeSerializer, TimestampSigner, BadSignature, SignatureExpired, BadTimeSignature)
from flask.ext.mail import Message 
from .models import AdsUserRecord
from adsabs.extensions import mail, statsd
from config import config
from adsabs.core.classic.user import *

__all__ = ['AdsUser', 'authenticate', 'login_exists', 'login_exists_local', 'login_exists_classic', 
           'login_is_active', 'create_user', 'activate_user', 'resend_activation_email', 'change_user_settings',
            'activate_user_new_email', 'change_user_password', 'reset_user_password_step_one', 'reset_user_password_step_two']


class AdsUser(object):
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
        #Extract first and lastname        
        firstname = lastname = ''
        split_name = classic_user.get('fullname', '').split('|')
        if len(split_name) == 1:
            lastname = split_name[0]
        else:
            firstname = split_name[0]
            lastname = split_name[1]
        #I try to extract the data
        loc_db_user = AdsUserRecord.query.filter(AdsUserRecord.cookie_id==classic_user.get('cookie')) #@UndefinedVariable
        user_rec = loc_db_user.first()
        #if it is empty I insert the data
        if not user_rec and classic_user.get('loggedin')=='1':
            new_rec = AdsUserRecord(cookie_id=classic_user.get('cookie'),
                                        myads_id=classic_user.get('myadsid'), 
                                        username=classic_user.get('email'), 
                                        firstname=firstname, 
                                        lastname=lastname,
                                        password='',
                                        registered=datetime.utcnow().replace(tzinfo=pytz.utc),
                                        active=True, 
                                        anonymous=False,
                                        remote_login_system=classic_user.get('request', {}).get('man_url', ''),
                                        openurl_icon=classic_user.get('openurl_icon'))
            new_rec.save()
            # then I re-extract the user object
            # (don't think it's necessary to re-fetch the record
            #user_local_info = AdsUser.query.filter(AdsUser.cookie_id==user_obj.get('cookie')).first() #@UndefinedVariable
            return AdsUser(new_rec)
        #if the user already exists, update the metadata in the local DB
        elif user_rec and classic_user.get('loggedin')=='1':
            params_update = {}
            if user_rec.username != classic_user.get('email'):
                params_update['username'] = classic_user.get('email')
            if user_rec.myads_id != classic_user.get('myadsid'):
                params_update['myads_id'] = classic_user.get('myadsid')
            if user_rec.openurl_icon != classic_user.get('openurl_icon'):
                params_update['openurl_icon'] = classic_user.get('openurl_icon')
            if user_rec.firstname != firstname:
                params_update['firstname'] = firstname
            if user_rec.lastname != lastname:
                params_update['lastname'] = lastname
            if user_rec.password != '':
                params_update['password'] = ''
            #if there are updates to run
            if params_update:
                #actual update
                loc_db_user.set(**params_update).execute()
                #refresh the user object
                user_rec = loc_db_user.first() 
        
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
        #I'm not sure which one is the best approach, but I spent time to find out how to do it and I saved the code here :-)
        ###################
        
        #Return an instance of a local style User object
        return AdsUser(user_rec)

    @classmethod
    def from_id(cls, id_):
        """
        function needed by the Flask-Login to make the Login work
        given an user id (an actual meaningless id) it returns the user object
        """
        #I retrieve the user from the local database
        user_rec = AdsUserRecord.query.filter(AdsUserRecord.cookie_id==id_).first() #@UndefinedVariable
        if user_rec:
            return cls(user_rec)
        return None
        
    @classmethod
    def from_email(cls, email):
        """
        """
        #I retrieve the user from the local database
        user_rec = AdsUserRecord.query.filter(AdsUserRecord.username==email).first() #@UndefinedVariable
        if user_rec:
            return cls(user_rec)
        return None
     
    #In the init I copy locally the variables coming from the user object
    def __init__(self, user_rec):
        self.user_rec = user_rec
        
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
    
    def get_username(self):
        return self.user_rec.username
    
    def get_developer_key(self):
        return self.user_rec.developer_key
    
    def get_registered(self):
        """
        Returns the UTC datetime object representing when the user first registered
        """
        return self.user_rec.registered
    
    def set_last_signon(self, dt=None):
        if not dt:
            dt = datetime.utcnow().replace(tzinfo=pytz.utc)
        self.user_rec.last_signon = dt
        self.user_rec.save()
        
    def get_last_signon(self):
        """
        Returns the UTC datetime object representing when the user first registered
        """
        return self.user_rec.last_signon



def send_email_to_user(title, message_html, recipients, sender=None):
    """ 
    Generic function to send an email to users
    """
    if not sender:
        sender = 'noReplay-ADS@cfa.harvard.edu'
    msg = Message(title,
                  html=message_html,
                  sender=sender,
                  recipients=recipients)
    mail.send(msg)  #@UndefinedVariable
    statsd.incr("user.email.sent")


def authenticate(login, password):
    """
    function that authenticate an user against a back-end service
    given username and password
    """
    if not login or not password:
        return  None, 'MADATORY_PARAMETERS_MISSING'
    #first fetch the user using the login
    user_rec = AdsUserRecord.query.filter(AdsUserRecord.username==login).first()    #@UndefinedVariable
    if user_rec:
        if not user_rec.active:
            return None, 'LOCAL_NOT_ACTIVE'
        
    #I try to login against ADS classic
    classic_user = get_classic_user(login, password)
    
    if classic_user.get('message') == 'LOGGED_IN':
        del classic_user['message']
    else:
        #If I've failed I return a negative response
        return None, 'WRONG_PARAMS'
    
    #otherwise I retrieve the full set of informations from the local database
    return AdsUser.from_classic_user(classic_user), 'SUCCESS'

def login_exists_local(login):
    """
    function that checks if there is a local login
    """
    #check local database
    user_rec = AdsUserRecord.query.filter(AdsUserRecord.username==login).first()    #@UndefinedVariable
    if user_rec:
        return True
    else:
        return False

def login_exists(login):
    """
    function that checks if an account already exists
    """
    if login_exists_local(login):
        return True
    if login_exists_classic(login):
        return True
    return False

def login_is_active(login):
    """
    function that checks if the login in the database is active
    """
    user_rec = AdsUserRecord.query.filter(AdsUserRecord.username==login).first()    #@UndefinedVariable
    if not user_rec:
        return False
    return user_rec.active
    
def create_user(signup_form):
    """
    Function that inserts the user info in the local database before being activated
    and sends an email with the confirmation code
    """    
    #create an itsdangerous object to sign the verification email and encrypt the password
    itsd = URLSafeSerializer(config.ACCOUNT_VERIFICATION_SECRET)
    
    #send the confirmation email
    act_code = itsd.dumps(signup_form.login.data)
    message_html = """<h3>Dear %(name)s %(lastname)s, thank you for registering to the NASA ADS</h3>
                        <p>Your activation code is <strong>%(code)s</strong></p>
                        <p>To activate your account, please click <a href="%(act_url)s">here</a></p>
                        <p>If the link doesn't work, please copy the following URL and paste it in your browser:<br/>%(act_url)s</p>
                        <p>Please do not replay to this email: to contact us please use our <a href="%(feedb_url)s">feedback form</a></p>
                        <p>Regards,<br/>The ADS team</p>
                    """ % {'name':signup_form.name.data, 'lastname':signup_form.lastname.data, 'code':act_code, 
                           'act_url': '%s%s?id=%s' % (config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('user.activate'), act_code),
                           'feedb_url' : '%s%s'%(config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('feedback.feedback'))
                         }
    try:  
        send_email_to_user(u"NASA ADS Account confirmation required", message_html, [signup_form.login.data])
    except:
        app.logger.error('Failed to send confirmation email for user creation')
        return False, 'There are some technical problems: please try later.', 'error'
    
    #create a new user object
    new_rec = AdsUserRecord(cookie_id=g.user_cookie_id,  #temporary unique cookie id
                            username=signup_form.login.data, 
                            firstname=signup_form.name.data, 
                            lastname=signup_form.lastname.data,
                            password=itsd.dumps(signup_form.password.data),
                            registered=datetime.utcnow().replace(tzinfo=pytz.utc),
                            active=False, 
                            anonymous=False)
    #save the user
    new_rec.save()
    return True, 'Thanks for the registration. An email with the activation code has been sent to you.', 'success'

def resend_activation_email(email_to_activate):
    """
    Function to resend the activation email
    """
    #check local database
    loc_db_user = AdsUserRecord.query.filter(AdsUserRecord.username==email_to_activate) #@UndefinedVariable
    #get the user object
    user_rec = loc_db_user.first()
    if user_rec:
        #create an itsdangerous object to sign the verification email 
        itsd = URLSafeSerializer(config.ACCOUNT_VERIFICATION_SECRET)
        #send the confirmation email
        act_code = itsd.dumps(email_to_activate)
        message_html = """<h3>Dear %(name)s %(lastname)s, thank you for registering to the NASA ADS</h3>
                            <p>Your activation code is <strong>%(code)s</strong></p>
                            <p>To activate your account, please click <a href="%(act_url)s">here</a></p>
                            <p>If the link doesn't work, please copy the following URL and paste it in your browser:<br/>%(act_url)s</p>
                            <p>Please do not replay to this email: to contact us please use our <a href="%(feedb_url)s">feedback form</a></p>
                            <p>Regards,<br/>The ADS team</p>
                        """ % {'name':user_rec.firstname, 'lastname':user_rec.lastname, 'code':act_code, 
                               'act_url': '%s%s?id=%s' % (config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('user.activate'), act_code),
                               'feedb_url' : '%s%s'%(config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('feedback.feedback'))
                               }
        try:
            send_email_to_user(u"NASA ADS Account confirmation required", message_html, [email_to_activate])
        except:
            app.logger.error('Failed to re-send confirmation email for user creation')
            return False, 'There are some technical problems: please try later.', 'error'
        return True, 'A new email with the activation code has been sent to your email address.', 'success'
    else:
        app.logger.error('Tried to re-send confirmation email for user creation for user not yet created or not stored in the DB. Email used %s' % email_to_activate)
        return False, 'The user with the given email does not exist', 'error'

def activate_user(activation_code):
    """
    Function that activate an user given an activation code
    It takes care of the actual creation on ADS Classic
    """
    #create an itsdangerous object to un sign the verification code and decrypt the password
    itsd = URLSafeSerializer(config.ACCOUNT_VERIFICATION_SECRET)
    #decrypt the activation code
    try:
        login = itsd.loads(activation_code)
    except BadSignature:
        app.logger.error('Activation code not valid. Code used: %s' % activation_code)
        return False, 'Activation Code not valid.', 'error'
    #check local database
    loc_db_user = AdsUserRecord.query.filter(AdsUserRecord.username==login) #@UndefinedVariable
    #get the user object
    user_rec = loc_db_user.first()
    if not user_rec:
        app.logger.error('User activation error: user not in db. Email used: %s' % login)
        return False, 'Account not found', 'error'
    if user_rec.active:
        app.logger.warn('User account already active. Email from activation code used: %s' % login)
        return False, 'Account already active', 'warn'
    #if everything is of it's time to proceed
    try:
        classic_user = create_classic_user(user_rec.username, itsd.loads(user_rec.password), user_rec.firstname, user_rec.lastname)
    except TypeError:
        app.logger.error('ADS Classic account creation error. Email from activation code used: %s' % login)
        return False, 'Problems in the account creation. Please try later.', 'error'
    if classic_user:
        update_params = {}
        if classic_user.get('cookie'):
            update_params.update({'cookie_id':classic_user['cookie'], 'active' : True, 'password': '', 'remote_login_system':classic_user['request']['man_url']})
            #actual update in the DB
            loc_db_user.set(**update_params).execute()
            return True, 'Account activated', 'success'
        else:
            app.logger.error('User account activation failed on the classic user creation: user created but no cookie id in the response from classic. Email from activation code used: %s' % login)
            return False, 'Problems in the creation of the classic user', 'error'
    
    app.logger.error('User activation error. Classic user not created. Email from activation code used: %s' % login)
    return False, 'Problems in the account creation. Please try later.', 'error'



def change_user_settings(form):
    """
    Function that checks the current params against the submitted ones and 
    changes them in case are different. If the email is different a 
    confirmation email is sent before proceeding
    """
    #check if name and lastname need to be changed
    name = lastname = login = ''
    if form.name.data != current_user.user_rec.firstname:
        name = form.name.data
    if form.lastname.data != current_user.user_rec.lastname:
        lastname = form.lastname.data
    if form.login.data != current_user.user_rec.username:
        login = form.login.data
    
    #if the user submitted a form with no changes there is nothing to do    
    if not (name or lastname or login):
        app.logger.debug('The user submitted a form with no changes.')
        return False, 'Settings not changed. Please modify some settings to change them.', 'warning'
    
    #check if the login is already used: if so throw an error unless it is from the same
    if login:
        user_rec = AdsUserRecord.query.filter((AdsUserRecord.alternate_usernames == login).or_(AdsUserRecord.username == login)).first()  #@UndefinedVariable
        if user_rec and (user_rec.cookie_id != current_user.get_id()) :
            return False, 'email address already taken by other user.', 'error'
        #check if the user already exists in classic and has another cookie
        if login_exists_classic(login):
            classic_user = get_classic_user(login)
            if classic_user.get('cookie') != current_user.get_id():
                app.logger.error('User tried to use change his login using one belonging to other user. User login: %s; other user login: %s ' % (current_user.get_username(), login))
                return False, 'email address already taken by other user.', 'error'
        
        #send the confirmation email
        #create an itsdangerous object to sign the verification email 
        itsd = URLSafeSerializer(config.ACCOUNT_VERIFICATION_SECRET)
        #send the confirmation email
        act_code = itsd.dumps('%s||%s' % (login, current_user.user_rec.username))
        message_html = """<h3>Please confirm your new email address</h3>
                            <p>Your activation code is <strong>%(code)s</strong></p>
                            <p>To activate your account, please click <a href="%(act_url)s">here</a></p>
                            <p>If the link doesn't work, please copy the following URL and paste it in your browser:<br/>%(act_url)s</p>
                            <p>Please do not replay to this email: to contact us please use our <a href="%(feedb_url)s">feedback form</a></p>
                            <p>Regards,<br/>The ADS team</p>
                        """ % {'code':act_code, 
                               'act_url': '%s%s?id=%s' % (config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('user.activate_new_email'), act_code),
                               'feedb_url' : '%s%s'%(config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('feedback.feedback'))
                               }
        try:
            send_email_to_user(u"NASA ADS: confirmation required for login update", message_html, [login])
        except:
            app.logger.error('Failed to send confirmation email for user settings modification.')
            return False, 'There are some technical problems: please try later.', 'error'
    
    #if name or lastname have changed, submit the changes to the classic ads and update the local database
    if name or lastname:
        loc_db_user = AdsUserRecord.query.filter(AdsUserRecord.cookie_id == current_user.get_id())  #@UndefinedVariable
        user_rec = loc_db_user.first()
        if not user_rec:
            app.logger.error('logged in user doesn\'t have an entry in local mongo DB: %s' % login)
            return False, 'Error with account modification. Please try to logout and login again before trying again.', 'error'
        #make sure that if name or lastname are present, both are sent for the update
        if not name:
            name = user_rec.firstname
        if not lastname:
            lastname = user_rec.lastname
        
        try:
            classic_user = update_classic_user_info(current_user.user_rec.username, form.password.data, name, lastname)
        except TypeError:
            app.logger.error('ADS Classic account modification error: getting wrong json structure back. Tried to update name and lastname: %s' % login)
            return False, 'Problems in the account modification. Please try later.', 'error'
        if classic_user and classic_user.get('message') == 'ACCOUNT_UPDATED':
            update_params = {'firstname':name, 'lastname':lastname}
            loc_db_user.set(**update_params).execute()
        elif classic_user and classic_user.get('message') == 'WRONG_PASSWORD':
            app.logger.error('ADS Classic account modification error: wrong old password used. %s' % login)
            return False, 'The current password is wrong. Please try again.', 'error'
        else:
            app.logger.error('ADS Classic account modification error: return message not expected. %s' % login)
            return False, 'Problems in the account modification. Please try again.', 'error'
        
    if (name or lastname) and login:
        return True, 'Almost all the information have been updated. Please confirm your new email to update your username: a confirmation email has been sent to the new address.', 'warning'
    elif login and not (name or lastname):
        return True, 'You are almost done. Please confirm your new email to update your username: a confirmation email has been sent to the new address.', 'warning'
    elif (name or lastname) and not login:
        return True, 'All the changes have been applied.', 'success'
    #there should be no else
    else:
        app.logger.error('Account modification error. Case the app should never reach: %s' % login)
        return False, 'Error with account modification.', 'error'


def activate_user_new_email(form):
    """
    Function that takes care of updating the email address that is also the username
    """
    activation_code, curpassword = form.id.data, form.password.data
    
    #create an itsdangerous object to un sign the verification code and decrypt the password
    itsd = URLSafeSerializer(config.ACCOUNT_VERIFICATION_SECRET)
    #decrypt the activation code
    try:
        logins = itsd.loads(activation_code)
    except BadSignature:
        app.logger.error('Activation code not valid. Code used: %s' % activation_code)
        return False, 'Activation Code not valid.', 'error'
    emails = logins.split('||')
    if len(emails) != 2:
        app.logger.error('Number of emails in the activation code not valid. Code used: %s' % activation_code)
        return False, 'Activation Code not valid.', 'error'
    new_login, old_login = emails
    #if the current user is the right one
    if current_user.get_username() != old_login:
        return False, 'Please activate the new email with the correct account', 'error'
    else:
        #update ads classic
        try:
            classic_user = update_classic_username(old_login, new_login, curpassword)
        except TypeError:
            app.logger.error('ADS Classic account modification error. Tried to update email: old %s, new %s' % (old_login, new_login))
            return False, 'Problems in the account modification. Please try later.', 'error'
        if classic_user and classic_user.get('message') == 'ACCOUNT_UPDATED':
            loc_db_user = AdsUserRecord.query.filter(AdsUserRecord.username == old_login)  #@UndefinedVariable
            loc_db_user.add_to_set('alternate_usernames', old_login).set(username=new_login).execute()
            return True, 'The username %s is now active and should be used from now on to login to this account.' % new_login, 'success'
        elif classic_user and classic_user.get('message') == 'WRONG_PASSWORD':
            app.logger.error('ADS Classic account modification error: wrong old password used. Tried to update email: old %s, new %s' % (old_login, new_login))
            return False, 'The current password is wrong. Please try again.', 'error'
        else:
            app.logger.error('ADS Classic account modification error: return message not expected: Tried to update email: old %s, new %s' % (old_login, new_login))
            return False, 'Problems in the account modification. Please try again.', 'error'
    

def change_user_password(form):
    """
    Function that takes care of changing the user password in ADSClassic
    """
    old_password, new_password = form.old_password.data, form.new_password.data
    
    try:
        classic_user = update_classic_password(current_user.get_username(), old_password, new_password)
    except TypeError:
        app.logger.error('ADS Classic account modification error: getting wrong json structure back. Tried to update password for user: %s' % current_user.get_username())
        return False, 'Problems in the password update. Please try later.', 'error'
    
    if classic_user and classic_user.get('message') == 'ACCOUNT_UPDATED':
        return True, 'Password successfully updated.', 'success'
    elif classic_user and classic_user.get('message') == 'WRONG_PASSWORD':
        app.logger.error('ADS Classic account modification error: wrong old password used. Tried to update password: login %s' % current_user.get_username())
        return False, 'The current password is wrong. Please try again.', 'error'
    else:
        app.logger.error('ADS Classic account modification error: return message not expected. Tried to update password: login %s' % current_user.get_username())
        return False, 'Problems in the account modification. Please try again.', 'error'
    

def reset_user_password_step_one(form):
    """
    first step of the password reset: hash generated, email with hash sent
    """
    #create an itsdangerous object to sign the verification email and encrypt the password
    itsd = TimestampSigner(config.ACCOUNT_VERIFICATION_SECRET)
    #generate a temporary password
    temp_password = os.urandom(12).encode('hex')
    reset_code = itsd.sign(temp_password)
    time_limit = datetime.now() + timedelta(hours=3)
    #check local database
    loc_db_user = AdsUserRecord.query.filter(AdsUserRecord.username==form.login.data) #@UndefinedVariable
    #get the user object
    user_rec = loc_db_user.first()
    if not user_rec:
        app.logger.error('User password reset error: user not in db. Email used: %s' % form.login.data)
    else:
        #store the reset password locally
        loc_db_user.set(password=reset_code).execute()
            
        #sent the email
        message_html = """<h3>ADS Password reset</h3>
                                <p>Your temporary reset code is <strong>%(reset_code)s</strong></p>
                                <p>To complete the password reset, please click <a href="%(reset_url)s">here</a></p>
                                <p>If the link doesn't work, please copy the following URL and paste it in your browser:<br/>%(reset_url)s</p>
                                <p>This temporary reset code is valid only until %(password_time_limit)s<p>
                                <p>Please do not replay to this email: to contact us please use our <a href="%(feedb_url)s">feedback form</a></p>
                                <p>Regards,<br/>The ADS team</p>
                            """ % {'reset_code':reset_code, 
                                   'reset_url': '%s%s?login=%s&resetcode=%s' % (config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('user.confirm_reset_password'), form.login.data, reset_code),
                                   'feedb_url' : '%s%s'%(config.MAIL_CONTENT_REDIRECT_BASE_URL, url_for('feedback.feedback')),
                                   'password_time_limit': time_limit.strftime("%A, %d. %B %Y %I:%M%p")
                                   }
        try:
            send_email_to_user(u"NASA ADS: confirmation required for login update", message_html, [form.login.data])
        except Exception, e:
            app.logger.error('Failed to send reset email for user password: %s' % e)
            return False, 'There are some technical problems: please try later.', 'error'
    return True, 'If the email you entered exists in our system, you will shortly receive a message at your e-mail address with further instructions on how to reset your password.', 'warning'

def reset_user_password_step_two(form):
    """
    second step of the password reset: check that the hash matches the temp password, force the change on ads classic
    """
    #create an itsdangerous object to sign the verification email and encrypt the password
    itsd = TimestampSigner(config.ACCOUNT_VERIFICATION_SECRET)
    reset_code = form.resetcode.data
    try:
        code = itsd.unsign(reset_code, max_age=10800) #code valid only 3 hours
    except BadTimeSignature:
        app.logger.error('User password reset error: used reset code not valid. Email used: %s ; reset code: %s' % (form.login.data, reset_code))
        return False, 'The reset code is not valid.', 'error'
    except SignatureExpired:
        app.logger.error('User password reset error: used reset code expired. Email used: %s ; reset code: %s' % (form.login.data, reset_code))
        return False, 'The reset code has expired. Please request a new one.', 'error'
    
    #check if the reset code is the same stored in the DB
    loc_db_user = AdsUserRecord.query.filter(AdsUserRecord.username==form.login.data) #@UndefinedVariable
    #get the user object
    user_rec = loc_db_user.first()
    if reset_code != user_rec.password:
        app.logger.error('User password reset error: used valid reset code but it doesn\'t match the one in the DB. Email used: %s ; reset code: %s' % (form.login.data, reset_code))
        return False, 'The reset code is not valid.', 'error'
    else:
        #proceed with the actual reset
        classic_user = reset_classic_password(form.login.data, form.new_password.data)
        if classic_user and classic_user.get('message') == 'ACCOUNT_UPDATED':
            #remove the reset code from the password field of the local db
            loc_db_user.set(password='').execute()
            return True, 'Password successfully updated.', 'success'
        else:
            app.logger.error('ADS Classic account modification error: return message not expected. Tried to force update password: login %s' % form.login.data)
            return False, 'Problems in the account modification. Please try again.', 'error'
    
    