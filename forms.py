from flask.ext.wtf import Form, TextField, BooleanField
from flask.ext.wtf import Required, validators


class login_form(Form):
    email = TextField('email', [validators.Required()])
    password = TextField('password', [validators.Required()])  
