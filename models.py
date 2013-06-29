from app import db

ROLE_USER = 0
ROLE_ADMIN = 1


# User object to be stored in database. Contains fields for
# unique id number (id), email address (email), password,
# a list of their listings (listings), and role (i.e. regular
# user vs. admin)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)

    listings = db.relationship('Listing', backref=db.backref('author', lazy='dynamic'))

    def __init__(self, password, email, role=ROLE_USER):
        self. password = password
        self.email = email
        self.role = role

    def __repr__(self):
        return '<User %r>' % (self.email)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)


# Listing object to be stored in database. Contains fields for
# a unique listing number (id), title, the body text (body), the
# time posted, the category it belongs to, and any images associated
# with it
class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), index=True)
    body = db.Column(db.String)
    time_posted = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                            index=True)
    images = db.relationship('Image', backref=db.backref('images', lazy='dynamic'))

    def __init__(self, title, body, category_id, time_posted):
        self.title = title
        self.body = body
        self.category_id = category_id
        self.time_posted = time_posted

    def __repr__(self):
        return '<Listing %r>' % (self.title)


# Category object to be stored in database. Contains fields for
# unique category number (id), category name, and all the listings
# associated with the category
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    listings = db.relationship('Listing', backref='category', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % (self.name)


# Image type to be stored in database. Has only a unique id number
# and the image itself.
class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.BLOB)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'))
