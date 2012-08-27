from flask import make_response

def ret_xml(str_text):
    """
    Function that creates a specific response object to return XML
    """
    response = make_response(str_text)
    response.headers['Content-Type'] = 'text/xml; charset=utf-8'
    return response