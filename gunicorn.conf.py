import multiprocessing

bind = "unix://tmp/gunicorn.socket"
workers = multiprocessing.cpu_count() * 2 + 1
max_requests = 100
preload_app = True
chdir = '/vagrant'
daemon = True
debug = False
errorlog = '/tmp/gunicorn.error.log'
