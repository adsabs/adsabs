from flask.ext.wtf import (Form, HiddenField, BooleanField, #@UnresolvedImport
                          PasswordField, SubmitField, #TextField, @UnresolvedImport
                          required, length, validators)#ValidationError, equal_to, email, @UnresolvedImport

from flask.ext.wtf.html5 import EmailField #@UnresolvedImport

class LoginForm(Form):
    login = EmailField(u'Email address', [required(), length(min=5, max=2048), validators.Email()])
    password = PasswordField(u'Password', [required(), length(min=6, max=50)])
    remember = BooleanField('Remember me')
    next = HiddenField()
    submit = SubmitField('Login')
    
class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField('Password', [required(), length(min=6, max=50)])
    submit = SubmitField('Reauthenticate')
    
    
class SignupForm(Form):
    pass

class RecoverPasswordForm(Form):
    pass

class ChangePasswordForm(Form):
    pass