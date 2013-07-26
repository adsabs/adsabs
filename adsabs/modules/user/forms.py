from flask.ext.wtf import (Form, HiddenField, BooleanField, #@UnresolvedImport
                          PasswordField, SubmitField, TextField, RecaptchaField, #@UnresolvedImport
                          required, length, validators)#ValidationError, equal_to, email, @UnresolvedImport

from flask.ext.wtf.html5 import EmailField #@UnresolvedImport

class LoginForm(Form):
    login = EmailField(u'Email address', [required(), length(min=5, max=2048), validators.Email()], description=u"Your login email")
    password = PasswordField(u'Password', [required(), length(min=6, max=100)], description=u"Your password")
    remember = BooleanField('Remember me')
    next = HiddenField()
    submit = SubmitField('Login')
    
class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField(u'Password', [required(), length(min=6, max=100)], description=u"Your password")
    submit = SubmitField('Re-authenticate')
    
    
class SignupForm(Form):
    name = TextField(u'Name', [required(), length(min=1, max=2048)], description=u"Your name")
    lastname = TextField(u'Last Name', [required(), length(min=1, max=2048)], description=u"Your last name")
    login = EmailField(u'Email address', [required(), length(min=5, max=2048), validators.Email()], description=u"Your login email")
    confirm_login = EmailField(u'Confirm Email address', [required(), length(min=5, max=2048), validators.Email(), validators.EqualTo('login', message='The two email fields must be equal')], description=u"Repeat your login email")
    password = PasswordField(u'Password', [required(), length(min=6, max=100)], description=u"Your password")
    confirm_password = PasswordField(u'Confirm Password', [required(), length(min=6, max=100), validators.EqualTo('password', message='The two password fields must be equal')], description=u"Repeat Your password")
    recaptcha = RecaptchaField()
    submit = SubmitField('Create user')

class PreActivateUserForm(Form):
    act_em = EmailField(u"Email", [required(), length(min=5, max=2048), validators.Email()], description=u"Your login email")
    submit_act_email = SubmitField('Submit')

class ActivateUserForm(Form):
    id = TextField(u'Activation Code', [required(), length(min=1, max=2048)], description=u"Past here your activation code")
    submit = SubmitField('Activate')

class ActivateNewUsernameForm(ActivateUserForm):
    password = PasswordField(u'Password to confirm changes', [required(), length(min=6, max=100)], description=u"Your password")

class ChangeUserParamsForm(Form):
    name = TextField(u'Name', [required(), length(min=1, max=2048)], description=u"Your name")
    lastname = TextField(u'Last Name', [required(), length(min=1, max=2048)], description=u"Your last name")
    login = EmailField(u'Email address', [required(), length(min=5, max=2048), validators.Email()], description=u"Your login email")
    confirm_login = EmailField(u'Confirm Email address', [required(), length(min=5, max=2048), validators.Email(), validators.EqualTo('login', message='The two email fields must be equal')], description=u"Repeat your login email")
    password = PasswordField(u'Password to confirm changes', [required(), length(min=6, max=100)], description=u"Your password")
    submit = SubmitField('Modify settings')

class ResetPasswordForm(Form):
    login = EmailField(u'Email address', [required(), length(min=5, max=2048), validators.Email()], description=u"Your login email")
    submit = SubmitField('Send temporary reset code')

class ResetPasswordFormConf(ResetPasswordForm):
    resetcode = TextField(u'Reset Code', [required(), length(min=1, max=2048)], description=u"Past here your reset code")
    new_password = PasswordField(u'New Password', [required(), length(min=6, max=100)], description=u"Your new password")
    confirm_new_password = PasswordField(u'Confirm New Password', [required(), length(min=6, max=100), validators.EqualTo('new_password', message='The two password fields must be equal')], description=u"Repeat your new password")
    submit = SubmitField('Change Password')

class ChangePasswordForm(Form):
    old_password = PasswordField(u'Current Password', [required(), length(min=6, max=100)], description=u"Your current password")
    new_password = PasswordField(u'New Password', [required(), length(min=6, max=100)], description=u"Your new password")
    confirm_new_password = PasswordField(u'Confirm New Password', [required(), length(min=6, max=100), validators.EqualTo('new_password', message='The two password fields must be equal')], description=u"Repeat your new password")
    submit = SubmitField('Modify your password')
    
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.old_password.data == self.new_password.data:
            self.new_password.errors.append('The new password must be different from the old one')
            return False
        return True
