from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from passlib.context import CryptContext


#initializes the app
app = Flask(__name__)

# setup for login manager from flask-login extension
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

# database setup. Uses sqlite database via sqlalchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

# CryptContext from passlib used for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt", all__vary_rounds=0.1)

# importing all of the page views and most of the real
# functions from views.py
from views import *

#Not very secret. Must fix.
app.secret_key = 'the secretest of keys'


if __name__ == '__main__':
    app.run(debug=True)
