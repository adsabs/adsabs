from flask.ext.wtf import (Form, HiddenField, BooleanField, #@UnresolvedImport
                          PasswordField, SubmitField, TextField, #@UnresolvedImport
                          ValidationError, required, equal_to, email, #@UnresolvedImport
                          length) #@UnresolvedImport


class LoginForm(Form):
    next = HiddenField()
    remember = BooleanField('Remember me')
    login = TextField('Email address', [required()])
    password = PasswordField('Password', [required(), length(min=6, max=50)])
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