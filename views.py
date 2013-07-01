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
# These are not yet actually used, so you can use literally
# any string you want when making a new account. It doesn't
# even have to be an actual email address.
pomona_regex = re.compile(r"[\w.]+@[\w.]*pomona.edu")
cmc_regex = re.compile(r"[\w.]+@[\w.]*cmc.edu")
hmc_regex = re.compile(r"[\w.]+@[\w.]*hmc.edu")
scripps_regex = re.compile(r"[\w.]+@[\w.]*scripps.edu")
pitzer_regex = re.compile(r"[\w.]+@[\w.]*pitzer.edu")


# Before every request that's made, this will run, setting
# flask's global variable g.user to the user currently logged
# in from the computer making the request, allowing for easy
# access.
@app.before_request
def before_request():
    g.user = current_user


# function telling the login manager how to load a user
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


# The basic login page and function.
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If a user is already logged in. is_authenticated is a function
    # of the User class in models.py
    if g.user is not None and g.user.is_authenticated():
        return 'user already logged in'

    # If the user is sending information (i.e. trying to log in),
    # checks the selected email against the users in the database.
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # queries the database for a user with the email submitted
        user = User.query.filter(User.email == email).first()

        # if the user was in the database and the password matches,
        # logs the user in and returns a message.
        if user is not None and user.password == password:
            login_user(user)
            session['email'] = email
            flash('Logged in successfully.')
            return 'login successful'

        return 'username or password invalid'

    # returns login form if request method was GET
    return render_template('login.html')


# The form and function for creating a new account.
@app.route('/new_account', methods=['GET', 'POST'])
def new_account():

    # if a user is already logged in
    if g.user is not None and g.user.is_authenticated():
        return 'please logout before attempting to create a new account'

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter(User.email == email).first()
        if user is not None:
            return 'an account with that email already exists'

       # if no user with that email exists, creates one and adds it to the database
        else:
            user = User(email, password)
            db.session.add(user)
            db.session.commit()
            return ('account successfully created. go to buy5c.com/login' +
                    ' to log in')

    return render_template('new_account.html')

# sell page and function: not yet implemented
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    return 'sell not yet implemented'


# 
@app.route("/logout")
def logout():
    session.pop('email', None)
    logout_user()
    flash("Logged out.")
    return redirect('/index')


@app.route('/')
@app.route('/index')
def index():
    # prints current user 
    print(g.user)

    if g.user.is_authenticated():
        return render_template('index.html',
                               username=g.user.email)
    return render_template('index.html')



@app.route('/a_a')
def a_a():
    if g.user is not None and g.user.is_authenticated():
        return render_template('a_a.html',
                               username=g.user.email)
    return render_template('a_a.html')


@app.route('/appliances')
def appliances():
    if g.user is not None and g.user.is_authenticated():
        return render_template('appliances.html',
                               username=g.user.email)
    return render_template('appliances.html')


@app.route('/books')
def books():
    if g.user is not None and g.user.is_authenticated():
        return render_template('books.html',
                               username=g.user.email)
    return render_template('books.html')


@app.route('/electronics')
def electronics():
    if g.user is not None and g.user.is_authenticated():
        return render_template('electronics.html',
                               username=g.user.email)
    return render_template('electronics.html')


@app.route('/furniture')
def furniture():
    if g.user is not None and g.user.is_authenticated():
        return render_template('furniture.html',
                               username=g.user.email)
    return render_template('furniture.html')


@app.route('/mmg')
def mmg():
    if g.user is not None and g.user.is_authenticated():
        return render_template('mmg.html',
                               username=g.user.email)
    return render_template('mmg.html')


@app.route('/tickets')
def tickets():
    if g.user is not None and g.user.is_authenticated():
        return render_template('tickets.html',
                               username=g.user.email)
    return render_template('tickets.html')


@app.route('/other')
def other():
    if g.user is not None and g.user.is_authenticated():
        return render_template('other.html',
                               username=g.user.email)
    return render_template('other.html')


@app.route('/listing')
def listing():
    if g.user is not None and g.user.is_authenticated():
        return render_template('listing.html',
                               username=g.user.email)
    return render_template('listing.html')


@app.route('/account')
def account():
    if g.user is not None and g.user.is_authenticated():
        return render_template('account.html',
                               username=g.user.email)
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