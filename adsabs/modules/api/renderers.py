'''
Created on Nov 2, 2012

@author: jluker
'''

import json
import flask

from flask.ext.pushrod.renderers import renderer #@UnresolvedImport
from adsabs.extensions import pushrod

# json is the default rendering method
@renderer(name='json', mime_type=('application/json','text/html'))
def json_renderer(unrendered, **kwargs):
  return unrendered.rendered(
      json.dumps(unrendered.response),
      'application/json')
  
@renderer(name='xml', mime_type=('application/xml','text/xml'))
def xml_renderer(unrendered, xml_template=None, **kwargs):
    if xml_template:
        return unrendered.rendered(
            flask.render_template(xml_template, **unrendered.response),
            'text/xml')
    else:
        return NotImplemented
    
pushrod.register_renderer(json_renderer)
pushrod.register_renderer(xml_renderer)