#!/usr/bin/env python
import os
import readline
from pprint import pprint

from flask import *
from app import *

os.environ['PYTHONINSPECT'] = 'True'

from adslabs import create_app
from adslabs import models

app = create_app()
ctx = app.test_request_context()
ctx.push()
ses = models.session
