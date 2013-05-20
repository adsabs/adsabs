'''
Created on May 9, 2013

@author: dimilia
'''

from flask.ext.wtf import (Form, TextField, RadioField, TextAreaField, RecaptchaField, HiddenField, #SelectField, IntegerField, BooleanField,  , SubmitField, HiddenField,  #@UnresolvedImport
                          validators, required, #optional, ValidationError, equal_to, email #@UnresolvedImport
                          length) #@UnresolvedImport

from flask.ext.wtf.html5 import EmailField #@UnresolvedImport

__all__ = ['FeedbackForm',]

class FeedbackForm(Form):
    """The form that will be used to submit feedbacks"""
    name = TextField(u'name', [required(), length(min=1, max=2048)], description=u"Your name")
    email = EmailField(u'email', [required(), length(min=1, max=2048), validators.Email()], description=u"Your Email Address")
    feedback_type = RadioField(u'feedback_type', [required()], choices=[('comment', 'Comment'), ('bug', 'Bug')], description=u"Feedback type", default="comment")
    feedback_text = TextAreaField(u'message', [validators.DataRequired(message="The message cannot be empty.")], description=u"Message")
    page_url_hidden = HiddenField(u'page_url', [required()], description=u"URL of the page")
    recaptcha = RecaptchaField()
    