'''
Created on Jul 22, 2013

@author: jluker
'''

import os
import re
import markdown
from hashlib import md5
from flask import render_template, abort, current_app as app
from config import config
from .markdown_extensions import get_extensions

__all__ = ['ContentManager']

class ContentManager(object):
    
    def __init__(self, content_path):
        self.content_path = content_path
        extensions = get_extensions()
        self.md = markdown.Markdown(extensions=extensions)
    
    def get_abs_path(self, page_path):
        """
        Transform the relative path into the full path to a content page
        """
        try:
            abs_path = os.path.join(self.content_path, page_path) + config.PAGES_FILE_EXT
            assert os.path.exists(abs_path)
        except AssertionError:
            abs_path = os.path.join(self.content_path, page_path, config.PAGES_DEFAULT_INDEX) + config.PAGES_FILE_EXT
        return abs_path

            
    def load_content(self, abs_path):
        """
        Takes the absolute path to a content page and returns
        the content converted from markdown
        """
        content = open(abs_path, 'r').read()
        content = gfm(content)
        content = content.decode('utf-8','ignore')
        content = self.md.convert(content)
        return content, PageMeta(self.md.Meta)
    
    def page_title(self, pagename):
        return pagename.replace('_', ' ')
    
class PageMeta(object):
    """
    simple interface to the values extracted by the markdown metadata extension
    """
    def __init__(self, meta):
        self.meta = meta
        
    def get(self, key, default=None):
        val = self.meta.get(key, [])
        return val and val[0] or default
    
    def get_all(self, key):
        return self.meta.get(key, [])

def gfm(text):
    """
    Handles a few oddities of github-flavored markdown
    copied from: https://gist.github.com/mvasilkov/710689
    """
    # Extract pre blocks.
    extractions = {}
    def pre_extraction_callback(matchobj):
        digest = md5(matchobj.group(0)).hexdigest()
        extractions[digest] = matchobj.group(0)
        return "{gfm-extraction-%s}" % digest
    pattern = re.compile(r'<pre>.*?</pre>', re.MULTILINE | re.DOTALL)
    text = re.sub(pattern, pre_extraction_callback, text)

    # Prevent foo_bar_baz from ending up with an italic word in the middle.
    def italic_callback(matchobj):
        s = matchobj.group(0)
        if list(s).count('_') >= 2:
            return s.replace('_', '\_')
        return s
    pattern = re.compile(r'^(?! {4}|\t)\w+(?<!_)_\w+_\w[\w_]*', re.MULTILINE | re.UNICODE)
    text = re.sub(pattern, italic_callback, text)

    # In very clear cases, let newlines become <br /> tags.
    def newline_callback(matchobj):
        if len(matchobj.group(1)) == 1:
            return matchobj.group(0).rstrip() + '  \n'
        else:
            return matchobj.group(0)
    pattern = re.compile(r'^[\w\<][^\n]*(\n+)', re.MULTILINE | re.UNICODE)
    text = re.sub(pattern, newline_callback, text)

    # Insert pre block extractions.
    def pre_insert_callback(matchobj):
        return '\n\n' + extractions[matchobj.group(1)]
    text = re.sub(r'{gfm-extraction-([0-9a-f]{32})\}', pre_insert_callback, text)

    return text