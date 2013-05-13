'''
Created on Feb 15, 2013

@author: dimilia
'''

import os
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

import unittest2

from test_utils import AdsabsBaseTestCase

import adsabs.core.data_formatter as df

class DataFormatterTestCase(AdsabsBaseTestCase):
    
    def test_field_to_json(self):
        self.assertEqual(df.field_to_json(["foo", "bar"]), [])
        self.assertEqual(df.field_to_json(["{'foo':'bar'}"]), [])
        self.assertEqual(df.field_to_json(['{"foo":"bar"}']), [{u'foo': u'bar'}])
        self.assertEqual(df.field_to_json(['{"foo":"bar"}', '["foo", "bar"]']), [{u'foo': u'bar'}, [u'foo', u'bar']])


if __name__ == '__main__':
    unittest2.main()