# -*- coding: utf-8 -*-

import os
import sys

import tempfile
import subprocess
import logging

from flask.ext.script import Manager, Command, prompt, prompt_pass, prompt_bool #@UnresolvedImport
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

tools_manager = Manager("Tools commands")#, with_default_commands=False)

@manager.command
def run():
    """Run server that can be reached from anywhere."""
    app.run(host='0.0.0.0')
    
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

@tools_manager.command
def tools():
    """
    download and setup of extras in the ./tools directory
    TODO: we should really move this kind of stuff into a deployment/config-management
    tool, like fabric or maybe hudson
    """
    
    tools_dir = app.root_path + '/../tools'
    if os.environ.has_key('VIRTUAL_ENV'):
        activate = ". %s/bin/activate" % os.environ['VIRTUAL_ENV']
    else:
        activate = ""
        
    temp = tempfile.NamedTemporaryFile(delete=False)
    print >>temp, """#!/bin/bash
    
    %s
    cd %s
    pip install django
    git clone https://github.com/adsabs/mongoadmin.git
    cd mongoadmin
    cp mongoadmin_project/settings.py.dist mongoadmin_project/settings.py
    perl -p -i -e 's/django\.db\.backends\.mysql/django.db.backends.sqlite3/' mongoadmin_project/settings.py
    %s manage.py syncdb --noinput
    
    """ % (activate, tools_dir, sys.executable)
    
    temp.close()
    subprocess.call(["chmod", "755", temp.name])
    subprocess.call(["bash", temp.name])
    temp.unlink(temp.name)
    
    print """
    mongoadmin install is complete.
    Run by typing...
    
    cd tools/mongoadmin
    python manage.py runserver
    """

# register sub-managers
from adsabs.modules.api import manager as api_manager
manager.add_command('api', api_manager)
manager.add_command('tools', tools_manager)

if __name__ == "__main__":
    manager.run()
