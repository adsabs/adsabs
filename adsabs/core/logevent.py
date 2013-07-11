'''
Created on Apr 30, 2013

@author: jluker
'''

import pytz
import socket
import datetime
from flask import request

class LogEvent(dict):
    
    @classmethod
    def new(cls, msg, **fields):
        event = cls()
        event['@message'] = msg
        if hasattr(request, 'remote_addr'):
            fields['client_addr'] = request.remote_addr
        event['@fields'] = fields
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
        self['@source'] = self['@source_host'] = socket.gethostname()
