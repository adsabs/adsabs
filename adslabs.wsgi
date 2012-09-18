# -*- coding: utf-8 -*-
"""
    wsgi
    ~~~~

    Deploy with apache2 wsgi.
"""

import sys, os, pwd
# http://code.google.com/p/modwsgi/wiki/ApplicationIssues#User_HOME_Environment_Variable
os.environ['HOME'] = pwd.getpwuid(os.getuid()).pw_dir

BASE_DIR = os.path.join(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from adsabs import create_app
application = create_app()