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
from app import app, lm, pwd_context
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


@app.route('/get_image/<int:listing_id>')
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
        if user is not None and pwd_context.verify(password, user.password):
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
            password = pwd_context.encrypt(password)
            user = User(email, password)
            session.add(user)
            session.commit()
            return ('account successfully created. go to buy5c.com/login' +
                    ' to log in')

    return render_template('register.html')


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
    return render_template('sell.html', email=g.user.email)


#
@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out.")
    return redirect('/index')


@app.route('/')
@app.route('/index')
def index():
    listings = session.query(Listing).order_by(Listing.id.desc()).limit(12).all()
    titles = []
    listing_ids = []
    prices = []
    for x in listings:
        titles.append(x.title)
        listing_ids.append(x.id)
        prices.append(x.price)
    thumbnail_info = zip(titles, listing_ids, prices)

    if g.user.is_authenticated():
        return render_template('index.html',
                               email=g.user.email,
                               listings=listings,
                               active='Everything')
    return render_template('index.html',
                           listings=listings)


@app.route('/a_a/')
def a_a():
    if g.user.is_authenticated():
        return render_template('index.html',
                               username=g.user.email,
                               active='Apparel/Accessories')
    return render_template('a_a.html',
                           active='Apparel/Accessories')


@app.route('/appliances')
def appliances():
    if g.user.is_authenticated():
        return render_template('index.html',
                               username=g.user.email,
                               active='Appliances')
    return render_template('index.html',
                           active='Appliances')


@app.route('/books')
def books():
    if g.user.is_authenticated():
        return render_template('index.html',
                               username=g.user.email,
                               active='Books')
    return render_template('index.html',
                           active='Books')


@app.route('/electronics')
def electronics():
    if g.user.is_authenticated():
        return render_template('index.html',
                               username=g.user.email,
                               active='Electronics')
    return render_template('index.html',
                           active='Electronics')


@app.route('/furniture')
def furniture():
    if g.user.is_authenticated():
        return render_template('index.html',
                               username=g.user.email,
                               active='Furniture')
    return render_template('index.html')


@app.route('/mmg')
def mmg():
    if g.user.is_authenticated():
        return render_template('index.html',
                               username=g.user.email,
                               active='Movies, Music, and Games')
    return render_template('index.html',
                           active='Movies, Music, and Games')


@app.route('/tickets')
def tickets():
    if g.user.is_authenticated():
        return render_template('index.html',
                               username=g.user.email,
                               active='Tickets')
    return render_template('index.html',
                           active='Tickets')


@app.route('/other')
def other():
    if g.user.is_authenticated():
        return render_template('index.html',
                               username=g.user.email,
                               active='Miscellaneous')
    return render_template('index.html',
                           active='Miscellaneous')


@app.route('/listing/<listing_id>')
def listing(listing_id):
    listing = session.query(Listing).get(listing_id)
    if listing.image is None:
        return render_template('listing.html',
                               email=g.user.email,
                               listing_id=listing_id,
                               title=listing.title,
                               body=listing.body,
                               price=listing.price)
    else:
        return render_template('listing.html',
                               email=g.user.email,
                               listing_id=listing_id,
                               title=listing.title,
                               body=listing.body,
                               price=listing.price,
                               image=1)


@app.route('/account')
def account():
    if g.user.is_authenticated():
        return render_template('header.html',
                               email=g.user.email)
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