import unittest2
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from base import AdsabsBaseSeleniumTestCase, case_ins_contains
from config import config
import time

class BasicSearchTest(AdsabsBaseSeleniumTestCase):
    
    def test_basic_search(self):

        browser = self.browser
        self.start_page()
        self.assertIn("ADS 2.0", browser.title)
        
        query_input = browser.find_element_by_name("q")
        query_input.send_keys("black holes")
        query_input.send_keys(Keys.RETURN)

        self.wait_for_page("footer")
        
        self.assertIn("Search Results: black holes", browser.title)
        elements = browser.find_elements_by_xpath("//a[contains(@href, '&page=2')][contains(text(),'Next')]")
        self.assertTrue(len(elements) > 0)


if __name__ == '__main__':
    
    unittest2.main()