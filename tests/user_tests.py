
import os
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) #@UndefinedVariable

import unittest2

from adsabs.app import create_app
from adsabs.modules.user import AdsUser
from adsabs.modules.api.user import create_api_user, PERMISSION_LEVELS
from config import config
from tests.utils import *

class UserTests(AdsabsBaseTestCase):

    def test_ads_user(self):
        
        user = AdsUser.from_id("a_cookie_id")
        self.assertIsNone(user)
        
        self.insert_user("a")
        user = AdsUser.from_id("a_cookie_id")
        self.assertIsNotNone(user)
        self.assertEqual("a_name", user.name)
        
        
class ApiUserTests(AdsabsBaseTestCase):
    
    def test_create_api_user(self):
        self.insert_user("foo", developer=False)
        ads_user = AdsUser.from_id("foo_cookie_id")
        self.assertTrue(ads_user.user_rec.developer_key in [None, ""])
        api_user = create_api_user(ads_user, "basic")
        self.assertTrue(api_user.is_developer())
        self.assertEqual(api_user.user_rec.developer_perms, PERMISSION_LEVELS["basic"])
        dev_key = api_user.get_dev_key()
        api_user2 = AdsApiUser.from_dev_key(dev_key)
        self.assertEqual(api_user.get_dev_key(), api_user2.get_dev_key()) 
        
        
if __name__ == '__main__':
    unittest2.main()