'''
Created on Jun 4, 2013

@author: jluker
'''

from blinker import Namespace
my_signals = Namespace()

__all__ = ['error_signal','search_signal']

search_signal = my_signals.signal('solr-request')
error_signal = my_signals.signal('solr-error')