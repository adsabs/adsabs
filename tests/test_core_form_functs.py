'''
Created on May 13, 2013

@author: dimilia
'''
import unittest2

from test_utils import AdsabsBaseTestCase

import adsabs.core.form_functs as ff

class DataFormatterTestCase(AdsabsBaseTestCase):
    
    def test_is_submitted_cust(self):
        """tests if a form is submitted in case of GET or POST request"""
        


if __name__ == '__main__':
    unittest2.main()