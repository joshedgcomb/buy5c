import os
import re

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

from flask.ext.login import *
from models import *
from app import db, app, lm
from forms import *


# Some basic regular expressions to match 5C email addresses
pomona_regex = re.compile(r"[\w.]+@[\w.]*pomona.edu")
cmc_regex = re.compile(r"[\w.]+@[\w.]*cmc.edu")
hmc_regex = re.compile(r"[\w.]+@[\w.]*hmc.edu")
scripps_regex = re.compile(r"[\w.]+@[\w.]*scripps.edu")
pitzer_regex = re.compile(r"[\w.]+@[\w.]*pitzer.edu")


@app.route('/new_account')
def new_account():
    return render_template('new_account.html')


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


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        pomona_match = pomona_regex.match(email)
        hmc_match = hmc_regex.match(email)
        cmc_match = cmc_regex.match(email)
        pitzer_match = pitzer_regex.match(email)
        scripps_match = scripps_regex.match(email)

        if ((pomona_match is None) and (hmc_match is None) and
            (cmc_match is None) and (pitzer_match is None) and
                                    (scripps_match is None)):
            return 'fission mailed'

        return 'success'
    return render_template(url_for('index'))


@app.before_request
def before_request():
    g.user = current_user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        return 'user not authenticated'

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter(User.email == email).first()
        if user is not None and user.password == password:
            login_user(user)
            session['email'] = email
            flash('Logged in successfully.')
            print (current_user)
        return 'username or password invalid'
    return render_template('login.html')


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login_redirect', methods=['GET', 'POST'])
def login_redirect():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session['username'] = email

    flash('login failed')
    return redirect(url_for('listing'))


@app.route("/logout")
def logout():
    session.pop('email', None)
    logout_user()
    flash("Logged out.")
    return redirect('/index')


@app.route('/')
@app.route('/index')
def index():
    user = g.user
    print(current_user)
    if current_user.is_authenticated():
        return render_template('index.html',
                               username='asdf')
    return render_template('index.html')



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