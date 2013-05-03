
import logging
import redis
from handler import *

def createLogger(app, logger_name, key=None, level=logging.INFO, propagate=0):
    """
    initialize a redis logger.
    handler will be a RedisLogHander, formatter will be a RedisLogFormatter.
    messages to the logger are expected to be LogEvent objects that
    provide a to_json_event() method
    """
    logger = logging.getLogger(logger_name)
    logger.propagate = propagate
    logger.setLevel(level)
    if app.config['REDIS_ENABLE']:
        if not key:
            key = "%s:%s" % (app.name, logger_name)
        host = app.config['REDIS_HOST']
        port = app.config['REDIS_PORT']
        db = app.config['REDIS_DATABASE']
        try:
            rc = redis.Redis(host=host, port=port, db=db)
            rc.info() # call this just to establish that connection is valid
            logger.addHandler(RedisLogHandler(key, rc, level))
        except redis.ConnectionError, e:
            app.logger.error("Redis connection failure! '%s' events will not be logged!: %s" \
                             % (logger_name, e))
    return logger