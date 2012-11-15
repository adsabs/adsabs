
import os
import site
site.addsitedir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest

from adsabs.app import create_app
from adsabs.modules.user import AdsUser
from config import config

class UserTests(unittest.TestCase):

    def setUp(self):
        config.TESTING = True
        config.MONGOALCHEMY_DATABASE = 'test'
        app = create_app(config)
        
        # insert fake api user
        from adsabs.extensions import mongodb
        mongodb.session.db.connection.drop_database('test')
        self.users = mongodb.session.db.ads_users
        
        self.app = app.test_client()
        
    def insert_user(self, username, developer=False, perms={}):
        self.users.insert({
            "username": username + "_name",
            "myads_id": username + "_myads_id",
            "developer_key": + "_dev_key",
            "cookie_id": username + "_cookie_id",
            "developer": developer,
            "developer_perm_data" : perms
        })

    def test_ads_user(self):
        
        user = AdsUser.from_id("a")
        self.assertIsNone(user)
        
        self.insert_user("a")
        user = AdsUser.from_id("a")
        self.assertIsNotNone(user)
        
        user = AdsUser.from_dev_key("b")
        self.assertIsNone(user)
        
        self.insert_user("foo")
        
if __name__ == '__main__':
    unittest.main()