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
        return u'%s %s' % (strftime('%b', strptime(date_string[5:7],'%m')), date_string[:4])
    else:
        return u'%s %s' % (strftime('%d %b', strptime(date_string[5:],'%m-%d')), date_string[:4])
        
