from app import db
from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROLE_USER = 0
ROLE_ADMIN = 1

engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()



# User object to be stored in database. Contains fields for
# unique id number (id), email address (email), password,
# a list of their listings (listings), and role (i.e. regular
# user vs. admin)
class User(Base):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)

    listings = db.relationship('Listing', backref='author')

    def __init__(self, email, password, role=ROLE_USER):
        self.email = email
        self.password = password
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
class Listing(Base):
    __tablename__ = 'listing'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), index=True)
    body = db.Column(db.String)
    time_posted = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),
                            index=True)
    image = db.Column(db.BLOB)

    def __init__(self, title, body, category_id, user_id, time_posted, image=None):
        self.title = title
        self.body = body
        self.category_id = category_id
        self.user_id = user_id
        self.time_posted = time_posted
        self.image = image

    def __repr__(self):
        return '<Listing %r>' % (self.title)


# Category object to be stored in database. Contains fields for
# unique category number (id), category name, and all the listings
# associated with the category
class Category(Base):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True)
    listings = db.relationship('Listing', backref='category')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % (self.name)

Base.metadata.create_all(engine)
