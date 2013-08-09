
import os
import re
import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions.meta import MetaPreprocessor

from config import config

EXTENSIONS = ['headerid']

def get_extensions():
    ext = [PagesExtension()]
    ext.extend(EXTENSIONS)
    return ext

class PagesExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        md.registerExtension(self)
        md.preprocessors.add("meta", HiddenMetaPreprocessor(md), "_begin")
        md.treeprocessors.add('rm_file_extension', RmFileExtTreeprocessor(self), "_end")

class RmFileExtTreeprocessor(Treeprocessor):
    """
    A custom markdown extension class that iterates through all <a> elements in 
    the document tree and removes the markdown file extension (".md") from the url path
    """
    def __init__(self, md):
        Treeprocessor.__init__(self, md)
        self.rx = re.compile(r'([/\w]+)(\%s)((?:\#[\w-]*)?)$' % config.PAGES_FILE_EXT)

    def run(self, root):
        for link in root.getiterator('a'):
            if not link.attrib.has_key('href'): continue
            href = self.rx.sub(r'\g<1>\g<3>', link.attrib['href'])
            link.attrib['href'] = href

class HiddenMetaPreprocessor(MetaPreprocessor):
    """
    Extra bit of preprocessing for metadata attribute extraction
    so that we can hide the metadata within '<!-- -->' comments
    """
    
    def run(self, lines):
        lines = filter(lambda l: l.strip() not in ['<!--','-->'], lines)
        return MetaPreprocessor.run(self, lines)
        