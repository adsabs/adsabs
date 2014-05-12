#from datetime import datetime
from flask import (Blueprint, request, flash, redirect, 
                   url_for, render_template, g, session, current_app as app)
from flask.ext.login import (login_required, login_user,                    
                current_user, logout_user,                                  
                confirm_login, fresh_login_required, login_fresh)           
from time import time
from .forms import (SignupForm, LoginForm, ResetPasswordForm, 
                   ChangePasswordForm, ReauthForm, ActivateUserForm,
                   PreActivateUserForm, ChangeUserParamsForm, ActivateNewUsernameForm, 
                   ResetPasswordFormConf)
from adsabs.core.after_request_funcs import after_this_request
from config import config
from .user import *
from adsabs.core.form_functs import is_submitted_cust
from adsabs.extensions import statsd

# For import *
__all__ = ['user_blueprint', 'index', 'login', 'reauth', 'logout', 'signup', 'activate', 
           'change_password', 'change_account_settings', 'reset_password',  'resend_activation_code_email']

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
    
def generate_redirect_url(next_=None, default_next=None):
    """
    function that generates a url where to redirect the user
    """
    #build redirect url
    base_redirect_url = next_ or default_next or url_for('user.index')
    if base_redirect_url.find('?') == -1:
        return "%s?refresh=%s" % (base_redirect_url, time())
    else:
        return "%s&refresh=%s" % (base_redirect_url, time())

@user_blueprint.route('/', methods=['GET'])
def index():
    """
    Index page of the User
    """
    app.logger.debug('Index of user page.')
    if current_user.is_authenticated():
        app.logger.debug('User already authenticated')
        statsd.incr("user.profile.viewed")
        return render_template('user_home_page.html')
    
    app.logger.debug('User not authenticated: redirect to authentication page.')
    return redirect(url_for('user.login'))

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login view
    """
    app.logger.debug('Login form')
    if current_user.is_authenticated():
        return redirect(request.args.get('next', None) or url_for('user.index'))
    
    form = LoginForm(login=request.args.get('login', None), next=request.args.get('next', None), csrf_enabled=config.CSRF_ENABLED)
    if form.validate_on_submit():
        statsd.incr("user.login.attempt")
        app.logger.debug('Authentication process')
        user, auth_msg = authenticate(form.login.data, form.password.data)
        if user and auth_msg == 'SUCCESS':
            user.set_last_signon()
            remember = request.form.get('remember') == 'y'
            if login_user(user, remember=remember):
                flash("Successfully logged in!", 'success')
            statsd.incr("user.login.success")
            return redirect(generate_redirect_url(next_=form.next.data))
        elif not user and auth_msg == 'WRONG_PARAMS':
            flash('Sorry, invalid login parameters', 'error')
            statsd.incr("user.login.failed")
        elif not user and auth_msg == 'LOCAL_NOT_ACTIVE':
            flash('Sorry, the user is not active yet. Please activate it before proceeding.', 'error')
            session['user_login_email'] = form.login.data
            statsd.incr("user.login.failed")
            return redirect(url_for('user.activate'))
        else:
            flash('Sorry, authentication error. Please try later.', 'error')
            statsd.incr("user.login.failed")

    return render_template('login.html', form=form)

@user_blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    """
    User logout view
    """
    app.logger.debug('User logout')
    #actual logout
    logout_user()
    #set a variable in g to skip the general after_request cookie set up
    g.skip_general_cookie_setup = True
    #call of the function that runs a specific after_request to invalidate the user cookies
    invalidate_user_cookie()
    flash('You are now logged out', 'success')
    statsd.incr("user.logout.success")
    return redirect(generate_redirect_url(next_=request.args.get('next', None)))


@user_blueprint.route('/reauth', methods=['GET', 'POST'])
@login_required
def reauth():
    """
    User re authentication view
    """
    app.logger.debug('User reauth')
    
    form = ReauthForm(next=request.args.get('next', None))
    #if the login is fresh there is no need to re-authenticate
    if login_fresh():
        return redirect(generate_redirect_url(next_=form.next.data))
    
    if form.validate_on_submit():
        user, authenticated = authenticate(current_user.get_username(), form.password.data)
        if user and authenticated:
            user.set_last_signon()
            confirm_login()
            return redirect(generate_redirect_url(next_=form.next.data))
        else:
            flash('Sorry, invalid login parameters', 'error')

    return render_template('reauth.html', form=form)

@user_blueprint.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    User password change
    """
    app.logger.debug('User password change')
    form = ChangePasswordForm()
    if form.validate_on_submit():
        success, message, message_type = change_user_password(form)
        flash(message, message_type)
        if success:
            statsd.incr("user.password.changed.success")
            return redirect(generate_redirect_url(next_=url_for('user.index')))
        else:
            statsd.incr("user.password.changed.failed")
    
    return render_template('change_password.html', form=form)


@user_blueprint.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """
    User password reset
    """
    app.logger.debug('User password reset')
    form = ResetPasswordForm()
    if form.validate_on_submit():
        success, message, message_type = reset_user_password_step_one(form)
        flash(message, message_type)
        if success:
            statsd.incr("user.password.reset.success")
            return redirect(generate_redirect_url(next_=url_for('user.confirm_reset_password')))
        else:
            statsd.incr("user.password.reset.failed")
    return render_template('reset_password_1.html', form=form)
    
@user_blueprint.route('/confirm_reset_password', methods=['GET', 'POST'])
def confirm_reset_password():
    """
    User password reset confirmation
    """
    app.logger.debug('User password reset confirmation')
    #if everything looks fine, it's time to proceed
    form_params_creation ={'csrf_enabled':False}
    if request.method == 'GET':
        if request.values.get('login'):
            form_params_creation.update({'login': request.values.get('login')})
        if request.values.get('resetcode'):
            form_params_creation.update({'resetcode': request.values.get('resetcode')})
    form = ResetPasswordFormConf(**form_params_creation)
    
    if form.validate_on_submit():
        success, message, message_type = reset_user_password_step_two(form)
        flash(message, message_type)
        if success:
            statsd.incr("user.password.confirm_reset.success")
            return redirect(generate_redirect_url(next_=url_for('user.login')))
        else:
            statsd.incr("user.password.confirm_reset.failed")
    return render_template('reset_password_2.html', form=form)
            

@user_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    User sign up form
    """
    app.logger.debug('User signup')
    #if the user is logged in he needs to logout before signup as another user
    if current_user.is_authenticated():
        flash('Please, logout before sign up as another user', 'warn')
        return redirect(generate_redirect_url())
    form = SignupForm()
    if form.validate_on_submit():
        if not login_exists(form.login.data):
            success, message, message_type =  create_user(form)
            flash(message, message_type)
            if success:
                #save the login email in the session
                session['user_login_email'] = form.login.data
                statsd.incr("user.signup.success")
                return redirect(generate_redirect_url(next_=url_for('user.activate')))
            else:
                statsd.incr("user.signup.failed")
        else:
            flash('An user with the same email address already exists in the system. <a href="%s">Log in</a>' % url_for('user.login'), 'error')
            statsd.incr("user.signup.duplicate")
    return render_template('signup.html', form=form)

@user_blueprint.route('/resend_activation_code_email', methods=['GET', 'POST'])
def resend_activation_code_email():
    """
    request of a new confirmation email
    """
    #if there is not an email in session I need one
    if not session.get('user_login_email'):
        form = PreActivateUserForm(csrf_enabled=False)
        if form.validate_on_submit():
            if not login_exists_local(form.act_em.data):
                if not login_exists_classic(form.act_em.data):
                    flash('There is no user with the provided email. Please sign up first.', 'error')
                    return redirect(generate_redirect_url(url_for('user.signup')))
                else:
                    flash('The user is already active. Please log in.', 'warn')
                    return redirect(generate_redirect_url(url_for('user.login'))) 
            elif login_is_active(form.act_em.data):
                flash('The user is already active. Please log in.', 'warn')
                return redirect(generate_redirect_url(url_for('user.login')))
            #if everything looks fine, the email goes in the session
            session['user_login_email'] = form.act_em.data
        else:
            return render_template('resend_email.html', form=form)
    #if the email is in the session, time to sent the email
    success, message, message_type =  resend_activation_email(session.get('user_login_email'))
    flash(message, message_type)
    if success:
        statsd.incr("user.resend_activation.success")
        return redirect(generate_redirect_url(next_=url_for('user.activate')))
    else:
        statsd.incr("user.resend_activation.failed")
        return redirect(generate_redirect_url(next_=url_for('user.resend_activation_code_email')))

@user_blueprint.route('/activate', methods=['GET', 'POST'])
def activate():
    """
    User activation form
    """
    #if the user is logged in he needs to logout before signup as another user
    if current_user.is_authenticated():
        flash('Please, <a href="%s">logout</a> before activate another user' % url_for('user.logout'), 'warn')
        return redirect(generate_redirect_url())
    
    #if everything looks fine, it's time to proceed
    form_params_creation ={'csrf_enabled':False}
    if request.method == 'GET' and request.values.get('id'):
        #need to specify the value to initialize the form because it cannot find this value in request.form
        form_params_creation.update({'id': request.values.get('id')})    
    form = ActivateUserForm(**form_params_creation)

    if is_submitted_cust(form):
        if form.validate():
            success, message, message_type = activate_user(form.id.data)
            if not success:
                flash('Activation failed: %s' % message, message_type)
                statsd.incr("user.activate.success")
            else:
                flash('Your account is now active.', 'success')
                statsd.incr("user.activate.failed")
                session['user_login_email'] = None
                return redirect(generate_redirect_url(url_for('user.login')))
    elif not session.get('user_login_email'):
        #if there is no email in the session, the user needs to provide it
        pre_form = PreActivateUserForm(csrf_enabled=False)
        if not is_submitted_cust(pre_form) or not pre_form.validate():
            return render_template('activate.html', form=pre_form, pre_activation=True)
        #if there is the email as input, check if the user exists locally and is not active
        if not login_exists_local(pre_form.act_em.data):
            if not login_exists_classic(pre_form.act_em.data):
                flash('There is no user with the provided email. Please sign up first.', 'error')
                return redirect(generate_redirect_url(url_for('user.signup')))
            else:
                flash('The user is already active. Please log in.', 'warn')
                return redirect(generate_redirect_url(url_for('user.login')))
        elif login_is_active(pre_form.act_em.data):
            flash('The user is already active. Please log in.', 'warn')
            return redirect(generate_redirect_url(url_for('user.login')))
        #if everything looks fine with the user login email, it can be stored in the session
        session['user_login_email'] = pre_form.act_em.data
    
    return render_template('activate.html', form=form, pre_activation=False)

@user_blueprint.route('/change_account_settings', methods=['GET', 'POST'])
@login_required
def change_account_settings():
    """
    Allows to change user settings (but not the password)
    """
    app.logger.debug('User change settings')
    #check if the form should be pre-filled with data from the post or from the current user
    form_params_to_check = ['name', 'lastname', 'login']
    form_params = {}
    for param in form_params_to_check:
        if not request.values.get(param) and current_user.is_authenticated():
            if param == 'name':
                form_params['name'] = current_user.user_rec.firstname
            elif param == 'lastname':
                form_params['lastname'] = current_user.user_rec.lastname
            elif param == 'login':
                form_params['login'] = current_user.user_rec.username
                form_params['confirm_login'] = current_user.user_rec.username
    form = ChangeUserParamsForm(**form_params)
    if form.validate_on_submit():
        success, message, message_type = change_user_settings(form)
        flash(message, message_type)
        if success:
            statsd.incr("user.account_change.success")
            return redirect(generate_redirect_url(next_=url_for('user.index')))
        else:
            statsd.incr("user.account_change.failed")
    return render_template('change_params.html', form=form)

@user_blueprint.route('/activate_new_email', methods=['GET', 'POST'])
@login_required
def activate_new_email():
    """
    Activation of the new email address
    """
    form_params_creation ={}
    if request.method == 'GET' and request.values.get('id'):
        #need to specify the value to initialize the form because it cannot find this value in request.form
        form_params_creation.update({'id': request.values.get('id')})    
    form = ActivateNewUsernameForm(**form_params_creation)
    
    if form.validate_on_submit():
        success, message, message_type = activate_user_new_email(form)
        flash(message, message_type)
        if success:
            statsd.incr("user.activate_new_email.success")
            return redirect(generate_redirect_url(next_=url_for('user.index')))
        else:
            statsd.incr("user.activate_new_email.failed")
    return render_template('activate_new_username.html', form=form)


