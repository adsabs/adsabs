import multiprocessing
import os

_basedir = os.path.dirname(__file__)
_logdir = os.path.join(_basedir, 'logs')
#bind = "unix:///tmp/gunicorn.socket"
bind = "0.0.0.0:8001"
workers = 10
max_requests = 100 #maximum number of requests before a worker is restarted
preload_app = True
chdir = os.path.dirname(__file__)
daemon = True
debug = False
accesslog = os.path.join(_logdir, 'access.log')
errorlog = os.path.join(_logdir, 'error.log')
pidfile = os.path.join(_logdir, 'gunicorn.pid')
