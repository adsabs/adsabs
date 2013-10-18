from flask import Blueprint, render_template, request, current_app, session, \
flash, request
import os
import zlib
import hashlib


#I define the blueprint
buggyme_blueprint = Blueprint('buggyme', __name__, template_folder="templates", url_prefix='/buggyme')

def create_hash(msg):
    """This function must return a string"""
    #return hashlib.md5(msg).digest()
    return str(zlib.adler32(unicode(msg)))
    #return unicode(msg)

def dismiss_message(msg, category):
    if 'buggyme_dismiss' not in session:
        session['buggyme_dismiss'] = {}
    session['buggyme_dismiss'][create_hash(msg)] = True
    
def is_message_dismissed(msg, category):
    if 'buggyme_dismiss' in session and create_hash(msg) in session['buggyme_dismiss']:
        return True
    return False 

@buggyme_blueprint.route('/', methods=['GET', 'POST'])
def ajax():
    """
    Entry point of the buggyme messages
    """
    
    # add the dismissed msg to list of prohibited msgs
    msg = request.args.get('msg', None)
    category  = request.args.get('category', None)
    
    if msg is not None:
        dismiss_message(msg, category)
        
    return ""
