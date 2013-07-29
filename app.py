from flask import Flask
from flask.ext.login import LoginManager
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config
from models import Base


#initializes the app
app = Flask(__name__)
app.config['TESTING'] = False

# setup for login manager from flask-login extension
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://josh:a@localhost/mydb'
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
app_session = Session()
app.config['SESSION'] = app_session
Base.metadata.create_all(engine)
conn = engine.connect()


# CryptContext from passlib used for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt", all__vary_rounds=0.1)

# importing all of the page views and most of the real
# functions from views.py
from views import *


#Not very secret. Must fix.
app.secret_key = 'the secretest of keys'


if __name__ == '__main__':
    app.run(debug=True)
