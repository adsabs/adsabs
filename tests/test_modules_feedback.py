'''
Created on May 14, 2013

@author: dimilia
'''
import sys
if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest
    
from test_utils import (AdsabsBaseTestCase, ClassicADSSignonFixture)
from bs4 import BeautifulSoup

class FeedbackTests(AdsabsBaseTestCase):
    
    def test_basic_feedback_page_1(self):
        """Tests that a request to the base url gives the form"""
        rv = self.client.get('/feedback/')
        soup = BeautifulSoup(rv.data)
        #there is only one input name and the value is empty
        tag = soup.find_all('input', id='name')
        self.assertEqual(len(tag), 1)
        self.assertEqual(tag[0]['value'], '')
        #there is only one input email and the value is empty
        tag = soup.find_all('input', id='email')
        self.assertEqual(len(tag), 1)
        self.assertEqual(tag[0]['value'], '')
        #there is only one input email and the value is empty
        tag = soup.find_all('textarea', id='feedback_text')
        self.assertEqual(len(tag), 1)
        #there are two input radio
        tag = soup.find_all('input', type='radio')
        self.assertEqual(len(tag), 2)
        #the checked input radio is the one with value comment
        tag = soup.find_all('input', type='radio', value='comment')
        self.assertEqual(len(tag), 1)
        self.assertIn(tag[0]['checked'], ['', 'checked'])
        #the other radio doesn't have the checked attribute
        tag = soup.find_all('input', type='radio', value='bug')
        self.assertEqual(len(tag), 1)
        self.assertEqual(tag[0].get('checked'), None)
        
    def test_basic_feedback_page_2(self):
        """Tests that a request to the base url from a logged in user gives the form pre filled"""
        fix = ClassicADSSignonFixture()
        self.useFixture(fix)
        #first the user logs in
        rv = self.client.post('/user/login', data=dict(login="foo@example.com",password="barbaz123",next="blah",remember=1,submit=1))
        #then the user goes to the feedback page
        rv = self.client.get('/feedback/')
        soup = BeautifulSoup(rv.data)
        #there is only one input name and the value is empty
        tag = soup.find_all('input', id='name')
        self.assertEqual(len(tag), 1)
        self.assertEqual(tag[0]['value'], 'Foo Bar')
        #there is only one input email and the value is empty
        tag = soup.find_all('input', id='email')
        self.assertEqual(len(tag), 1)
        self.assertEqual(tag[0]['value'], 'foo@example.com')
        #there is only one input email and the value is empty
        tag = soup.find_all('textarea', id='feedback_text')
        self.assertEqual(len(tag), 1)
        #there are two input radio
        tag = soup.find_all('input', type='radio')
        self.assertEqual(len(tag), 2)
        #the checked input radio is the one with value comment
        tag = soup.find_all('input', type='radio', value='comment')
        self.assertEqual(len(tag), 1)
        self.assertIn(tag[0]['checked'], ['', 'checked'])
        #the other radio doesn't have the checked attribute
        tag = soup.find_all('input', type='radio', value='bug')
        self.assertEqual(len(tag), 1)
        self.assertRaises(tag[0].get('checked'), None)
        
    def test_submit_feedback_1(self):
        """tests that a form submitted with all the necessary data """
        rv = self.client.post('/feedback/', data=dict(name='Foo Bar', email='foo@example.com', feedback_text='bla bla bla', 
                                                      feedback_type='comment', page_url_hidden='/feedback/', recaptcha_challenge_field='test',
                                                      recaptcha_response_field='test'))
        soup = BeautifulSoup(rv.data)
        #there is only a success message a not form
        tag = soup.find_all('div', class_='feedback_success')
        self.assertEqual(len(tag), 1)
        tag = soup.find_all('form')
        self.assertEqual(len(tag), 0)
        tag = soup.find_all('input')
        self.assertEqual(len(tag), 0)
        tag = soup.find_all('textarea')
        self.assertEqual(len(tag), 0)
        
    def test_submit_feedback_2(self):
        """tests that a form submitted with not all the necessary data """
        rv = self.client.post('/feedback/', data=dict(name='Foo Bar', email='foo@example.com', feedback_text='', 
                                                      feedback_type='comment', page_url_hidden='/feedback/', recaptcha_challenge_field='test',
                                                      recaptcha_response_field='test'))
        soup = BeautifulSoup(rv.data)
        #there is only a success message a not form
        tag = soup.find_all('div', class_='feedback_success')
        self.assertEqual(len(tag), 0)
        tag = soup.find_all('form')
        self.assertGreater(len(tag), 0)
        tag = soup.find_all('input')
        self.assertGreater(len(tag), 0)
        tag = soup.find_all('textarea')
        self.assertGreater(len(tag), 0)
        
if __name__ == '__main__':
    unittest.main()