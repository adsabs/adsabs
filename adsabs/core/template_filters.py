'''
Created on Dec 10, 2012

@author: dimilia
'''
from urllib import quote_plus
from time import strftime, strptime
import jinja2
import scrubber

from config import config

__all__ = [
    'quote_url',
    'format_ads_date',
    'format_ads_facet_str',
    'safe_html_unescape',
    'ads_url_redirect',
    ]

def quote_url(value):
    """
    Return the simple urllib.quote_plus for a normal string
    But the in case of a string like 1/Fo o/Bar (hierarchical facets) it quotes only "Fo o" and "Bar"
    """
    #re-encode the unicode characters
    value = unicode(value).encode('utf-8')
    try:
        split_str = value.split('/')
        int(split_str[0])
    except ValueError:
        return quote_plus(value)
    
    if len(split_str) == 1:
        return quote_plus(value)
    
    ret_str = split_str[0]
    for elem in split_str[1:]:
        ret_str = '%s/%s' % (ret_str, quote_plus(elem))
    return ret_str
    
def format_ads_date(date_string):
    """
    Returns a formatted date given a numeric one
    """
    if not date_string:
        return u''
    elif date_string[5:7] == '00' and date_string[8:] == '00':
        return date_string[:4]
    elif date_string[8:] == '00':
        return u'%s %s' % (strftime('%b', strptime(date_string[5:7],'%m')), date_string[:4])
    else:
        return u'%s %s' % (strftime('%d %b', strptime(date_string[5:],'%m-%d')), date_string[:4])
        

def format_ads_facet_str(value):
    """
    Returns a string to be shown as a facet
    """
    try:
        split_str = value.split('/')
        int(split_str[0])
    except ValueError:
        return value
    if len(split_str) == 1:
        return value
    return split_str[-1]

def safe_html_unescape(html_str):
    """
    Returns a safely unescaped html string where the unsafe tags like <script> and their content is removed
    """
    return scrubber.Scrubber().scrub(jinja2.Markup(html_str).unescape())

def ads_url_redirect(adsid, id_type):
    """
    Returns an url that points to the urlbuilder in ADS Classic
    """
    if id_type=='doi':
        return "%s/cgi-bin/nph-abs_connect?fforward=http://dx.doi.org/%s" % (config.ADS_CLASSIC_BASEURL, adsid)
    elif id_type=='data':
        return "%s/cgi-bin/nph-data_query?bibcode=%s&link_type=DATA" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    elif id_type=='electr':
        return "%s/cgi-bin/nph-data_query?bibcode=%s&link_type=EJOURNAL" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    elif id_type=='gif':
        return "%s/cgi-bin/nph-data_query?bibcode=%s&link_type=GIF" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    elif id_type=='article':
        return "%s/cgi-bin/nph-data_query?bibcode=%s&link_type=ARTICLE" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    elif id_type=='preprint':
        return "%s/cgi-bin/nph-data_query?bibcode=%s&link_type=PREPRINT" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    elif id_type=='simbad':
        return "%s/cgi-bin/nph-data_query?bibcode=%s&link_type=SIMBAD" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    elif id_type=='ned':
        return "%s/cgi-bin/nph-data_query?bibcode=%s&link_type=NED" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    elif id_type=='openurl':
        return "%s/cgi-bin/nph-data_query?bibcode=%s&link_type=OPENURL" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    #here all the other needed cases
    else:
        return adsid

