'''
Created on Dec 10, 2012

@author: dimilia
'''
from urllib import quote_plus
from time import strftime, strptime
import jinja2
import scrubber
import re
from werkzeug import url_decode, url_encode
from flask import Markup, json
import dicttoxml
import math
import sys
import itertools


from config import config
from adsabs.core import get_global_messages


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

def format_complex_ads_facet_str(value):
    """
    Returns a string that can be used as human readable facet
    """
    if not value.startswith('-'):
        value = value.strip('()[]')
    ret_value = []
    tmp_quoted_str = []
    quoted_section = False
    for char in value:
        if char != '"' and not quoted_section:
            ret_value.append(char)
        elif char != '"' and quoted_section:
            tmp_quoted_str.append(char)
        elif char == '"' and not quoted_section:
            quoted_section = True
            ret_value.append(char)
        elif char == '"' and quoted_section:
            quoted_section = False
            ret_value = ret_value + list(format_ads_facet_str(''.join(tmp_quoted_str)))
            ret_value.append(char)
            tmp_quoted_str = []
    return ''.join(ret_value)

def format_special_ads_facet_str(value):
    """
    Returns a formatted version of a facet string in very special cases, like "notrefereed" that needs to be transformed to "not refereed"
    But any other special case can be added here (and in the tests)
    """
    if value == 'notrefereed':
        return u'non-refereed'
    
    #in any other case returns the original string
    return value

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
    elif id_type=='arXiv':
        return "%s/cgi-bin/nph-abs_connect?fforward=http://arxiv.org/abs/%s" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    elif id_type=='simbad':
        return "%s/cgi-bin/nph-data_query?bibcode=%s&link_type=SIMBAD" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    elif id_type=='ned':
        return "%s/cgi-bin/nph-data_query?bibcode=%s&link_type=NED" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    elif id_type=='openurl':
        return "%s/cgi-bin/nph-data_query?bibcode=%s&link_type=OPENURL" % (config.ADS_CLASSIC_BASEURL, quote_plus(adsid))
    #here all the other needed cases
    else:
        return adsid
    
def facet_id_to_html_id(facet_id):
    """
    Returned a html compatible version of some id:
    removes commas, dots and any other character not compatible with an id
    and replace them with underscores
    """
    replace_pattern = '[^_A-Za-z0-9]'
    re_obj = re.compile(replace_pattern)
    return re_obj.sub('_', facet_id)

def facet_get_next_level_prefix(facet):
    """
    Given an hierarchical facet it returns the prefix for the second level of this facet
    """
    try:
        facet_split = facet.strip('/').split('/')
        num_prefix = int(facet_split[0])
    except (IndexError, ValueError):
        #if the first element is not an integer I cannot create the prefix for the next level
        #simply because it's not an hierarchical facet
        return facet
    return '%s/%s/' % (num_prefix+1, '/'.join(facet_split[1:]))

def get_prev_level_applied_facets(applied_facet_list, level=1):
    """
    Given a list of hierarchical facets that have been applied, it returns the unique prefixes of the previous level
    It works only with a level >0
    """
    if not applied_facet_list or not isinstance(level, (int, long)):
        return []
    if level <1:
        return []
    return list(set(['%s/%s' % (level-1, '/'.join(elem.split('/')[1:-1])) for elem in applied_facet_list if elem.split('/')[0]==str(level)]))

def update_param_url_query_str(url_query_string, param_name, new_val, old_val=None):
    """
    Given an url query string this function:
    1- updates the all the param_name with the new_val if old_val=None (only one instance after the update)
    2- updates the all the param_name containing old_val with the new_val if old_val!=None
    """
    if not param_name or not new_val:
        return url_query_string
    query_params = url_decode(url_query_string)
    #if I don't have the param_name I don't need to update
    if not query_params.has_key(param_name):
        return url_query_string
    #case 1
    if new_val and not old_val:
        query_params.setlist(param_name, [new_val])
        return url_encode(query_params)
    #case 2
    elif new_val and old_val:
        query_params.setlist(param_name, [new_val if old_val==elem else elem for elem in query_params.getlist(param_name)])
        return url_encode(query_params)
    else:
        url_query_string

def insert_param_url_query_str(url_query_string, param_name, param_val):
    """
    Given an url query string this function:
    appends a new instance of param_name containing param_val (it doesn't remove existing ones)
    """
    if not param_name or not param_val:
        return url_query_string
    query_params = url_decode(url_query_string)
    query_params.update({param_name:param_val})
    return url_encode(query_params)

def remove_param_url_query_str(url_query_string, param_name, param_val=None):
    """
    Given an url query string this function:
    1- removes all the param_name if param_val=None
    2- removes all the param_name containing param_val if param_val!=None
    """
    if not param_name:
        return url_query_string
    query_params = url_decode(url_query_string)
    #if I don't have the param_name I don't need to remove
    if not query_params.has_key(param_name):
        return url_query_string
    #case 1
    if not param_val:
        query_params.setlist(param_name, [])
        return url_encode(query_params)
    #case 2
    else:
        query_params.setlist(param_name, [facet_val for facet_val in query_params.getlist(param_name) if facet_val != param_val])
        return url_encode(query_params)


def boundaries_for_range_facets(first, last, num_div):
    """
    returns an array of 'boundaries' for producing approx num_div
    segments between first and last.  The boundaries are 'nicefied'
    to factors of 5 or 10, so exact number of segments may be more
    or less than num_div. Algorithm copied from Flot.
    
    Because of arithmetic issues with creating boundaries that will
    be turned into inclusive ranges, the FINAL boundary will be one
    unit more than the actual end of the last range later computed.
    
    Translated from the Ruby function in the blacklight_range_limit add on
    """
    #Cribbed from Flot.  Round to nearby lower multiple of base
    def floor_in_base(n, base):
        return base * math.floor(n / base)
    # arithmetic issues require last to be one more than the actual
    # last value included in our inclusive range
    last += 1
    # code cribbed from Flot auto tick calculating, but leaving out
    # some of Flot's options becuase it started to get confusing. 
    delta = float(last - first) / num_div
    # Don't know what most of these variables mean, just copying
    # from Flot. 
    dec = int(-1 * ( math.log10(delta) ))
    magn = float(10 ** (-1 * dec))
    # norm is between 1.0 and 10.0
    if magn == 0:
        norm = delta
    else:
        norm = (delta / magn)
    
    size = 10
    if (norm < 1.5):
        size = 1
    elif (norm < 3):
        size = 2
        # special case for 2.5, requires an extra decimal
        if (norm > 2.25 ):
            size = 2.5
            dec = dec + 1                
    elif (norm < 7.5):
        size = 5
    size = size * magn
    boundaries = []     
    start = floor_in_base(first, size)
    i = 0
    prev = sys.float_info.max
    v = 0
    while ( v < last and v != prev):
        #at the first cycle invert the values to have the same situation there was in ruby
        if i == 0:
            prev, v = v, prev
        prev = v
        v = start + i * size
        boundaries.append(int(v))
        i += 1
    boundaries = list(set(boundaries))
    boundaries = [x for x in boundaries if first < x < last]
    ret_boundaries = [first]
    ret_boundaries.extend(boundaries)
    ret_boundaries.append(last)
    return sorted(ret_boundaries)

def numeric_facets_to_histogram(facets_list):
    """
    Function to transform a list of numeric facets in a list of values useful for an histogram representation
    """
    if len(facets_list) == 0:
        return {'min':0, 'max':0, 'histogram':[((0, 0), 0)]}
    #Remove the "Easter egg" from the search result
    if facets_list[-1][0] == '2314':
        facets_list.pop()
    #convert facets to a dictionary for easy access 
    facets_dict = dict([ elem[:2] for elem in facets_list])
    #approx max number of buckets to create
    num_div = 10
    #I get the min and max value from the list
    facets_list.sort()
    try:
        first, last = int(facets_list[0][0]), int(facets_list[-1][0])
    except (ValueError, IndexError):
        first, last = 0, 0
    #extract the boundaries of each group
    boundaries = boundaries_for_range_facets(first, last, num_div)
    #fill the histogram
    histogram = [((couple[0], couple[1]-1), sum([facets_dict.get(str(fac_year), 0) for fac_year in xrange(couple[0], couple[1])])) for couple in itertools.izip(boundaries[:-1], boundaries[1:])]
    return {'min':first, 'max':last, 'histogram':histogram}
    
def configure_template_filters(app):
    """
    Function to configure the template filters inside a given app
    Moved here from the app module
    """
    @app.template_filter('urlencode')
    def urlencode_filter(value):
        return quote_url(value)
    
    @app.template_filter('format_ads_date')
    def f_a_d(date_string):
        return format_ads_date(date_string)
    
    @app.template_filter('format_ads_facet_str')
    def f_a_f_s(facet_string):
        return format_ads_facet_str(facet_string)
    
    @app.template_filter('format_complex_ads_facet_str')
    def f_c_a_f_s(facet_string):
        return format_complex_ads_facet_str(facet_string)
    
    @app.template_filter('format_special_ads_facet_str')
    def f_s_a_f_s(facet_string):
        return format_special_ads_facet_str(facet_string)
    
    @app.template_filter('safe_html_unescape')
    def s_h_f(html_string):
        return safe_html_unescape(html_string)
    
    @app.template_filter('ads_url_redirect')
    def a_u_r(adsid, id_type):
        return ads_url_redirect(adsid, id_type)
    
    @app.template_filter('dict2xml')
    def d_2_x(d):
        xml = dicttoxml.dicttoxml(d, root=False)
        return Markup(xml)
    
    @app.template_filter('facet_to_id')
    def f_2_i(facet_id):
        return facet_id_to_html_id(facet_id)
    
    @app.template_filter('facet_next_level_prefix')
    def f_g_n_l_p(hier_facet):
        return facet_get_next_level_prefix(hier_facet)
    
    @app.template_filter('get_prev_level_applied_facets')
    def g_p_l_a_f(applied_facet_list, level=1):
        return get_prev_level_applied_facets(applied_facet_list, level)
        
    @app.template_filter('upd_par_url')
    def u_p_u_q_s(url_query_string, param_name, new_val, old_val=None):
        return update_param_url_query_str(url_query_string, param_name, new_val, old_val)
    
    @app.template_filter('ins_par_url')
    def i_p_u_q_s(url_query_string, param_name, param_val):
        return insert_param_url_query_str(url_query_string, param_name, param_val)
    
    @app.template_filter('rem_par_url')
    def r_p_u_q_s(url_query_string, param_name, param_val=None):
        return remove_param_url_query_str(url_query_string, param_name, param_val)
    
    @app.template_filter('numeric_facets_to_histogram')
    def n_f_t_h(facets_list):
        return numeric_facets_to_histogram(facets_list)
    
    @app.template_filter('get_messages')
    def g_g_m(categories):
        return get_global_messages(with_categories=True, category_filter=categories)

    @app.template_filter('to_json')
    def to_json(value):
        return json.dumps(value)    

    # like this we can make a filter available inside templates (macros)
    # ie. like get_flashed_messages() - however it is not a good practice
    # we should use it very carefully
    #app.jinja_env.globals.update(get_x_messages=g_g_m)
