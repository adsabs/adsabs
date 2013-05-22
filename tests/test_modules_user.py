
import os
import site
tests_dir = os.path.dirname(os.path.abspath(__file__))
site.addsitedir(os.path.dirname(tests_dir)) #@UndefinedVariable
site.addsitedir(tests_dir) #@UndefinedVariable

import unittest2
import uuid
import pytz
from datetime import datetime#, timedelta
from urlparse import urlparse
from urllib import quote_plus
from flask import g
from werkzeug.datastructures import Headers

#from adsabs.app import create_app
from adsabs.modules.user import user
from adsabs.modules.api.user import create_api_user, PERMISSION_LEVELS
from config import config
from test_utils import (AdsabsBaseTestCase, ClassicADSSignonFixture, AdsApiUser)

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
        rv = self.client.post('/user/login', data=dict(login="foo@example.com",password="barbaz123",next="blah",remember=1,submit=1))
        u = user.AdsUser.from_id(fix.user_data['cookie'])
        self.assertIsNotNone(u.get_last_signon())
        
    def test_anonymous_user_cookie_1(self):
        """fist time request: test if the cookie is set properly in the application"""
        with self.app.test_request_context('/'):
            self.app.preprocess_request()
            user_cookie_id = getattr(g, 'user_cookie_id', None)
            self.assertIsNotNone(user_cookie_id)
            self.assertIsInstance(user_cookie_id, unicode)
            try:
                uuid.UUID(user_cookie_id)
            except ValueError:
                self.fail('Anonymous user cookie id is not a valid UUID value')
                
    def test_anonymous_user_cookie_2(self):
        """fist time request: test if two set-cookie headers are sent back"""
        rv = self.client.get('/')
        self.assertTrue(rv.headers.has_key('Set-Cookie'))
        adsabs2_cookies = 0
        ads_cookies = 0
        for elem in rv.headers.get_all('Set-Cookie'):
            if elem.startswith(config.COOKIE_ADSABS2_NAME):
                adsabs2_cookies +=1
            elif elem.startswith(config.COOKIE_ADS_CLASSIC_NAME):
                ads_cookies += 1
        self.assertEqual(adsabs2_cookies, 2)
        self.assertEqual(ads_cookies, 0)
                    
    def test_anonymous_user_cookie_3(self):
        """following requests: test that in the application  the cookie is set properly"""
        
        cookie_value = 'c910a0dc-c75b-4f2e-b811-38c45192d93f'
        headers = Headers({'Cookie':'NASA_ADSABS2_ID=%s;' % cookie_value})
        with self.app.test_request_context('/', headers=headers):
            self.app.preprocess_request()
            user_cookie_id = getattr(g, 'user_cookie_id', None)
            self.assertIsNotNone(user_cookie_id)
            self.assertIsInstance(user_cookie_id, unicode)
            try:
                uuid.UUID(user_cookie_id)
            except ValueError:
                self.fail('Anonymous user cookie id is not a valid UUID value')
            self.assertEqual(user_cookie_id, cookie_value)
            
    def test_anonymous_user_cookie_4(self):
        """following requests: test that there are no set-cookie if the request already contains cookies"""
        cookie_value = 'c910a0dc-c75b-4f2e-b811-38c45192d93f'
        headers = Headers({'Cookie':'NASA_ADSABS2_ID=%s;' % cookie_value})
        rv = self.client.get('/', headers=headers)
        adsabs2_cookies = 0
        ads_cookies = 0
        for elem in rv.headers.get_all('Set-Cookie'):
            if elem.startswith(config.COOKIE_ADSABS2_NAME):
                adsabs2_cookies +=1
            elif elem.startswith(config.COOKIE_ADS_CLASSIC_NAME):
                ads_cookies += 1
        self.assertEqual(adsabs2_cookies, 0)
        self.assertEqual(ads_cookies, 0)
        
    def test_anonymous_user_cookie_5(self):
        """sending a wrong anonymous cookie: 2 set cookie expected"""
        cookie_value = 'wrong_cookie'
        headers = Headers({'Cookie':'NASA_ADSABS2_ID=%s;' % cookie_value})
        rv = self.client.get('/', headers=headers)
        adsabs2_cookies = 0
        ads_cookies = 0
        for elem in rv.headers.get_all('Set-Cookie'):
            if elem.startswith(config.COOKIE_ADSABS2_NAME):
                adsabs2_cookies +=1
            elif elem.startswith(config.COOKIE_ADS_CLASSIC_NAME):
                ads_cookies += 1
        self.assertEqual(adsabs2_cookies, 2)
        self.assertEqual(ads_cookies, 0)
        
    def test_user_cookie_at_login_1(self):
        """ test that when the user logs in, 4 set-cookie headers are sent back"""
        fix = ClassicADSSignonFixture()
        self.useFixture(fix)
        rv = self.client.post('/user/login', data=dict(login="foo@example.com",password="barbaz123",next="blah",remember=1,submit=1))
        #there are some cookies
        self.assertTrue(rv.headers.has_key('Set-Cookie'))
        #count that there are 2 ADS2 and 2 ads classic cookies
        adsabs2_cookies = 0
        ads_cookies = 0
        for elem in rv.headers.get_all('Set-Cookie'):
            if elem.startswith(config.COOKIE_ADSABS2_NAME):
                adsabs2_cookies +=1
            elif elem.startswith(config.COOKIE_ADS_CLASSIC_NAME):
                ads_cookies += 1
        self.assertEqual(adsabs2_cookies, 2)
        self.assertEqual(ads_cookies, 2)
    
    def test_user_cookie_at_login_2(self):
        """ test that when the user logs in, 4 set-cookie headers are sent back 
        even if there are some anonymous cookies sent together with the request (the cookies must get updated)"""
        fix = ClassicADSSignonFixture()
        self.useFixture(fix)
        cookie_value = 'c910a0dc-c75b-4f2e-b811-38c45192d93f'
        headers = Headers({'Cookie':'NASA_ADSABS2_ID=%s;' % cookie_value})
        rv = self.client.post('/user/login', data=dict(login="foo@example.com",password="barbaz123",next="blah",remember=1,submit=1), headers=headers)
        #there are some cookies
        self.assertTrue(rv.headers.has_key('Set-Cookie'))
        #count that there are 2 ADS2 and 2 ads classic cookies
        adsabs2_cookies = 0
        ads_cookies = 0
        for elem in rv.headers.get_all('Set-Cookie'):
            if elem.startswith(config.COOKIE_ADSABS2_NAME):
                adsabs2_cookies +=1
            elif elem.startswith(config.COOKIE_ADS_CLASSIC_NAME):
                ads_cookies += 1
        self.assertEqual(adsabs2_cookies, 2)
        self.assertEqual(ads_cookies, 2)
     
    def test_user_logged_in_cookie_1(self):
        """test that if the user is logged in and the cookies are not right, some new cookies are sent back"""
        fix = ClassicADSSignonFixture()
        self.useFixture(fix)
        #first the user logs in
        rv = self.client.post('/user/login', data=dict(login="foo@example.com",password="barbaz123",next="blah",remember=1,submit=1))
        #request with wrong cookies
        self.client.set_cookie('localhost', 'NASA_ADSABS2_ID', 'wrong_cookie')
        self.client.set_cookie('localhost', 'NASA_ADS_ID', 'wrong_cookie')
        rv = self.client.get('/')
        #count that there are 2 ADS2 and 2 ads classic cookies
        adsabs2_cookies = 0
        ads_cookies = 0
        for elem in rv.headers.get_all('Set-Cookie'):
            if elem.startswith(config.COOKIE_ADSABS2_NAME):
                adsabs2_cookies +=1
            elif elem.startswith(config.COOKIE_ADS_CLASSIC_NAME):
                ads_cookies += 1
        self.assertEqual(adsabs2_cookies, 2)
        self.assertEqual(ads_cookies, 2)
    
    def test_user_logged_in_cookie_2(self):
        """test that if the user is logged in and the cookies are right, not set cookies are sent back"""
        fix = ClassicADSSignonFixture()
        self.useFixture(fix)
        #first the user logs in
        rv = self.client.post('/user/login', data=dict(login="foo@example.com",password="barbaz123",next="blah",remember=1,submit=1))
        #set cookies for the next request
        self.client.set_cookie('localhost', 'NASA_ADSABS2_ID', 'abc123')
        self.client.set_cookie('localhost', 'NASA_ADS_ID', 'abc123')
        #request with right cookies
        rv = self.client.get('/')
        #count that there are 0 ADS2 and 0 ads classic cookies
        adsabs2_cookies = 0
        ads_cookies = 0
        for elem in rv.headers.get_all('Set-Cookie'):
            if elem.startswith(config.COOKIE_ADSABS2_NAME):
                adsabs2_cookies +=1
            elif elem.startswith(config.COOKIE_ADS_CLASSIC_NAME):
                ads_cookies += 1
        self.assertEqual(adsabs2_cookies, 0)
        self.assertEqual(ads_cookies, 0)
        
    def test_user_cookie_at_logout_1(self):
        """test that at the logout the cookies are invalidated"""
        fix = ClassicADSSignonFixture()
        self.useFixture(fix)
        #first the user logs in
        rv = self.client.post('/user/login', data=dict(login="foo@example.com",password="barbaz123",next="blah",remember=1,submit=1))
        #set cookies for the next request
        self.client.set_cookie('localhost', 'NASA_ADSABS2_ID', 'abc123')
        self.client.set_cookie('localhost', 'NASA_ADS_ID', 'abc123')
        rv = self.client.get('/user/logout')
        #count that there are 2 ADS2 and 2 ads classic cookies invalidations
        adsabs2_cookies = 0
        ads_cookies = 0
        for elem in rv.headers.get_all('Set-Cookie'):
            if elem.startswith(config.COOKIE_ADSABS2_NAME +'=;'):
                adsabs2_cookies +=1
            elif elem.startswith(config.COOKIE_ADS_CLASSIC_NAME +'=;'):
                ads_cookies += 1
        self.assertEqual(adsabs2_cookies, 2)
        self.assertEqual(ads_cookies, 2)
    
    def test_redirect_after_login_1(self):
        """Tests that the redirect after the login works properly"""
        fix = ClassicADSSignonFixture()
        self.useFixture(fix)
        next_path = "/search"
        rv = self.client.post('/user/login', data=dict(login="foo@example.com",password="barbaz123",next=next_path,remember=1,submit=1))
        self.assertEqual(rv.status_code, 302)
        self.assertNotEqual(rv.headers.get('Location'), None)
        self.assertEqual(urlparse(rv.headers.get('Location')).path, next_path)
        
    def test_redirect_after_login_2(self):
        """Tests that the redirect after the login works properly even with a query string"""
        fix = ClassicADSSignonFixture()
        self.useFixture(fix)
        next_path = "/search?param=foo&param2=bar+bar&nil=nal"
        rv = self.client.post('/user/login', data=dict(login="foo@example.com",password="barbaz123",next=next_path,remember=1,submit=1))
        self.assertEqual(rv.status_code, 302)
        self.assertNotEqual(rv.headers.get('Location'), None)
        parsed_location_header = urlparse(rv.headers.get('Location'))
        self.assertEqual('%s?%s' % (parsed_location_header.path, parsed_location_header.query), next_path)
        
    def test_redirect_after_logout_1(self):
        """Tests that the redirect after the logout works properly"""
        fix = ClassicADSSignonFixture()
        self.useFixture(fix)
        #first the user logs in
        rv = self.client.post('/user/login', data=dict(login="foo@example.com",password="barbaz123",next='foo',remember=1,submit=1))
        #then he logs out
        next_path = "/search"
        rv = self.client.get('/user/logout?next=%s' % quote_plus(next_path))
        self.assertEqual(rv.status_code, 302)
        self.assertNotEqual(rv.headers.get('Location'), None)
        self.assertEqual(urlparse(rv.headers.get('Location')).path, next_path)
        
    def test_redirect_after_logout_2(self):
        """Tests that the redirect after the logout works properly even with a query string"""
        fix = ClassicADSSignonFixture()
        self.useFixture(fix)
        #first the user logs in
        rv = self.client.post('/user/login', data=dict(login="foo@example.com",password="barbaz123",next='foo',remember=1,submit=1))
        #then he logs out
        next_path = "/search?param=foo&param2=bar+bar&nil=nal"
        rv = self.client.get('/user/logout?next=%s' % quote_plus(next_path))
        self.assertEqual(rv.status_code, 302)
        self.assertNotEqual(rv.headers.get('Location'), None)
        parsed_location_header = urlparse(rv.headers.get('Location'))
        self.assertEqual('%s?%s' % (parsed_location_header.path, parsed_location_header.query), next_path)
        
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