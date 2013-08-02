from flask import Flask
from flask.ext.login import LoginManager
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import config
from models import Base
from flask.ext.mail import Mail

first_run = True

#initializes the app
app = Flask(__name__)
app.config['TESTING'] = False
mail = Mail(app)

# setup for login manager from flask-login extension
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://josh:a@localhost/j'
# app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
app_session = Session()
app.config['SESSION'] = app_session
Base.metadata.create_all(engine)
conn = engine.connect()

# The first time you run this, open up a python shell, run this function to setup search index
def setup_search():

    conn.execute('ALTER TABLE listing ADD COLUMN tsv tsvector')
    conn.execute("""update listing set tsv = 
                to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))""")
    conn.execute("""create trigger tsvectorupdate before insert or update
                on listing for each row execute procedure
                tsvector_update_trigger(tsv, 'pg_catalog.english', title, description)""")


# CryptContext from passlib used for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt", all__vary_rounds=0.1)

# importing all of the page views and most of the real
# functions from views.py
from views import *


#Not very secret. Must fix.
app.secret_key = 'the secretest of keys'


if __name__ == '__main__':
    app.run(debug=True)
