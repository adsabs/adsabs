'''
Created on Dec 10, 2012

@author: dimilia
'''
from urllib import quote_plus
from time import strftime, strptime

def quote_url(value):
    """
    Very basic function
    """
    return quote_plus(value)

def format_ads_date(date_string):
    """
    Returns a formatted date given a numeric one
    """
    if not date_string:
        return u''
    elif date_string[5:7] == '00' and date_string[8:] == '00':
        return date_string[:4]
    elif date_string[8:] == '00':
        return strftime('%b %Y', strptime(date_string[:7],'%Y-%m'))
    else:
        return strftime('%d %b %Y', strptime(date_string,'%Y-%m-%d'))
        