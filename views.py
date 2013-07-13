import re
import io

from flask import (
    render_template,
    redirect,
    request,
    url_for,
    g,
    flash,
    send_file
)

from flask.ext.login import current_user, login_user, logout_user
from models import *
from app import app, lm
from datetime import datetime


# Some basic regular expressions to match 5C email addresses
# These are not yet actually used, so you can use literally
# any string you want when making a new account. It doesn't
# even have to be an actual email address.
pomona_regex = re.compile(r"[\w.]+@[\w.]*pomona.edu")
cmc_regex = re.compile(r"[\w.]+@[\w.]*cmc.edu")
hmc_regex = re.compile(r"[\w.]+@[\w.]*hmc.edu")
scripps_regex = re.compile(r"[\w.]+@[\w.]*scripps.edu")
pitzer_regex = re.compile(r"[\w.]+@[\w.]*pitzer.edu")


# Used to check if a user's price is a number
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


@app.route('/get_image/<listing_id>')
def get_image(listing_id):
    image_binary = session.query(Listing).get(listing_id).image
    if image_binary is None:
        return False
    return send_file(io.BytesIO(image_binary))


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
    return session.query(User).get(int(id))


# The basic login page and function.
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If a user is already logged in. is_authenticated is a function
    # of the User class in models.py
    if g.user.is_authenticated():
        return 'user already logged in'

    # If the user is sending information (i.e. trying to log in),
    # checks the selected email against the users in the database.
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # queries the database for a user with the email submitted
        user = session.query(User).filter(User.email == email).first()

        # if the user was in the database and the password matches,
        # logs the user in and returns a message.
        if user is not None and user.password == password:
            login_user(user)
            flash('Logged in successfully.')
            return 'login successful'

        return 'username or password invalid'

    # returns login form if request method was GET
    return render_template('login.html')


# The form and function for creating a new account.
@app.route('/register', methods=['GET', 'POST'])
def register():

    # if a user is already logged in
    if g.user.is_authenticated():
        return 'please logout before attempting to create a new account'

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = session.query(User).filter(User.email == email).first()
        if user is not None:
            return 'an account with that email already exists'

       # if no user with that email exists, creates one and adds it to the database
        else:
            user = User(email, password)
            session.add(user)
            session.commit()
            return ('account successfully created. go to buy5c.com/login' +
                    ' to log in')

    return render_template('new_account.html')


# sell page and function: not yet implemented
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if not g.user.is_authenticated():
        return 'you must be logged in to sell an item'

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']
        image = None
        if 'image' in request.files:
            image_file = request.files['image'].read()
            image = buffer(image_file)

        if len(title) == 0:
            return 'please include a title for your item'

        if len(description) == 0:
            return 'please include a description for your item'

        if len(category) == 0:
            return 'please select a category for your item'

        if not is_number(price):
            return 'please input a price for your item'

        category_id = session.query(Category).filter(Category.name == category).first()

        listing = Listing(title, description, category_id, g.user.id, datetime.utcnow(), price, image)
        session.add(listing)
        session.commit()
        return 'listing created'
    return render_template('sell.html')


#
@app.route("/logout")
def logout():
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


@app.route('/a_a/')
def a_a(balls):
    if g.user.is_authenticated():
        return render_template('a_a.html',
                               username=g.user.email)
    return render_template('a_a.html')


@app.route('/appliances')
def appliances():
    if g.user.is_authenticated():
        return render_template('appliances.html',
                               username=g.user.email)
    return render_template('appliances.html')


@app.route('/books')
def books():
    if g.user.is_authenticated():
        return render_template('books.html',
                               username=g.user.email)
    return render_template('books.html')


@app.route('/electronics')
def electronics():
    if g.user.is_authenticated():
        return render_template('electronics.html',
                               username=g.user.email)
    return render_template('electronics.html')


@app.route('/furniture')
def furniture():
    if g.user.is_authenticated():
        return render_template('furniture.html',
                               username=g.user.email)
    return render_template('furniture.html')


@app.route('/mmg')
def mmg():
    if g.user.is_authenticated():
        return render_template('mmg.html',
                               username=g.user.email)
    return render_template('mmg.html')


@app.route('/tickets')
def tickets():
    if g.user.is_authenticated():
        return render_template('tickets.html',
                               username=g.user.email)
    return render_template('tickets.html')


@app.route('/other')
def other():
    if g.user.is_authenticated():
        return render_template('other.html',
                               username=g.user.email)
    return render_template('other.html')


@app.route('/listing/<listing_id>')
def listing(listing_id):
    listing = session.query(Listing).get(listing_id)
    return render_template('listing.html',
                           email=g.user.email,
                           listing_id=listing_id,
                           title=listing.title,
                           body=listing.body,
                           price=listing.price)


@app.route('/account')
def account():
    if g.user.is_authenticated():
        return render_template('header.html')
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