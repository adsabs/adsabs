
import os
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #@UndefinedVariable

import unittest2

from adsabs.app import create_app
from adsabs.modules.user import AdsUser
from config import config
from tests.utils import user_creator

class UserTests(unittest2.TestCase):

    def setUp(self):
        config.TESTING = True
        config.MONGOALCHEMY_DATABASE = 'test'
        app = create_app(config)
        
        from adsabs.extensions import mongodb
        mongodb.session.db.connection.drop_database('test') #@UndefinedVariable
        
        self.insert_user = user_creator()
        self.app = app.test_client()
        
    def test_ads_user(self):
        
        user = AdsUser.from_id("a_cookie_id")
        self.assertIsNone(user)
        
        self.insert_user("a")
        user = AdsUser.from_id("a_cookie_id")
        self.assertIsNotNone(user)
        self.assertEqual("a_name", user.name)
        
 
        
        
if __name__ == '__main__':
    unittest2.main()