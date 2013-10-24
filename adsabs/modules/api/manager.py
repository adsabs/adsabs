'''
Created on Jan 4, 2013

@author: jluker
'''

import sys
import gspread
import simplejson

from flask import current_app as app
from flask.ext.script import Manager, prompt, prompt_choices, prompt_bool #@UnresolvedImport
from config import config

manager = Manager("Perform api user operations", with_default_commands=False)

@manager.command
def useradd(email=None, level=None):
    """add an api user"""

    import api_user
    from adsabs.modules.user import AdsUser
    
    if not email:
        email = prompt("Enter e-mail address of Classic ADS account", "")
        if not len(email):
            sys.exit(1)
    if not level:
        level = prompt_choices("Enter developer permission level", sorted(api_user.PERMISSION_LEVELS.keys()), "basic")
        if level not in api_user.PERMISSION_LEVELS:
            sys.exit(1)
            
    user = AdsUser.from_email(email)
    if not user:
        app.logger.info("user not found")
        sys.exit(1)
        
    # first check if the user is already a dev
    user = api_user.AdsApiUser(user.user_rec)
    if user.is_developer():
        app.logger.info("User already has api access. Developer key: %s" % user.get_dev_key())
        if prompt_bool("Would you like to reset the user's permissions", False):
            user.set_perms(level)
            app.logger.info("API User permissions updated")
        return
            
    user = api_user.create_api_user(user, level)
    dev_key = user.get_dev_key()
    app.logger.info("API User created with %s permissions. Developer key: %s" % (level, dev_key))
    
    if prompt_bool("Send welcome message", True):
        sendwelcome(dev_key=dev_key, no_prompt=True)

    if prompt_bool("Update Google Spreadsheet", True):
        update_spreadsheet(user=user)    

@manager.command
def userinfo(email=None, dev_key=None):
    """dump the api-related parts of the mongo user record"""
    import api_user
    
    if email:
        user = api_user.AdsApiUser.from_email(email)
    elif dev_key:
        user = api_user.AdsApiUser.from_dev_key(dev_key)
    else:
        app.logger.error("You must provide an email address or dev_key for the lookup")
        sys.exit(1)
    
    if not user:
        app.logger.info("User not found")
    else:
        user_data = {
            'dev_key': user.get_dev_key(),
            'username': user.get_username(),
            'cookie': user.get_id(),
            'dev_perms': user.get_dev_perms(),
            }
        app.logger.info(simplejson.dumps(user_data, indent=True))
        
@manager.command
def userdel(email=None, dev_key=None):
    """remove a user's developer api status"""
    import api_user
    
    if email:
        user = api_user.AdsApiUser.from_email(email)
    elif dev_key:
        user = api_user.AdsApiUser.from_dev_key(dev_key)
    else:
        app.logger.error("You must provide an email address or dev_key for the lookup")
        sys.exit(1)
    
    if not user:
        app.logger.info("User not found")
    elif prompt_bool("Remove API access for user %s" % user.get_username(), True):
        user.set_dev_key("")
        user.set_perms(perms={})
        
@manager.command
def sendwelcome(email=None, dev_key=None, no_prompt=False):
    """send the welcome message to an api user"""
    import api_user
    
    if email:
        user = api_user.AdsApiUser.from_email(email)
    elif dev_key:
        user = api_user.AdsApiUser.from_dev_key(dev_key)
    else:
        app.logger.error("You must provide an email address or dev_key for the lookup")
        sys.exit(1)
    
    if not user:
        app.logger.info("User not found")
    else:
        if no_prompt or prompt_bool("Send welcome message to %s" % user.get_username(), True):
            user.send_welcome_message()
            app.logger.info("Welcome message sent")

@manager.command
def update_spreadsheet(email=None, user=None):
    """
    update the google signup spreadsheet with the user's dev_key value
    so that we know access has been granted
    """
    import api_user

    if email:
        user = api_user.AdsApiUser.from_email(email)
    elif user is None:
        app.logger.error("You must provide an email address for the lookup")
        sys.exit(1)
    
    if not user:
        app.logger.error("User not found: %s" % email)
        sys.exit()
        
    username = user.get_username()
    dev_key = user.get_dev_key()
    sheet = SignupSheet()
    
    if not sheet.has_signup(username):
        app.logger.info("No spreadsheet record found for user: %s" % username)
        return
        
    if sheet.get_dev_key(username) == dev_key:
        app.logger.info("dev_key is already up-to-date for %s" % username)
    else:
        try:
            sheet.set_dev_key(username, dev_key)
            app.logger.info("woot! dev_key updated for %s!" % username)
        except Exception, e:
            app.logger.error("something went wrong updating the dev_key cell: %s" % e)
            sys.exit(1)

@manager.command
def signups(all=False):
    """
    print out the current api access signups
    by default, will only show the ones with missing BEER logins and/or un-issued dev_keys
    """
    import api_user
    import string
    sheet = SignupSheet()
    print '%-50s %6s %20s' % ('email/username', 'login?', 'dev_key?')
    for email in sheet.signups():
        user = api_user.AdsApiUser.from_email(email)
        dev_key = sheet.get_dev_key(email)
        if user and dev_key and not all:
            continue
        print '%-50s %6s %20s' % (email, str(user is not None), str(dev_key))


class SignupSheet(object):
    
    def __init__(self):


        if config.API_SIGNUP_SPREADSHEET_KEY is None:
            raise RuntimeError("Signup spreadsheet config is missing!")
        try: 
            gc = gspread.login(*config.API_SIGNUP_SPREADSHEET_LOGIN)
            spreadsheet = gc.open_by_key(config.API_SIGNUP_SPREADSHEET_KEY)
        except Exception, e:
            app.logger.error(e)
            sys.exit(1)
            
        self.sheet = spreadsheet.sheet1

        col_headers = self.sheet.row_values(1)
        self.dev_key_col = col_headers.index('dev_key') + 1
        self.email_col = col_headers.index('Email') + 1
    
    def get_cell(self, value):
        try:
            return self.sheet.find(value)
        except gspread.exceptions.CellNotFound:
            pass
        
    def has_signup(self, email):
        return self.get_cell(email) is not None
    
    def get_dev_key(self, email):
        email_cell = self.get_cell(email)
        if email_cell is None:
            raise RuntimeError("No such signup: %s" % email)
        dev_key_cell = self.sheet.cell(email_cell.row, self.dev_key_col)
        return dev_key_cell.value
    
    def set_dev_key(self, email, dev_key):
        email_cell = self.get_cell(email)
        if email_cell is None:
            raise RuntimeError("No such signup: %s" % email)
        dev_key_cell = self.sheet.cell(email_cell.row, self.dev_key_col)
        self.sheet.update_cell(dev_key_cell.row, dev_key_cell.col, dev_key) 
        
    def signups(self):
        # don't return the first entry--that's the header
        return filter(lambda x: x and len(x.strip()), self.sheet.col_values(self.email_col)[1:])


          