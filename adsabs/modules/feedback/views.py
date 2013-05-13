'''
Created on May 9, 2013

@author: dimilia
'''
from flask import (Blueprint, request, render_template, flash)
from .forms import FeedbackForm
from flask.ext.mail import Message #@UnresolvedImport
from adsabs.extensions import mail
from config import config

#Definition of the blueprint
feedback_blueprint = Blueprint('feedback', __name__, template_folder="templates", url_prefix='/feedback')

__all__ = ['feedback_blueprint', 'feedback', 'ajax_endpoint']

def send_feedback(form):
    """function that actually sends the email"""
    msg = Message(u"ADSABS2 feedback: %s" % form.feedback_type.data,
                  body=form.feedback_text.data,
                  sender=form.email.data,
                  recipients=config.FEEDBACK_RECIPIENTS)
    mail.send(msg)

@feedback_blueprint.route('/', methods=('GET', 'POST'))
def feedback():
    """HTML interface integrated in the web site"""
    form = FeedbackForm(request.values, csrf_enabled=False)
    if form.is_submitted():
        if form.validate():
            try:
                send_feedback(form)
                return render_template('feedback.html', form=None, status='sent')
            except:
                flash('There has been a technical problem. Please retry.', 'error')
        else:
            for field_name, errors_list in form.errors.iteritems():
                flash('errors in the form validation: %s.' % '; '.join(errors_list), 'error')
    return render_template('feedback.html', form=form, status=None)
        
    
@feedback_blueprint.route('/', methods=('GET', 'POST'))
def ajax_endpoint():
    """AJAX endpoint"""
    pass