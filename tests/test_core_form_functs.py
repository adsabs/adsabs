'''
Created on May 13, 2013

@author: dimilia
'''
import unittest2
from flask import request
from flask.ext.wtf import (Form, TextField, RadioField,     #@UnresolvedImport
                           TextAreaField, required, length, validators) #@UnresolvedImport
from flask.ext.wtf.html5 import EmailField #@UnresolvedImport
from test_utils import AdsabsBaseTestCase


import adsabs.core.form_functs as ff

class MyTestForm(Form):
    """A form """
    name = TextField(u'name', [required(), length(min=1, max=2048)], description=u"Your name")
    email = EmailField(u'email', [required(), length(min=1, max=2048), validators.Email()], description=u"Your Email Address")
    feedback_type = RadioField(u'feedback_type', [required()], choices=[('comment', 'Comment'), ('bug', 'Bug')], description=u"Feedback type", default="comment")
    feedback_text = TextAreaField(u'message', [validators.DataRequired(message="The message cannot be empty.")], description=u"Message")

class FomFunctions(AdsabsBaseTestCase):
    
    def test_is_submitted_cust_1(self):
        """tests if a form is submitted in case of GET request"""
        with self.app.test_request_context('/feedback/?name=Johnny+Miller&email=johnny@miller.com&feedback_type=bug&feedback_text=foobar'):
            form = MyTestForm(request.values)
            self.assertFalse(form.is_submitted())
            self.assertTrue(ff.is_submitted_cust(form))
        
    def test_is_submitted_cust_2(self):
        """tests if a form is submitted in case of POST request"""        
        with self.app.test_request_context('/feedback/', method='POST', data=dict(name="Johnny Miller",email="johnny@miller.com",
                                                                                  feedback_type="bug",feedback_text='foobar')):
            form = MyTestForm(request.values)
            self.assertTrue(form.is_submitted())
            self.assertTrue(ff.is_submitted_cust(form))

if __name__ == '__main__':
    unittest2.main()