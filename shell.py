# -*- coding: utf-8 -*-

import os
import sys

import tempfile
import subprocess
from time import sleep

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
    
@manager.command
def start_beaver():
    """
    starts a beaver daemon for transmitting log files to the redis/logstash
    """
    pid_path = os.path.join(app.root_path, '../.beaver.pid')
    if os.path.exists(pid_path):
        with open(pid_path, 'r') as pid:
            raise Exception("looks like another beaver process is running: %s" % pid.read())
            
    config_path = os.path.join(app.root_path, '../config/beaver.conf')
    if not os.path.exists(config_path):
        raise Exception("no config file found at %s" % config_path)
    
    beaver_log = os.path.join(app.root_path, '../logs/beaver.log')
    p = subprocess.Popen(["beaver",
                          "-D", # daemonize
                          "-c", config_path,
                          "-P", pid_path,
                          "-l", beaver_log
                          ])
    sleep(1)
    with open(pid_path, 'r') as pid:
        app.logger.info("beaver daemon started with pid %s" % pid.read())

@manager.command
def stop_beaver():
    """
    stops a running beaver daemon identified by the pid in app.root_path/.beaver.pid
    """
    import signal
    pid_path = os.path.join(app.root_path, '../.beaver.pid')
    if not os.path.exists(pid_path):
        raise Exception("There doesn't appear to be a pid file for a running beaver instance")
    pid = int(open(pid_path,'r').read())
    os.kill(pid, signal.SIGTERM)
    sleep(1)
    # Check that we really killed it
    try: 
        os.kill(pid, 0)
        raise Exception("""wasn't able to kill the process 
                        HINT:use signal.SIGKILL or signal.SIGABORT""")
    except OSError:
        app.logger.info("killed beaver process with pid %d" % pid)

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
