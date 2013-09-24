'''
Created on Jul 11, 2013

@author: jluker
'''

import os
from functools import wraps
from flask import Blueprint, abort, render_template

from adsabs.modules.pages.content import ContentManager
from config import config

pages_blueprint = Blueprint('pages', __name__, 
                           template_folder="templates",
                           url_prefix=config.PAGES_URL_PREFIX,
                           static_folder=os.path.join(config.PAGES_CONTENT_DIR, 'static')
                           )

def templated(default_template=None):
    """
    allows view method to return a context dictionary that will be
    used to automatically render the template
    """
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            page_path = kwargs.get('page_path')
            
            # first try a page-specific template
            templates = [page_path + '.html']
            # then maybe a section-specific one
            if '/' in page_path:
                section = page_path.split('/')[0]
                templates.append(section + '.html')
            # fallback to generic page template
            templates.append(default_template)
            
            ctx = func(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(templates, **ctx)
        return decorated_function
    return decorator

@pages_blueprint.route('/<path:page_path>')
@pages_blueprint.route('/', defaults={'page_path': ''})
@templated(default_template="page.html")
def page(page_path):
    content_manager = ContentManager(config.PAGES_CONTENT_DIR)
    abs_path = content_manager.get_abs_path(page_path)
    if not os.path.exists(abs_path):
        abort(404)
    content, meta = content_manager.load_content(abs_path)
    title = meta.get('title', '') 
    return { 
        'content': content,
        'title': title
        }
    
        
        
        
        
        