import os

from flask import (
    Flask,
    render_template,
    session,
    redirect,
    request,
    url_for,
    g,
    flash,
    escape
)
import db
import urllib
import requests
import json
import datetime
from flask.ext.mongokit import MongoKit, Document
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)

import re


USERS = {
    
}


app = Flask(__name__)

login_manager = LoginManager()
login_manager.login_view = "login_redirect"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"
app.config.from_object(__name__)


@login_manager.user_loader
def load_user(id):
    for x in db.users.find():
        if x['username'] == id:
            return User(x['username'], x['email'], x['password'], x['active'])

login_manager.setup_app(app)

db = MongoKit(app)

# set the secret key.  keep this really secret:
app.secret_key = 'fuck you this is my secret key'


@app.route('/new_account')
def new_account():
    return render_template('new_account.html')



class User_Account(Document):
    __collection__ = 'users'
    structure = {
        'username': basestring,
        'email': basestring,
        'password': basestring,
        'active': bool,
        'listings': list
    }
    required_fields = ['username', 'email', 'password']
    use_dot_notation = True

class Listing(Document):
    __collection__ = 'listings'
    structure = {
        'item': basestring,
        'description': basestring,
        'category': basestring,
        'price': basestring,
        'image': basestring,
        'username': basestring
    }
    required_fields = ['item', 'category', 'price', 'username']
    use_dot_notation = True



class User():
    def __init__(self, username, email, password, active):
        self.username = username
        self.email = email
        self.password = password
        self.active = active

    def is_active(self):
        return self.active


    def is_anonymous(self):
        return False


    def is_authenticated(self):
        return True


    def get_id(self):
        return self.username

    

db.register([User_Account])
db.register([Listing])


@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if request.method == 'POST':
        listing = db.Listing()
        listing.item = request.form['item']
        listing.description = request.form['desc']
        listing.category = request.form['category']
        listing.price = request.form['price']
        listing.image = request.form['image']
        listing.save()

        return render_template('listing.html', listing=listing)
    return render_template('index.html')

@app.route('/new_listing')
def new_listing():
    return render_template('sell.html')


pomona_regex = re.compile(r"[\w.]+@[\w.]*pomona.edu")
cmc_regex = re.compile(r"[\w.]+@[\w.]*cmc.edu")
hmc_regex = re.compile(r"[\w.]+@[\w.]*hmc.edu")
scripps_regex = re.compile(r"[\w.]+@[\w.]*scripps.edu")
pitzer_regex = re.compile(r"[\w.]+@[\w.]*pitzer.edu")

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        listings = []


        pomona_match = pomona_regex.match(email)
        hmc_match = hmc_regex.match(email)
        cmc_match = cmc_regex.match(email)
        pitzer_match = pitzer_regex.match(email)
        scripps_match = scripps_regex.match(email)

        if ((pomona_match is None) and (hmc_match is None) and
            (cmc_match is None) and (pitzer_match is None) and
            (scripps_match is None)):
            return 'you done fucked up'


        

        if (db.users.find_one(username) is None):
            account = db.User_Account
            account.username = username
            account.email = email
            account.password = password
            account.active = False
            account.save()
        return 'john is a poopyhead'
    return render_template(url_for('index'))



@app.before_request
def before_request():
    g.user = current_user


@app.route('/login',)
def login():
    return render_template('login.html')


@app.route('/login_redirect', methods=['GET', 'POST'])
def login_redirect():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        for x in db.users.find():
            if x['email'] == email and x['password'] == password:
                session['username'] = email
                x['active'] = True
                user = User(x['username'], x['email'], x['password'], x['active'])
                USERS[email] = user
                return redirect(url_for('index'))

    flash('login failed')
    return redirect(url_for('index'))



@app.route("/logout")
def logout():
    session.pop('username', None)
    logout_user()
    flash("Logged out.")
    return redirect('/index')

@login_manager.user_loader
def load_user(id):
    return False



@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        return render_template('index.html',
                               username=escape(session['username']))
    return render_template('index.html')


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



@app.route('/a_a')
def a_a():
    if 'username' in session:
        return render_template('a_a.html',
                               username=escape(session['username']))
    return render_template('a_a.html')


@app.route('/appliances')
def appliances():
    if 'username' in session:
        return render_template('appliances.html',
                               username=escape(session['username']))
    return render_template('appliances.html')


@app.route('/books')
def books():
    if 'username' in session:
        return render_template('books.html',
                               username=escape(session['username']))
    return render_template('books.html')


@app.route('/electronics')
def electronics():
    if 'username' in session:
        return render_template('electronics.html',
                               username=escape(session['username']))
    return render_template('electronics.html')


@app.route('/furniture')
def furniture():
    if 'username' in session:
        return render_template('furniture.html',
                               username=escape(session['username']))
    return render_template('furniture.html')


@app.route('/mmg')
def mmg():
    if 'username' in session:
        return render_template('mmg.html',
                               username=escape(session['username']))
    return render_template('mmg.html')


@app.route('/tickets')
def tickets():
    if 'username' in session:
        return render_template('tickets.html',
                               username=escape(session['username']))
    return render_template('tickets.html')


@app.route('/other')
def other():
    if 'username' in session:
        return render_template('other.html',
                               username=escape(session['username']))
    return render_template('other.html')

@app.route('/listing')
def listing():
    if 'username' in session:
        return render_template('listing.html',
                               username=escape(session['username']))
    return render_template('listing.html')


@app.route('/account')
def account():
    if 'username' in session:
        return render_template('account.html',
                               username=escape(session['username']))
    return redirect(url_for('login'))


@app.route('/about')
def about():
    return False


@app.route('/terms')
def terms():
    return False


@app.route('/contact')
def contact():
    return False


@app.route('/feedback')
def feedback():
    return False

if __name__ == '__main__':
    app.run(debug=True)
