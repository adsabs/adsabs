
import logging
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
        handler = RedisLogHandler.create(key, host, port, level, db)
        logger.addHandler(handler)
    return logger