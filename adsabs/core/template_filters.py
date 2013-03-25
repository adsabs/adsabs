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
from flask import Markup
import dicttoxml


from config import config


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
    value = value.strip('()')
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
    return ''.join(ret_value)

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
    
