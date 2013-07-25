
import unittest2
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from config import config

def case_ins_contains(s):
    """
    lower-case() is only avialable in xslt 2.0, so we need to use this dumb hack
    """
    translate = "translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
    return "contains(%s, %s)" % (translate, s)

def wait_for_page(browser, elem_id, page_wait=config.SELENIUM_PAGE_WAIT):
        """
        call to make the process wait until a particular element has completed loading
        """
        w = WebDriverWait(browser, page_wait)
        w.until(lambda b: b.find_element_by_id(elem_id))
    
def start_page(browser, url=config.SELENIUM_BASE_URL):
    browser.get(url)
    
class AdsabsBaseSeleniumTestCase(unittest2.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.page_wait = config.SELENIUM_PAGE_WAIT
        
    def start_page(self, url=config.SELENIUM_BASE_URL):
        start_page(self.browser, url)
        
    def wait_for_page(self, id):
        wait_for_page(self.browser, id, self.page_wait)

    def tearDown(self):
        self.browser.close()