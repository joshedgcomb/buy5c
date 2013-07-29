import re
import io

from flask import (
    render_template,
    redirect,
    request,
    url_for,
    g,
    flash,
    send_file,
    abort
)

from flask.ext.login import current_user, login_user, logout_user
from models import *
from app import app, lm, pwd_context, app_session
from datetime import datetime

session = app_session

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


def get_listings(category=None, page_size=24, page_offset=0, user_id=None):
    # for user specific listing queries, this can only return all of a user's listings
    if user_id:
        user = session.query(User).get(user_id)
        listings = user.listings
        return listings

    if category is None:
        listings = session.query(Listing).order_by(Listing.id.desc()).limit(page_size).offset(page_size*page_offset).all()
    else:
        category_id = session.query(Category).filter(Category.name == category).first().id
        listings = session.query(Listing).filter(Listing.category_id == category_id).order_by(Listing.id.desc()).limit(page_size).offset(page_size*page_offset).all()

    return listings


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
    global session
    session = app.config['SESSION']


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
        return render_template('index.html', 
                                message='A user is already logged in.',
                                email=g.user.email,
                                listings=get_listings())

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
            return render_template('index.html',
                                    message='Login was successful.',
                                    email=user.email,
                                    listings=get_listings())

        return render_template('index.html',
                                message='Email or password invalid. Please try again.',
                                listings=get_listings())

    # returns login form if request method was GET
    return render_template('login.html')


# The form and function for creating a new account.
@app.route('/register', methods=['GET', 'POST'])
def register():

    # if a user is already logged in
    if g.user.is_authenticated():
        return render_template('index.html',
                                message='Please logout before attempting to create a new_account.',
                                email=g.user.email,
                                listings=get_listings())

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = session.query(User).filter(User.email == email).first()
        if user is not None:
            return render_template('index.html',
                                    message='An account with that email already exists. If you have forgotten your password,'
                                    + ' go to "buy5c.com/forgot_password" to find out how to reset it.',
                                    listings=get_listings())

       # if no user with that email exists, creates one and adds it to the database
        else:
            password = pwd_context.encrypt(password)
            user = User(email, password)
            session.add(user)
            session.commit()
            return render_template('index.html',
                                    message='Account successfully created.',
                                    listings=get_listings())

    return render_template('register.html')


# sell page and function: not yet implemented
@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if not g.user.is_authenticated():
        return render_template('index.html',
                                message='You must be logged in to sell an item.',
                                listings=get_listings())

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
            return render_template('sell.html',
                                    message='Please include a title for your item.',
                                    email=g.user.email)

        if len(description) == 0:
            return render_template('sell.html',
                                    message='Please include a description for your item.',
                                    email=g.user.email)

        if len(category) == 0:
            return render_template('sell.html',
                                    message='Please select a category for your item.',
                                    email=g.user.email)

        if not is_number(price):
            return render_template('sell.html',
                                    message='Please include a price for your item. Note: it must be a number',
                                    email=g.user.email)

        category_id = session.query(Category).filter(Category.name == category).first()

        listing = Listing(title, description, category_id, g.user.id, datetime.utcnow(), price, image)
        session.add(listing)
        session.commit()
        return render_template('index.html',
                                message='Listing successfully created',
                                email=g.user.email,
                                listings=get_listings())
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
    if g.user.is_authenticated():
        return render_template('index.html',
                               email=g.user.email,
                               listings=get_listings(),
                               active='Everything')
    return render_template('index.html',
                           listings=get_listings(),
                           active='Everything')


@app.route('/a_a/')
def a_a():
    if g.user.is_authenticated():
        return render_template('index.html',
                               username=g.user.email,
                               active='Apparel/Accessories')
    return render_template('index.html',
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
    if listing is None:
        abort(404)

    if g.user.is_authenticated():
        if listing.image is None:
            return render_template('listing.html',
                                   email=g.user.email,
                                   user_id=g.user.id,
                                   listing_user_id=listing.user_id,
                                   listing_id=listing_id,
                                   title=listing.title,
                                   description=listing.description,
                                   price=listing.price)
        else:
            return render_template('listing.html',
                                   email=g.user.email,
                                   user_id=g.user.id,
                                   listing_user_id=listing.user_id,
                                   listing_id=listing_id,
                                   title=listing.title,
                                   description=listing.description,
                                   price=listing.price,
                                   image=listing.image)
    else:
        if listing.image is None:
            return render_template('listing.html',
                                   listing_id=listing_id,
                                   title=listing.title,
                                   description=listing.description,
                                   price=listing.price)
        else:
            return render_template('listing.html',
                                   listing_id=listing_id,
                                   title=listing.title,
                                   description=listing.description,
                                   price=listing.price,
                                   image=listing.image)


@app.route('/listing/<listing_id>/edit', methods=['GET', 'POST'])
def edit_listing(listing_id):
    listing = session.query(Listing).get(listing_id)
    if listing is None:
        return abort(404)

    if not g.user.is_authenticated():
        return render_template('listing.html',
                                listing_id=listing_id,
                                title=listing.title,
                                description=listing.description,
                                price=listing.price,
                                image=listing.image,
                                message='You must be logged in to edit your listing.')

    if g.user.id != listing.user_id:
        return render_template('listing.html',
                                email=g.user.email,
                                listing_id=listing_id,
                                title=listing.title,
                                description=listing.description,
                                price=listing.price,
                                image=listing.image,
                                message='Only the creator of this listing may edit it.')

    if request.method == 'GET':
        return render_template('edit_listing.html',
                                listing_id=listing_id,
                                title=listing.title,
                                description=listing.description,
                                price=listing.price,
                                image=listing.image)

    elif request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']
        image = None
        if 'image' in request.files:
            image_file = request.files['image'].read()
            image = buffer(image_file)
            listing.image = image

        if title != '':
            listing.title = title

        if description != '':
            listing.description = description

        if category != '':
            category_id = session.query(Category).filter(Category.name == category).first()
            listing.category_id = category_id

        if price != '' and is_number(price):
            listing.price = price

        session.commit()
        return redirect(url_for('listing', listing_id=listing.id))






@app.route('/account')
def account():
    if g.user.is_authenticated():
        listings = get_listings(user_id=g.user.id)
        return render_template('account.html',
                               email=g.user.email,
                               listings=listings
                               )
    return redirect(url_for('login'))

# @app.route('/search', methods=['POST'])
def search(query_string):
    # terms = request.form['terms']
    query_string = "select * from listing where to_tsvector('english', description) @@ plainto_tsquery('english','" + query_string + "')"
    listings = session.execute(query_string)
    return listings.fetchall()


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


@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html'), 404
