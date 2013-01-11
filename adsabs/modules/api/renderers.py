'''
Created on Nov 2, 2012

@author: jluker
'''

import json
import flask

from flask.ext.pushrod.renderers import renderer #@UnresolvedImport
from adsabs.extensions import pushrod

VALID_FORMATS = []

def _register(renderer):
    VALID_FORMATS.extend(renderer.renderer_names)
    pushrod.register_renderer(renderer)
    
# json is the default rendering method
@renderer(name='json', mime_type=('application/json','text/html'))
def json_renderer(unrendered, **kwargs):
    return unrendered.rendered(
      json.dumps(unrendered.response),
      'application/json')
  
@renderer(name='xml', mime_type=('application/xml','text/xml'))
def xml_renderer(unrendered, xml_template=None, wrap=None, **kwargs):
    if xml_template:
        if wrap:
            content = {wrap: unrendered.response}
        else:
            content = unrendered.response
        return unrendered.rendered(
            flask.render_template(xml_template, **content),
            'text/xml')
    else:
        return NotImplemented
    
_register(json_renderer)
_register(xml_renderer)