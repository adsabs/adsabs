'''
Created on Apr 30, 2013

@author: jluker
'''

import pytz
import socket
import logging
import datetime
from flask import request

def log_event(logger, **kwargs):
    if not kwargs.has_key('msg'):
        kwargs['msg'] = request.url
    event = LogEvent.new(**kwargs)
    logging.getLogger(logger).info(event)   
    
class LogEvent(dict):
    
    @classmethod
    def new(cls, msg, **fields):
        event = cls()
        event['message'] = msg
        if hasattr(request, 'remote_addr'):
            fields['client_addr'] = request.remote_addr
        event.update(fields)
        event.init()
        return event
    
    def __init__(self, *args):
        dict.__init__(self, *args)
        
    def init(self):
        """
        this method should be overridden in subclasses
        """
        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        self['@timestamp'] = now.isoformat()
        self['source'] = self['source_host'] = socket.gethostname()
