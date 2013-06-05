'''
Created on Jun 4, 2013

@author: jluker
'''

from blinker import Namespace
my_signals = Namespace()

__all__ = ['abstract_view_signal']

abstract_view_signal = my_signals.signal('abstract-view')
