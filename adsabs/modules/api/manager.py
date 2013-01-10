'''
Created on Jan 4, 2013

@author: jluker
'''

import sys
import logging
import simplejson

from flask.ext.script import Manager, prompt, prompt_choices, prompt_bool #@UnresolvedImport
from config import config

manager = Manager("Perform api user operations", with_default_commands=False)

log = logging.getLogger(__name__)

@manager.command
def useradd(email=None, level=None):
    """add an api user"""

    from adsabs.modules.user import AdsUser
    from adsabs.modules.api import user
    
    if not email:
        email = prompt("Enter e-mail address of Classic ADS account", "")
        if not len(email):
            sys.exit(1)
    if not level:
        level = prompt_choices("Enter developer permission level", sorted(user.PERMISSION_LEVELS.keys()), "basic")
        if level not in user.PERMISSION_LEVELS:
            sys.exit(1)
            
    ads_user = AdsUser.from_email(email)
    if not ads_user:
        log.info("user not found")
        sys.exit(1)
        
    # first check if the user is already a dev
    api_user = user.AdsApiUser(ads_user.user_rec)
    if api_user.is_developer():
        log.info("User already has api access. Developer key: %s" % api_user.get_dev_key())
        if prompt_bool("Would you like to reset the user's permissions", False):
            api_user.set_perms(level)
            log.info("API User permissions updated")
        return
            
    api_user = user.create_api_user(ads_user, level)
    dev_key = api_user.get_dev_key()
    log.info("API User created with %s permissions. Developer key: %s" % (level, dev_key))
    
    if prompt_bool("Send welcome message", True):
        sendwelcome(dev_key=dev_key, no_prompt=True)
    
@manager.command
def userinfo(email=None, dev_key=None):
    """dump the api-related parts of the mongo user record"""
    from adsabs.modules.api import user
    
    if email:
        api_user = user.AdsApiUser.from_email(email)
    elif dev_key:
        api_user = user.AdsApiUser.from_dev_key(dev_key)
    else:
        log.error("You must provide an email address or dev_key for the lookup")
        sys.exit(1)
    
    if not api_user:
        log.info("User not found")
    else:
        log.info("User dev_key: %s" % api_user.get_dev_key())
        log.info(simplejson.dumps(api_user.get_dev_perms(), indent=True))
        
@manager.command
def userdel(email=None, dev_key=None):
    """remove a user's developer api status"""
    from adsabs.modules.api import user
    
    if email:
        api_user = user.AdsApiUser.from_email(email)
    elif dev_key:
        api_user = user.AdsApiUser.from_dev_key(dev_key)
    else:
        log.error("You must provide an email address or dev_key for the lookup")
        sys.exit(1)
    
    if not api_user:
        log.info("User not found")
    elif prompt_bool("Remove API access for user %s" % api_user.get_username(), True):
        api_user.set_dev_key("")
        api_user.set_perms(perms={})
        
@manager.command
def sendwelcome(email=None, dev_key=None, no_prompt=False):
    """send the welcome message to an api user"""
    from adsabs.modules.api import user
    
    if email:
        api_user = user.AdsApiUser.from_email(email)
    elif dev_key:
        api_user = user.AdsApiUser.from_dev_key(dev_key)
    else:
        log.error("You must provide an email address or dev_key for the lookup")
        sys.exit(1)
    
    if not api_user:
        log.info("User not found")
    else:
        if no_prompt or prompt_bool("Send welcome message to %s" % api_user.get_username(), True):
            api_user.send_welcome_message()
            log.info("Welcome message sent")
    