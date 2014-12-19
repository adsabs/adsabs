# -*- coding: utf-8 -*-
'''

flask-script tasks

registering sub-managers
========================

submanager modules should be placed in the adsabs.managers package and
imported into that package via __init__. The module should contain a Flask-Script Manager
object and include a 'name' attribute which will appear in the shell.py usage 
output and is what will # be used when executing subtasks in that manager
e.g.
%> python shell.py <submanager.name> <task> [args]

'''
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="wtforms")

import os
import sys

import tempfile
import subprocess
from time import sleep

from flask.ext.script import Manager, Command, prompt, prompt_pass, prompt_bool 
from flask import render_template

from adsabs import create_app
from config import config

config.LOGGING_LOG_TO_FILE = False
config.LOGGING_LOG_TO_CONSOLE = True
config.LOGGING_LOG_LEVEL = 'INFO'

if not getattr(config, 'SECRET_KEY', None):
    # set a fake one to keep the create_app from barfing
    config.SECRET_KEY = "foo"



app = create_app(config)    
manager = Manager(app)#, with_default_commands=False)

from adsabs import managers
for thing in dir(managers):
    if thing.startswith('__'):
        continue
    try:
        sub_manager = __import__('adsabs.managers.%s' % thing, globals(), locals(), [thing], -1)
        manager.add_command(sub_manager.name, sub_manager.manager)
    except ImportError, e:
        print e

@manager.command
def run(port=5000, debug=True):
    """Run server that can be reached from anywhere."""
    app.run(host='0.0.0.0', port=int(port), debug=debug)
    
@manager.command
def create_local_config():
    """Generate a local_config.py with necessary settings"""
    local_config_path = os.path.join(app.root_path, '../config/local_config.py')
    if os.path.exists(local_config_path):
        app.logger.info("local_config.py exists")
        if not prompt_bool("Overwrite"):
            return
    config_items = {}
    if prompt_bool("Generate SECRET_KEY", True):
        config_items['SECRET_KEY'] = os.urandom(24).encode('hex')
        config_items['ACCOUNT_VERIFICATION_SECRET'] = os.urandom(24).encode('hex')
    else:
        app.logger.warn("OK. You'll need to include a SECRET_KEY in local_config.py for the app to run.")
    output = render_template('config/local_config.py.tmpl', config_items=config_items)
    with open(local_config_path, 'w') as lc:
        print >>lc, output
    app.logger.info("local_config.py created")
        
@manager.command
def generate_secret_key():
    """Generate a random string suitable for using a the SECRET_KEY value"""
    app.logger.info("SECRET_KEY = '%s'" % os.urandom(24).encode('hex'))
    app.logger.info("ACCOUNT_VERIFICATION_SECRET = '%s'" % os.urandom(24).encode('hex'))
    
if __name__ == "__main__":
    manager.run()
