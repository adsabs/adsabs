'''
Created on May 9, 2013

@author: dimilia
'''

from flask.ext.wtf import (Form, RecaptchaField)      
from wtforms import (TextField, RadioField, TextAreaField, HiddenField, #SelectField, IntegerField, BooleanField,  , SubmitField, HiddenField,  
                          validators)   
from wtforms.validators import (required, length) #optional, ValidationError, equal_to, email 
from flask.ext.wtf.html5 import EmailField 
from config import config

__all__ = ['FeedbackForm',]

class FeedbackForm(Form):
    """The form that will be used to submit feedbacks"""
    name = TextField(u'Name', [required(), length(min=1, max=2048)], description=u"Your name")
    email = EmailField(u'Email address', [required(), length(min=1, max=2048), validators.Email()], description=u"Your Email Address")
    feedback_type = RadioField(u'Feedback type', [required()], choices=[('comment', 'Comment'), ('bug', 'Bug')], description=u"Feedback type", default="comment")
    feedback_text = TextAreaField(u'Message', [validators.DataRequired(message="The message cannot be empty.")], description=u"Message")
    page_url = HiddenField(u'page_url', [required()], description=u"URL of the page")
    environ = HiddenField(u'environ', [required()], description=u"Captured wsgi environment variables")
    
if config.RECAPTCHA_ENABLED:
    setattr(FeedbackForm, "recaptcha", RecaptchaField())
    