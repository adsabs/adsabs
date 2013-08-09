'''
Created on Nov 5, 2012

@author: jluker
'''
import os
import fixtures
import shutil
import tempfile
import unittest2 as unittest

from config import config
from test_utils import AdsabsBaseTestCase

class PageFixture(fixtures.Fixture):
    
    def __init__(self, content_dir, content):
        self.content_dir = content_dir
        self.content = content
        
    def setUp(self):
        super(PageFixture, self).setUp()
        self.tempfile = tempfile.mktemp(config.PAGES_FILE_EXT, None, self.content_dir)
        self.tempfile.write(self.content)
        self.tempfile.flush()
        self.addCleanup(lambda obj: obj.tempfile.close(), self)
        
class PagesTestCase(AdsabsBaseTestCase):

    def setUp(self):
        super(PagesTestCase, self).setUp()
        self.content_dir = self.useFixture(fixtures.TempDir())
        config.PAGES_CONTENT_DIR = self.content_dir.path
        
    def test_index_redirect(self):
        
        # no trailing slash should redirect
        rv = self.client.get('/page')
        self.assertEqual(rv.status_code, 301)
        
    def test_content_missing(self):

        rv = self.client.get('/page/')
        self.assertEqual(rv.status_code, 404)
        
        rv = self.client.get('/page/Foo')
        self.assertEqual(rv.status_code, 404)
        
    def test_default_index(self):
        
        with tempfile.NamedTemporaryFile(suffix=config.PAGES_FILE_EXT, dir=self.content_dir.path) as f:
            f.write("Hello!Hello!Hello!")
            f.flush()
        
            config.PAGES_DEFAULT_INDEX = os.path.splitext(os.path.basename(f.name))[0]
            rv = self.client.get('/page/')
            self.assertEqual(rv.status_code, 200)
            self.assertIn("Hello!Hello!Hello!", rv.data)

    def test_default_section_index(self):
        
        section_dir = os.path.join(self.content_dir.path,"foo")
        os.mkdir(section_dir)

        with tempfile.NamedTemporaryFile(suffix=config.PAGES_FILE_EXT, dir=section_dir) as f:
            f.write("Blah!Blah!Blah!")
            f.flush()
        
            config.PAGES_DEFAULT_INDEX = os.path.splitext(os.path.basename(f.name))[0]
            rv = self.client.get('/page/foo/')
            self.assertEqual(rv.status_code, 200)
            self.assertIn("Blah!Blah!Blah!", rv.data)
            
    def test_named_page(self):
        
        with tempfile.NamedTemporaryFile(suffix=config.PAGES_FILE_EXT, dir=self.content_dir.path) as f:
            f.write("Goodbye!Goodbye!Goodbye!")
            f.flush()
        
            page_name = os.path.splitext(os.path.basename(f.name))[0]
            rv = self.client.get('/page/' + page_name)
            self.assertEqual(rv.status_code, 200)
            self.assertIn("Goodbye!Goodbye!Goodbye!", rv.data)
        
    def test_named_section_page(self):
        
        section_dir = os.path.join(self.content_dir.path,"foo")
        os.mkdir(section_dir)

        with tempfile.NamedTemporaryFile(suffix=config.PAGES_FILE_EXT, dir=section_dir) as f:
            f.write("Bluh!Bluh!Bluh!")
            f.flush()
        
            page_name = os.path.splitext(os.path.basename(f.name))[0]
            rv = self.client.get('/page/foo/' + page_name)
            self.assertEqual(rv.status_code, 200)
            self.assertIn("Bluh!Bluh!Bluh!", rv.data)
            
        
        
    
if __name__ == '__main__':
    unittest.main()