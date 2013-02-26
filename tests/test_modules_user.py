
import os
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

import unittest2
import pytz
from datetime import datetime, timedelta

from adsabs.app import create_app
from adsabs.modules.user import user
from adsabs.modules.api.user import create_api_user, PERMISSION_LEVELS
from config import config
from test_utils import *

class UserTests(AdsabsBaseTestCase):

    def test_ads_user(self):
        
        u = user.AdsUser.from_id("a_cookie_id")
        self.assertIsNone(u)
        
        self.insert_user("a")
        u = user.AdsUser.from_id("a_cookie_id")
        self.assertIsNotNone(u)
        self.assertEqual("a_name", u.name)
    
    def test_classic_signon(self):
        
        self.useFixture(ClassicADSSignonFixture())
        classic_user = user.get_classic_user(None, None)
        self.assertEqual(classic_user['cookie'], 'abc123')
        
        u, authenticated = user.authenticate(None, None)
        self.assertTrue(authenticated)
        self.assertEqual(u.get_username(), 'foo@example.com')
        # check that the new registered datetime is less than a few seconds diff
        now = datetime.utcnow().replace(tzinfo=pytz.utc)
        tdelta = now - u.get_registered()
        self.assertTrue(tdelta.seconds <= 3)
        
    def test_last_signon(self):
        
        fix = ClassicADSSignonFixture()
        self.useFixture(fix)
        u, authenticated = user.authenticate(None, None)
        self.assertIsNone(u.user_rec.last_signon)
        
        # user/password doesn't matter here since we've monkeypatched the auth method
        rv = self.client.post('/user/login', data=dict(login="foo",password="barbaz123",next="blah",remember=1,submit=1))
        u = user.AdsUser.from_id(fix.user_data['cookie'])
        self.assertIsNotNone(u.get_last_signon())
        
        
class ApiUserTests(AdsabsBaseTestCase):
    
    def test_create_api_user(self):
        self.insert_user("bar", developer=False)
        ads_user = user.AdsUser.from_id("bar_cookie_id")
        self.assertTrue(ads_user.user_rec.developer_key in [None, ""])
        api_user = create_api_user(ads_user, "basic")
        self.assertTrue(api_user.is_developer())
        self.assertEqual(api_user.user_rec.developer_perms, PERMISSION_LEVELS["basic"])
        dev_key = api_user.get_dev_key()
        api_user2 = AdsApiUser.from_dev_key(dev_key)
        self.assertEqual(api_user.get_dev_key(), api_user2.get_dev_key()) 
        
        
if __name__ == '__main__':
    unittest2.main()