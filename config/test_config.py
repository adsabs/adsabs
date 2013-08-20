'''
Created on Jul 31, 2013

@author: jluker
'''
import sys
import easyprocess
from pyvirtualdisplay import Display

class TestConfig(object):
    
    SELENIUM_PAGE_WAIT = 30
    SELENIUM_BASE_URL = "http://localhost:5000/"
    SELENIUM_TEST_NAME = "adsabs selenium tests"
    SELENIUM_USE_VIRTUALDISPLAY = True
    SELENIUM_VIRTUALDISPLAY_BACKEND = 'xvfb'
    SELENIUM_FIREFOX_PATH = None
    
try:
    if TestConfig.SELENIUM_USE_VIRTUALDISPLAY:
        d = Display(backend=TestConfig.SELENIUM_VIRTUALDISPLAY_BACKEND, size=(600, 800))
except:
    print >>sys.stderr, "%s initialization failed. Selenium tests won't use virtualdisplay." % TestConfig.SELENIUM_VIRTUALDISPLAY_BACKEND
    TestConfig.SELENIUM_USE_VIRTUALDISPLAY = False

try:
    from test_local_config import TestLocalConfig
except ImportError:
    TestLocalConfig = type('TestLocalConfig', (object,), dict())
    
for attr in filter(lambda x: not x.startswith('__'), dir(TestLocalConfig)):
    setattr(TestConfig, attr, TestLocalConfig.__dict__[attr])
    
test_config = TestConfig
