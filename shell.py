# -*- coding: utf-8 -*-

import os
import sys

import tempfile
import subprocess
import logging

from flask.ext.script import Manager, Command, prompt, prompt_choices, prompt_bool #@UnresolvedImport

from adsabs import create_app
from config import config

config.LOGGING_CONFIG = None
logging.basicConfig(format='%(message)s', level=logging.INFO)

app = create_app(config)
manager = Manager(app)#, with_default_commands=False)

log = logging.getLogger("shell")

tools_manager = Manager("Tools commands")#, with_default_commands=False)

@manager.command
def run():
    """Run server that can be reached from anywhere."""
    app.run(host='0.0.0.0')

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
