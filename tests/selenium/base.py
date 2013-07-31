
import os
import unittest2
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pyvirtualdisplay import Display

from config import test_config

virtualdisplay = None

def case_ins_contains(s):
    """
    lower-case() is only avialable in xslt 2.0, so we need to use this dumb hack
    """
    translate = "translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
    return "contains(%s, %s)" % (translate, s)

def wait_for_page(browser, elem_id, page_wait=test_config.SELENIUM_PAGE_WAIT):
        """
        call to make the process wait until a particular element has completed loading
        """
        w = WebDriverWait(browser, page_wait)
        w.until(lambda b: b.find_element_by_id(elem_id))
    
def start_page(browser, url=test_config.SELENIUM_BASE_URL):
    browser.get(url)
    
def get_browser():
    
    if test_config.SELENIUM_USE_REMOTE:
        dc = getattr(DesiredCapabilities, test_config.SELENIUM_DEFAULT_BROWSER.upper())
        dc['name'] = test_config.SELENIUM_TEST_NAME
        cmd_exec = test_config.SELENIUM_REMOTE_CMD_EXEC
        browser = webdriver.Remote(desired_capabilities=dc, command_executor=cmd_exec)
    else:
        global virtualdisplay
        virtualdisplay = Display(backend=test_config.SELENIUM_VIRTUALDISPLAY_BACKEND, size=(320, 240)).start()
        driver = getattr(webdriver, test_config.SELENIUM_DEFAULT_BROWSER)
        browser = driver()
    browser.implicitly_wait(test_config.SELENIUM_PAGE_WAIT)
    return browser

def close_browser(browser):
    browser.quit()
    global virtualdisplay
    virtualdisplay.stop()
    
class AdsabsBaseSeleniumTestCase(unittest2.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.page_wait = test_config.SELENIUM_PAGE_WAIT
        
    def start_page(self, url=test_config.SELENIUM_BASE_URL):
        start_page(self.browser, url)
        
    def wait_for_page(self, id):
        wait_for_page(self.browser, id, self.page_wait)

    def tearDown(self):
        self.browser.close()