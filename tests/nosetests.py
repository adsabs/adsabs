'''
Created on Nov 26, 2012

@author: jluker
'''

import os
import sys
import nose

test_dir = os.path.abspath(os.path.dirname(__file__))
selenium_dir = os.path.join(test_dir, 'selenium')

argv = sys.argv[:]
argv += [test_dir, selenium_dir, '-v']
nose.main(argv=argv)