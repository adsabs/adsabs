'''
Created on Apr 25, 2013

@author: jluker
'''

import redis
import logging
import simplejson as json

class RedisLogFormatter(logging.Formatter):

    def format(self, r):
        """
        expects a dict or a LogEvent (which acts as a dict) as the record's msg attribute
        """
        r.msg['@source_path'] = "%s, %s:%d" % (r.funcName, r.pathname, r.lineno)
        return json.dumps(r.msg)

class RedisLogHandler(logging.Handler):
    """
    Publish messages to a redis list.
    """

    @classmethod
    def create(klass, key, host='localhost', port=6379, level=logging.NOTSET, db=0):
        rc = redis.Redis(host=host, port=port, db=db)
        return klass(key, rc, level=level)

    def __init__(self, key, redis_client, level=logging.NOTSET):
        """
        Create a new logger for the given key and redis_client.
        """
        logging.Handler.__init__(self, level)
        self.key = key
        self.redis_client = redis_client
        self.formatter = RedisLogFormatter()

    def emit(self, record):
        """
        Publish record to redis logging list
        """
        try:
            self.redis_client.rpush(self.key, self.format(record))
        except redis.RedisError:
            pass