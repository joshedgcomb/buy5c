from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.expression import func
from sqlalchemy.schema import Index

ROLE_USER = 0
ROLE_ADMIN = 1

Base = declarative_base()

# User object to be stored in database. Contains fields for
# unique id number (id), email address (email), password,
# a list of their listings (listings), and role (i.e. regular
# user vs. admin)
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    password = Column(String(64), index=True, unique=True)
    email = Column(String(120), index=True, unique=True)
    role = Column(SmallInteger, default=ROLE_USER)

    listings = relationship('Listing', backref='author')

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

    id = Column(Integer, primary_key=True)
    title = Column(String(140))
    description = Column(String)
    time_posted = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))

    category_id = Column(Integer, ForeignKey('category.id'),
                         index=True)
    price = Column(String(64))
    image = Column(LargeBinary)

    listing_search_index = Index('listing_search_index', func.to_tsvector('english', 'title'),
                                 func.to_tsvector('english', 'description'), postgresql_using='gin')


    def __init__(self, title, description, category_id, user_id, time_posted, price, image=None):
        self.title = title
        self.description = description
        self.category_id = category_id
        self.user_id = user_id
        self.time_posted = time_posted
        self.price = price
        self.image = image

    def __repr__(self):
        return '<Listing %r>' % (self.title)


# Category object to be stored in database. Contains fields for
# unique category number (id), category name, and all the listings
# associated with the category
class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), index=True)
    listings = relationship('Listing', backref='category')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % (self.name)
