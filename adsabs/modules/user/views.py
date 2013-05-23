#from datetime import datetime
from flask import (Blueprint, request, flash, redirect, 
                   url_for, render_template, g, current_app as app)
from flask.ext.login import (login_required, login_user,                    #@UnresolvedImport
                current_user, logout_user, )                                 #@UnresolvedImport
#                confirm_login, fresh_login_required, login_fresh)           #@UnresolvedImport
from time import time
from .forms import (SignupForm, LoginForm, RecoverPasswordForm, 
                   ChangePasswordForm, ReauthForm)
from adsabs.core.after_request_funcs import after_this_request
from config import config
from .user import authenticate

# For import *
__all__ = ['user_blueprint', 'index', 'login', 'reauth', 'logout', 'signup', 'change_password',]

#definition of the blueprint for the user part
user_blueprint = Blueprint('user', __name__, template_folder="templates", 
                           static_folder="static", url_prefix='/user')

def invalidate_user_cookie():
    @after_this_request
    def delete_username_cookie(response):
        #set the ads cookie to expire
        for cookie_name, cookie_conf in config.COOKIES_CONF.items():
            for domain in cookie_conf['domain']:
                response.delete_cookie(cookie_name, domain=domain)
                #response.set_cookie(cookie_name, '', expires=0, domain=domain)
        return response

@user_blueprint.route('/', methods=['GET'])
def index():
    """
    Index page of the User
    """
    app.logger.debug('Index of user page.')
    if current_user.is_authenticated():
        app.logger.debug('User already authenticated')
        return render_template('user_home_page.html')
    
    app.logger.debug('User not authenticated: redirect to authentication page.')
    return redirect(url_for('user.login'))

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login view
    """
    app.logger.debug('Login form')
    form = LoginForm(login=request.args.get('login', None), next=request.args.get('next', None))

    if form.validate_on_submit():
        app.logger.debug('Authentication process')
        user, authenticated = authenticate(form.login.data, form.password.data)
        if user and authenticated:
            user.set_last_signon()
            remember = request.form.get('remember') == 'y'
            if login_user(user, remember=remember):
                flash("Successfully logged in!", 'success')
            #build redirect url
            base_redirect_url = form.next.data or url_for('user.index')
            if base_redirect_url.find('?') == -1:
                return redirect("%s?refresh=%s" % (base_redirect_url, time()))
            else:
                return redirect("%s&refresh=%s" % (base_redirect_url, time()))
        else:
            flash('Sorry, invalid login parameters', 'error')

    return render_template('login.html', form=form)

@user_blueprint.route('/reauth', methods=['GET', 'POST'])
@login_required
def reauth():
    """
    """
    invalidate_user_cookie()
    return 'reauth'

@user_blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    """
    User logout view
    """
    app.logger.debug('User logout')
    form = LoginForm(login=request.args.get('login', None), next=request.args.get('next', None))
    #actual logout
    logout_user()
    #set a variable in g to skip the general after_request cookie set up
    g.skip_general_cookie_setup = True
    #call of the function that runs a specific after_request to invalidate the user cookies
    invalidate_user_cookie()
    flash('You are now logged out', 'success')
    #build redirect url
    base_redirect_url = form.next.data or url_for('user.index')
    if base_redirect_url.find('?') == -1:
        return redirect("%s?refresh=%s" % (base_redirect_url, time()))
    else:
        return redirect("%s&refresh=%s" % (base_redirect_url, time()))

@user_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    """
    return 'signup'

@user_blueprint.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """
    """
    return 'change password'
