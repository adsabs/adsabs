'''
Test that a solr Term Vector response generates the proper data for a word clound
'''
import os
import sys
import site
import json
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

from adsabs.modules.visualization import solrjsontowordcloudjson as wc

class TestWordCloud(unittest.TestCase):

    def test_wc_json(self):
        with open('wc_solr_tvrh.json') as solrfp:
            solr_input = json.load(solrfp)
            wc_freq = wc.wc_json(solr_input)
        with open('wc_freq_shouldbe.json') as wcfp:
            wc_should = json.load(wcfp)
        self.assertEqual(wc_freq, wc_should)
        # save output to help comparisons
        #with open('wc_freq_is.json','w') as ofp:
        #    json.dump(wc_freq, ofp, sort_keys=True, indent=2)

if __name__ == '__main__':
    unittest.main()
        
