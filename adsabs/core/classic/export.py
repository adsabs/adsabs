'''
Created on Sep 5, 2013

@author: dimilia
'''

from flask import current_app as app
import requests
import sys
import traceback


__all__ = ['get_classic_records_export']

CLASSIC_EXPORT_URL = 'http://adsabs.harvard.edu/cgi-bin/nph-abs_connect'

def get_classic_records_export(bibcodes_list, export_format):
    """
    Fetches the metadata for the list of bibcodes in the specified list
    """
    
    parameters = {'bibcode' : ';'.join(bibcodes_list),
                  'data_type' : export_format
                  }
    headers = {'User-Agent':'ADS Script Request Agent'}
    
    #actual request
    r = requests.post(CLASSIC_EXPORT_URL, data=parameters, headers=headers)
    #check for errors
    try:
        r.raise_for_status()
    except Exception, e:
        exc_info = sys.exc_info()
        app.logger.error("Classic export http request error: %s, %s\n%s" % (exc_info[0], exc_info[1], traceback.format_exc()))
        
        return 'Error'
    
    #get all the lines of the response
    result = r.text.split('\n')
    
    #if there are enough rows, remove the header of the page
    if len(result) > 5:
        result = result[5:]
    
    return '\n'.join(result)