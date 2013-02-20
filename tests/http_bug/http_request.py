'''
Created on Feb 19, 2013

@author: jluker
'''
import os
import sys
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

from urllib2 import urlopen
from test_utils import *
from multiprocessing import Pool

def query():
    u = urlopen("http://adsx:8081/")
    return u.read()

class HttpTestCase(AdsabsBaseTestCase):

    def test_cannot_send_request_errors(self):
        p = Pool(24)
        num_requests = 10
        results = [p.apply_async(query) for x in range(num_requests)]
        success = sum([int(x.get()) for x in results])
        print >>sys.stderr, "successful requests: %d" % success
        self.assertEqual(success, num_requests)
        
if __name__ == '__main__':
    unittest2.main()
