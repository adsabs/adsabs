'''
Created on Dec 21, 2012

@author: dimilia
'''
import json

def field_to_json(field_list):
    """
    Function that transforms a solr o invenio field that contains a list of json strings to a list of json structures
    """
    def str_to_json(json_str):
        try:
            return json.loads(json_str)
        except:
            return None
    new_list = []
    for elem in field_list:
        json_obj = str_to_json(elem)
        if json_obj:
            new_list.append(json_obj)
    return new_list