#!/usr/bin/env python
import os
import readline
from pprint import pprint

from flask import *
from app import *

os.environ['PYTHONINSPECT'] = 'True'

from adslabs import app
from adslabs import model

app = app()
ctx = app.test_request_context()
ctx.push()
ses = model.session
