import multiprocessing

bind = "unix:///tmp/gunicorn.socket"
#bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
max_requests = 100 #maximum number of requests before a worker is restarted
preload_app = True
chdir = '/vagrant/adsabs/'
daemon = True
debug = False
errorlog = '/tmp/gunicorn.error.log'
pidfile = '/tmp/gunicorn.pid'
