'''
Created on May 9, 2013

@author: dimilia
'''
from flask import (Blueprint, request, render_template, flash)
from urllib import unquote_plus
from .forms import FeedbackForm
from flask.ext.mail import Message #@UnresolvedImport
from adsabs.extensions import mail
from config import config

#Definition of the blueprint
feedback_blueprint = Blueprint('feedback', __name__, template_folder="templates", url_prefix='/feedback')

__all__ = ['feedback_blueprint', 'feedback']

def send_feedback(form):
    """function that actually sends the email"""
    try:
        url_from = unquote_plus(form.page_url_hidden.data)
    except:
        url_from = ''
    message_body = "Sent from url: %s \n\nMessage:\n%s" % (url_from, form.feedback_text.data)
    msg = Message(u"ADSABS2 feedback from %s: %s" % (form.email.data, form.feedback_type.data),
                  body=message_body,
                  sender=form.email.data,
                  recipients=config.FEEDBACK_RECIPIENTS)
    mail.send(msg)

@feedback_blueprint.route('/', methods=('GET', 'POST'))
def feedback():
    """HTML interface integrated in the web site"""
    form = FeedbackForm(request.values, csrf_enabled=False)
    feedb_req_mode = request.values.get('feedb_req_mode')
    if form.validate_on_submit():
        try:
            send_feedback(form)
            return render_template('feedback.html', form=None, status='sent', feedb_req_mode=feedb_req_mode)
        except:
            flash('There has been a technical problem. Please retry.', 'error')
    return render_template('feedback.html', form=form, status=None, feedb_req_mode=feedb_req_mode)
