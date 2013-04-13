import os

from flask import (
    Flask,
    render_template,
    session,
    redirect,
    request,
    url_for,
    g,
    flash
)
import db
import urllib
import requests
import json
import datetime
from flask.ext.mongokit import MongoKit, Document
from flask.ext.login import (
    LoginManager,
    login_user,
    logout_user,
    current_user
)

import re


app = Flask(__name__)

login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'login'

db = MongoKit(app)

# set the secret key.  keep this really secret:
app.secret_key = 'fuck you this is my secret key'


@login_manager.user_loader
def load_user(userid):
    return User.get(userid)


class User_Account(Document):
    __collection__ = 'users'
    structure = {
        'username': basestring,
        'email': basestring,
        'password': basestring,
    }

    required_fields = ['username', 'email', 'password']
    use_dot_notation = True

db.register([User_Account])

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        account = db.User_Account
        account.username = request.form['username']
        account.email = request.form['email']
        account.password = request.form['password']
        account.save()
        return 'john is a poopyhead'
    return render_template(url_for('index'))

@app.route('/new_account')
def new_account():
    return render_template('new_account.html')




pomona_regex = re.compile(r"[\w.]+@[\w.]*pomona.edu")
cmc_regex = re.compile(r"[\w.]+@[\w.]*cmc.edu")
hmc_regex = re.compile(r"[\w.]+@[\w.]*hmc.edu")
scripps_regex = re.compile(r"[\w.]+@[\w.]*scripps.edu")
pitzer_regex = re.compile(r"[\w.]+@[\w.]*pitzer.edu")



'''class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)
        '''

YELP_SEARCH_URL = 'http://api.yelp.com/v2/search'


@app.before_request
def before_request():
    g.user = current_user


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        #!!!return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


#!!!@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/')
@app.route('/index')
#!!!@login_required
def index():
    user = g.user
    posts = [
        {
            'author': {'nickname': 'John'}, 
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'nickname': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',
                           title='Home',
                           user=user,
                           posts=posts)


@app.route('/results', methods=['POST'])
def results():
    search_term = request.form['term']
    location = request.form['location']

    data = {
        'term': search_term,
        'location': location
    }
    query_string = urllib.urlencode(data)
    api_url = YELP_SEARCH_URL + "?" + query_string
    signed_url = sign_url(api_url)
    response = requests.get(signed_url)
    json_response = json.loads(response.text)

    return render_template('results.html',
                           search_term=search_term,
                           location=location,
                           businesses=json_response['businesses'])


@app.route('/save', methods=["POST"])
def save():
    new_entry = collection.Entry()
    new_entry.name = request.form['name']
    new_entry.url = request.form['url']
    new_entry.phone_number = request.form['phone_number']
    new_entry.address = request.form['address']
    new_entry.categories = request.form.getlist('categories')

    new_entry.save()

    return redirect('/')
if __name__ == '__main__':
    app.run(debug=True)
