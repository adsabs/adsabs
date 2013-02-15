'''
Created on Feb 14, 2013

@author: dimilia
'''

import os
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

import unittest2

from config import config
from test_utils import *

import adsabs.core.template_filters as tf

class TemplateFiltersTestCase(AdsabsBaseTestCase):
    
    def test_quote_url(self):
        self.assertEqual(tf.quote_url('foobar'), 'foobar')
        self.assertEqual(tf.quote_url('foo bar'), 'foo+bar')
        self.assertEqual(tf.quote_url('foo&bar'), 'foo%26bar')
        self.assertEqual(tf.quote_url('foo:bar%'), 'foo%3Abar%25')
        self.assertEqual(tf.quote_url('0/foobar'), '0/foobar')
        self.assertEqual(tf.quote_url('0/foo:bar%'), '0/foo%3Abar%25')
        self.assertEqual(tf.quote_url('1/foo:/bar%'), '1/foo%3A/bar%25')
        
    def test_format_ads_date(self):
        self.assertEqual(tf.format_ads_date('2010-01-01'), u'01 Jan 2010')
        self.assertEqual(tf.format_ads_date('2010-01-00'), u'Jan 2010')
        self.assertEqual(tf.format_ads_date('2010-00-00'), u'2010')
        self.assertEqual(tf.format_ads_date('9999-00-00'), u'9999')
        self.assertEqual(tf.format_ads_date(''), u'')
        self.assertRaises(ValueError, tf.format_ads_date, ('2010'))
        self.assertRaises(ValueError, tf.format_ads_date, ('2010-13-01'))
        
    def test_format_ads_facet_str(self):
        self.assertEqual(tf.format_ads_facet_str('Foobar'), 'Foobar')
        self.assertEqual(tf.format_ads_facet_str('0/Foobar'), 'Foobar')
        self.assertEqual(tf.format_ads_facet_str('1/Foo/bar'), 'bar')
        self.assertEqual(tf.format_ads_facet_str('Foo/bar'), 'Foo/bar')
       
    def test_safe_html_unescape(self):
        self.assertEqual(tf.safe_html_unescape('Foobar'), u'Foobar')
        self.assertEqual(tf.safe_html_unescape('<h1>Foobar</h1>'), u'<h1>Foobar</h1>')
        self.assertEqual(tf.safe_html_unescape('<h1>Foo<script>bar</script></h1>'), u'<h1>Foo</h1>')
        
    def test_ads_url_redirect(self):
        self.assertEqual(tf.ads_url_redirect('foo', 'bar'), 'foo')
        self.assertEqual(tf.ads_url_redirect('FOOBAR', 'doi'), '%s/cgi-bin/nph-abs_connect?fforward=http://dx.doi.org/FOOBAR' % config.ADS_CLASSIC_BASEURL)
        self.assertEqual(tf.ads_url_redirect('FOOBAR', 'data'), '%s/cgi-bin/nph-data_query?bibcode=FOOBAR&link_type=DATA' % config.ADS_CLASSIC_BASEURL)
        self.assertEqual(tf.ads_url_redirect('FOOBAR', 'electr'), '%s/cgi-bin/nph-data_query?bibcode=FOOBAR&link_type=EJOURNAL' % config.ADS_CLASSIC_BASEURL)
        self.assertEqual(tf.ads_url_redirect('FOOBAR', 'gif'), '%s/cgi-bin/nph-data_query?bibcode=FOOBAR&link_type=GIF' % config.ADS_CLASSIC_BASEURL)
        self.assertEqual(tf.ads_url_redirect('FOOBAR', 'article'), '%s/cgi-bin/nph-data_query?bibcode=FOOBAR&link_type=ARTICLE' % config.ADS_CLASSIC_BASEURL)
        self.assertEqual(tf.ads_url_redirect('FOOBAR', 'preprint'), '%s/cgi-bin/nph-data_query?bibcode=FOOBAR&link_type=PREPRINT' % config.ADS_CLASSIC_BASEURL)
        self.assertEqual(tf.ads_url_redirect('FOOBAR', 'arXiv'), '%s/cgi-bin/nph-abs_connect?fforward=http://arxiv.org/abs/FOOBAR' % config.ADS_CLASSIC_BASEURL)
        self.assertEqual(tf.ads_url_redirect('FOOBAR', 'simbad'), '%s/cgi-bin/nph-data_query?bibcode=FOOBAR&link_type=SIMBAD' % config.ADS_CLASSIC_BASEURL)
        self.assertEqual(tf.ads_url_redirect('FOOBAR', 'ned'), '%s/cgi-bin/nph-data_query?bibcode=FOOBAR&link_type=NED' % config.ADS_CLASSIC_BASEURL)
        self.assertEqual(tf.ads_url_redirect('FOOBAR', 'openurl'), '%s/cgi-bin/nph-data_query?bibcode=FOOBAR&link_type=OPENURL' % config.ADS_CLASSIC_BASEURL)


if __name__ == '__main__':
    unittest2.main()