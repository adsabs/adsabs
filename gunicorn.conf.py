import multiprocessing
import os

_basedir = os.path.dirname(__file__)
_logdir = os.path.join(_basedir, 'logs')
#bind = "unix:///tmp/gunicorn.socket"
bind = "0.0.0.0:8001"
# this is a busy machine, so don't overdo it
workers = multiprocessing.cpu_count()
max_requests = 100 #maximum number of requests before a worker is restarted
preload_app = True
chdir = os.path.dirname(__file__)
# daemon mode does not work with supervisord; see http://gunicorn-docs.readthedocs.org/en/latest/deploy.html
daemon = False
debug = False
accesslog = os.path.join(_logdir, 'access.log')
errorlog = os.path.join(_logdir, 'error.log')
pidfile = os.path.join(_logdir, 'gunicorn.pid')
loglevel = 'debug'
# somehow these don't work -- the real IP is not captured in the gunicorn logfile
forwarded_allow_ips = '127.0.0.1'
proxy_allow_ips = '127.0.0.1'
