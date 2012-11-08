from flask import (Blueprint, request, flash, redirect, 
                   url_for, render_template)
from flask.ext.login import (login_required, login_user,    #@UnresolvedImport
                current_user, logout_user, confirm_login,   #@UnresolvedImport
                fresh_login_required, login_fresh)          #@UnresolvedImport
from forms import (SignupForm, LoginForm, RecoverPasswordForm, 
                   ChangePasswordForm, ReauthForm)
from .user import authenticate

import logging

# For import *
__all__ = ['user_blueprint', 'index', 'login', 'reauth', 'logout', 'signup', 'change_password',]

#definition of the blueprint for the user part
user_blueprint = Blueprint('user', __name__, template_folder="templates", static_folder="static")

log = logging.getLogger(__name__)

@user_blueprint.route('/', methods=['GET'])
def index():
    """
    Index page of the User
    """
    log.debug('Index of user page.')
    if current_user.is_authenticated():
        log.debug('User already authenticated')
        return render_template('user_home_page.html')
    
    log.debug('User not authenticated: redirect to authentication page.')
    return redirect(url_for('user.login'))

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    """
    log.debug('Login form')
    form = LoginForm(login=request.args.get('login', None), next=request.args.get('next', None))

    if form.validate_on_submit():
        user, authenticated = authenticate(form.login.data, form.password.data)

        if user and authenticated:
            remember = request.form.get('remember') == 'y'
            if login_user(user, remember=remember):
                flash("Successfully logged in!", 'success')
            return redirect(form.next.data or url_for('user.index'))
        else:
            flash('Sorry, invalid login parameters', 'error')

    return render_template('login.html', form=form)

@user_blueprint.route('/reauth', methods=['GET', 'POST'])
@login_required
def reauth():
    """
    """
    return 'reauth'

@user_blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('You are now logged out', 'success')
    return redirect(url_for('index.index'))

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