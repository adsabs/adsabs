'''
Created on Jul 31, 2013

@author: jluker
'''

class TestConfig(object):
    
    SELENIUM_USE_REMOTE = False
    SELENIUM_REMOTE_CMD_EXEC = None
    SELENIUM_PAGE_WAIT = 10
    SELENIUM_BASE_URL = "http://localhost:5000/"
    SELENIUM_DEFAULT_BROWSER = 'Firefox'
    SELENIUM_TEST_NAME = "adsabs selenium tests"
    SELENIUM_VIRTUALDISPLAY_BACKEND = 'xvfb'
    
try:
    from test_local_config import TestLocalConfig
except ImportError:
    TestLocalConfig = type('TestLocalConfig', (object,), dict())
    
for attr in filter(lambda x: not x.startswith('__'), dir(TestLocalConfig)):
    setattr(TestConfig, attr, TestLocalConfig.__dict__[attr])
    
test_config = TestConfig