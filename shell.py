# -*- coding: utf-8 -*-

import os
import sys

import tempfile
import subprocess

from flask.ext.script import Manager, prompt, prompt_pass, prompt_bool #@UnresolvedImport

from adsabs import create_app
from config import config

manager = Manager(create_app())

app = create_app(config)
project_root_path = os.path.join(os.path.dirname(app.root_path))

@manager.command
def run():
    """Run server that can be reached from anywhere."""
    app.run(host='0.0.0.0')

@manager.command
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

@manager.command
def create_api_user(email):
    from adsabs.modules.user import AdsUser
    user = AdsUser.from_email(email)
    
    
if __name__ == "__main__":
    manager.run()
