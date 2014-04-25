'''
Created on May 9, 2013

@author: dimilia
'''
from flask import Blueprint, request, render_template, flash, g
from urllib import unquote_plus
from .forms import FeedbackForm
from flask.ext.mail import Message #@UnresolvedImport
from flask.ext.login import current_user #@UnresolvedImport
from adsabs.extensions import mail, statsd
from config import config
import simplejson as json
from types import *

#Definition of the blueprint
feedback_blueprint = Blueprint('feedback', __name__, template_folder="templates", url_prefix='/feedback')

__all__ = ['feedback_blueprint', 'feedback']

ALLOWED_ENVIRON_TYPES = [BooleanType, IntType, LongType, FloatType, StringType, UnicodeType, TupleType, ListType, DictType]

class EnvironEncoder(json.JSONEncoder):
    """simple custom encoder to allow json-serialization of the wsgi environment vars"""
    def default(self, obj):
        if type(obj) not in ALLOWED_ENVIRON_TYPES:
            return repr(obj)
        return json.JSONEncoder.default(self, obj)

def send_feedback(form):
    """function that actually sends the email"""
    
    anonymous = current_user is None or current_user.is_anonymous()
    user_id = "%s%s" % (getattr(g, 'user_cookie_id'), anonymous and " (anonymous)" or "")

    template_ctx = {
        'page_url': unquote_plus(form.page_url.data),
        'user_id': user_id,
        'feedback': form.feedback_text.data,
        # do a json round-trip to get pretty indenting
        'environ': json.dumps(json.loads(form.environ.data), indent=True),
        }
    message_body = render_template('message_body.txt', **template_ctx)
    msg = Message(u"ADSABS2 feedback from %s <%s>: %s" % (form.name.data, form.email.data, form.feedback_type.data),
                  body=message_body,
                  sender=form.email.data,
                  recipients=config.FEEDBACK_RECIPIENTS)

    mail.send(msg)
    statsd.incr("feedback.email.sent")

@feedback_blueprint.route('/', methods=('GET', 'POST'))
def feedback():
    """HTML interface integrated in the web site"""
    form = FeedbackForm(request.values, csrf_enabled=False)

    # request is coming from feedback widget == 'nolayout', otherwise empty
    feedb_req_mode = request.values.get('feedb_req_mode')

    if form.validate_on_submit():
        try:
            send_feedback(form)
            return render_template('feedback.html', form=None, status='sent', feedb_req_mode=feedb_req_mode)
        except Exception, e:
            flash('There has been a technical problem. Please retry.', 'error')

    template_ctx = {
        'page_url': request.values.get('page_url',''),
        'form': form,
        'environ': json.dumps(request.environ, cls=EnvironEncoder),
        'status': None,
        'feedb_req_mode': feedb_req_mode,
    }
    return render_template('feedback.html', **template_ctx)
