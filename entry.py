# -*- coding: utf-8 -*-
"""
    wsgi
    ~~~~

    Deploy with gunicorn.
"""

import sys, os

PROJECT_ROOT = os.path.join(os.path.dirname(__file__))
sys.path.insert(0,PROJECT_ROOT)

from adsabs import create_app
application = create_app()
