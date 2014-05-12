from flask.ext.wtf import (Form, RecaptchaField)      
from wtforms import (HiddenField, BooleanField,
                     PasswordField, SubmitField, TextField, validators)
from wtforms.validators import (required, length)   #ValidationError, equal_to, email
from flask.ext.wtf.html5 import EmailField 

from config import config

class LoginForm(Form):
    login = EmailField(u'Email address', [required(), length(min=1, max=2048), validators.Email()], description=u"Your login email")
    password = PasswordField(u'Password', [required(), length(min=config.USER_MIN_PASSWORD_LENGTH, max=config.USER_MAX_PASSWORD_LENGTH)], description=u"Your password")
    remember = BooleanField('Remember me')
    next = HiddenField()
    submit = SubmitField('Login')
    
class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(u'Password', [required(), length(min=config.USER_MIN_PASSWORD_LENGTH, max=config.USER_MAX_PASSWORD_LENGTH)], description=u"Your password")
    submit = SubmitField('Re-authenticate')
    
    
class SignupForm(Form):
    name = TextField(u'Name', [length(min=1, max=30)], description=u"Your name")
    lastname = TextField(u'Last Name', [required(), length(min=1, max=30)], description=u"Your last name")
    login = EmailField(u'Email address', [required(), length(min=5, max=40), validators.Email()], description=u"Your login email")
    confirm_login = EmailField(u'Confirm Email address', [required(), length(min=5, max=40), validators.Email(), validators.EqualTo('login', message='The two email fields must be equal')], description=u"Repeat your login email")
    password = PasswordField(u'Password', [required(), length(min=config.USER_MIN_PASSWORD_LENGTH, max=config.USER_MAX_PASSWORD_LENGTH)], description=u"Your password")
    confirm_password = PasswordField(u'Confirm Password', [required(), length(min=config.USER_MIN_PASSWORD_LENGTH, max=config.USER_MAX_PASSWORD_LENGTH), validators.EqualTo('password', message='The two password fields must be equal')], description=u"Repeat Your password")
    submit = SubmitField('Create user')
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if len(self.name.data) + len(self.lastname.data) > 29: #name plus lastname cannot be bigger than 29 (one char reserved for the separator)
            self.name.errors.append('The name and the last name cannot be more than 29 chars long together (we will fix this, we promise)')
            self.lastname.errors.append('The name and the last name cannot be more than 29 chars long together (we will fix this, we promise)')
            return False
        return True

if config.RECAPTCHA_ENABLED:
    setattr(SignupForm, "recaptcha", RecaptchaField())   

class PreActivateUserForm(Form):
    act_em = EmailField(u"Email", [required(), length(min=5, max=40), validators.Email()], description=u"Your login email")
    submit_act_email = SubmitField('Submit')

class ActivateUserForm(Form):
    id = TextField(u'Activation Code', [required(), length(min=1, max=2048)], description=u"Past here your activation code")
    submit = SubmitField('Activate')

class ActivateNewUsernameForm(ActivateUserForm):
    password = PasswordField(u'Password to confirm changes', [required(), length(min=config.USER_MIN_PASSWORD_LENGTH, max=config.USER_MAX_PASSWORD_LENGTH)], description=u"Your password")

class ChangeUserParamsForm(Form):
    name = TextField(u'Name', [length(min=1, max=30)], description=u"Your name")
    lastname = TextField(u'Last Name', [required(), length(min=1, max=30)], description=u"Your last name")
    login = EmailField(u'Email address', [required(), length(min=5, max=40), validators.Email()], description=u"Your login email")
    confirm_login = EmailField(u'Confirm Email address', [required(), length(min=5, max=40), validators.Email(), validators.EqualTo('login', message='The two email fields must be equal')], description=u"Repeat your login email")
    password = PasswordField(u'Password to confirm changes', [required(), length(min=config.USER_MIN_PASSWORD_LENGTH, max=config.USER_MAX_PASSWORD_LENGTH)], description=u"Your password")
    submit = SubmitField('Modify settings')
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if len(self.name.data) + len(self.lastname.data) > 29: #name plus lastname cannot be bigger than 29 (one char reserved for the separator)
            self.name.errors.append('The name and the last name cannot be more than 29 chars long together (we will fix this, we promise)')
            self.lastname.errors.append('The name and the last name cannot be more than 29 chars long together (we will fix this, we promise)')
            return False
        return True

class ResetPasswordForm(Form):
    login = EmailField(u'Email address', [required(), length(min=5, max=40), validators.Email()], description=u"Your login email")
    submit = SubmitField('Send temporary reset code')

class ResetPasswordFormConf(ResetPasswordForm):
    resetcode = TextField(u'Reset Code', [required(), length(min=1, max=2048)], description=u"Past here your reset code")
    new_password = PasswordField(u'New Password', [required(), length(min=config.USER_MIN_PASSWORD_LENGTH, max=config.USER_MAX_PASSWORD_LENGTH)], description=u"Your new password")
    confirm_new_password = PasswordField(u'Confirm New Password', [required(), length(min=config.USER_MIN_PASSWORD_LENGTH, max=config.USER_MAX_PASSWORD_LENGTH), validators.EqualTo('new_password', message='The two password fields must be equal')], description=u"Repeat your new password")
    submit = SubmitField('Change Password')

class ChangePasswordForm(Form):
    old_password = PasswordField(u'Current Password', [required(), length(min=config.USER_MIN_PASSWORD_LENGTH, max=config.USER_MAX_PASSWORD_LENGTH)], description=u"Your current password")
    new_password = PasswordField(u'New Password', [required(), length(min=config.USER_MIN_PASSWORD_LENGTH, max=config.USER_MAX_PASSWORD_LENGTH)], description=u"Your new password")
    confirm_new_password = PasswordField(u'Confirm New Password', [required(), length(min=config.USER_MIN_PASSWORD_LENGTH, max=config.USER_MAX_PASSWORD_LENGTH), validators.EqualTo('new_password', message='The two password fields must be equal')], description=u"Repeat your new password")
    submit = SubmitField('Modify your password')
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.old_password.data == self.new_password.data:
            self.new_password.errors.append('The new password must be different from the old one')
            self.confirm_new_password.errors.append('The new password must be different from the old one')
            return False
        return True
