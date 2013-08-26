'''
Created on Jan 4, 2013

@author: jluker
'''

import sys
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
        app.logger.info("User dev_key: %s" % user.get_dev_key())
        app.logger.info(simplejson.dumps(user.get_dev_perms(), indent=True))
        
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
    