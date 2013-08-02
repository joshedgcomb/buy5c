# Automated functional tests for buy5c. Test end user functionality with
# gets and posts using a test sqlite database created in memory.
# 
# Some code snippets, such as creating a user and logging them in, are
# repeated several times. This is done to keep the number of things
# tested in each test to a minimum, allowing for easier pinpointing
# of bugs.
# 
# Unit tests in unit_tests.py.

from app import app, pwd_context
import unittest
from flask import g
from models import *
from sqlalchemy.orm import sessionmaker
from flask.ext.login import current_user
from datetime import datetime

app.config['TESTING'] = True
engine = create_engine('sqlite:///:memory')
Session = sessionmaker(bind=engine)
session = Session()
app.config['SESSION'] = session


class Buy5cTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_user_can_create_new_account(self):
        email = 'steve-o'
        password = 'wonder_woman'
        encrypted_password = pwd_context.encrypt(password)
        rv = self.app.post('/register', data=dict(
            email=email,
            password=password))
        user = session.query(User).filter(User.email == email).first()
      
        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        pwd_context.verify(encrypted_password, user.password)

    def test_user_can_login(self):
        email = 'login_test'
        password = 'login_test'
        user = User(email, pwd_context.encrypt(password))
        session.add(user)
        session.commit()

        with self.app as c:
            c.post('/login', data=dict(
            email=email,
            password=password))
            self.assertEqual(user, current_user)

    def test_user_can_logout(self):
        email = 'logout_test'
        password = 'logout_test'
        user = User(email, pwd_context.encrypt(password))
        session.add(user)
        session.commit()

        with self.app as c:
            c.post('/login', data=dict(
            email=email,
            password=password))
            self.assertEqual(user, current_user, "Could not test user logout because login failed.")

            c.get('/logout')
            self.assertNotEqual(user, current_user, "User still logged in.")

    def test_user_can_create_a_listing(self):
        email = 'listing_creation_test'
        password = 'listing_creation_test'
        user = User(email, pwd_context.encrypt(password))
        session.add(user)
        session.commit()

        with self.app as c:
            c.post('/login', data=dict(
            email=email,
            password=password))
            self.assertEqual(user, current_user, "Could not test user listing creation because login failed.")

            title = 'listing creation test title'
            description = 'listing creation test description'
            category_id = '7'
            price = '50'

            c.post('/sell', data=dict(
                title=title,
                description=description,
                category=category_id,
                price=price,
                image=None
                ))

            listing = session.query(Listing).filter(Listing.title == 'listing creation test title').first()
            self.assertIsNotNone(listing)
            self.assertEqual(listing.title, title)
            self.assertEqual(listing.description, description)
            self.assertEqual(listing.price, price)
            self.assertEqual(listing.user_id, user.id)

    #put tests covering listing editing and deletion here when functionality added


    def test_anonymous_user_can_view_a_listing(self):
        title = 'anonymous view title'
        description = 'anonymous view description'
        category_id = '5'  # arbitrary value, not important for this test
        user_id = '5'  # ibid
        time_posted = datetime.utcnow()
        price = '50'  # ibid
        image = None
        listing = Listing(title, description, category_id, user_id, time_posted, price, image)

        session.add(listing)
        session.commit()
        listing_id = session.query(Listing).filter(Listing.title == title).first().id

        response_form = self.app.get('/listing/' + str(listing_id))
        self.assertIn(description, response_form.data)

    def test_attempt_to_view_invalid_listing_gives_404(self):
        response_form = self.app.get('/listing/79870907989870987')  # arbitrary nonexistent listing
        self.assertIn('404', response_form.data)

    def test_user_can_edit_their_listing(self):
        email = 'listing editing email'
        password = 'listing editing password'
        user = User(email, pwd_context.encrypt(password))

        listing_id = 9000000
        title = 'listing editing title'
        description = 'listing editing description'
        category_id = '5'  # arbitrary value, not important for this test
        user_id = '5'  # ibid
        time_posted = datetime.utcnow()
        price = '50'  # ibid
        image = None
        listing = Listing(title, description, category_id, user_id, time_posted, price, image)

        session.add(user)
        session.commit()

        user_in_database = session.query(User).filter(User.email == email).first()
        listing.user_id = user_in_database.id
        listing.id = listing_id

        session.add(listing)
        session.commit()

        with self.app as c:
            c.post('/login', data=dict(
            email=email,
            password=password))
            self.assertEqual(user, current_user, "Could not test user listing editing because login failed.")

            new_title = 'new listing editing title'
            new_description = 'new listing editing description'
            new_category_id = '8'
            new_price = '75'
            rv = c.post('/listing/' + str(listing_id) + '/edit', data=dict(
                title=new_title,
                description=new_description,
                category=new_category_id,
                price=new_price,
                ), follow_redirects=True)

        edited_listing = session.query(Listing).get(listing_id)

        self.assertEqual(edited_listing.title, new_title)
        self.assertEqual(edited_listing.description, new_description)
        # self.assertEqual(edited_listing.category_id, new_category_id)  #Categories not yet implemented
        self.assertEqual(edited_listing.price, new_price)

    def test_user_cannot_edit_listing_if_not_logged_in(self):
        email = 'listing editing1 email'
        password = 'listing editing1 password'
        user = User(email, pwd_context.encrypt(password))

        listing_id = 90000001
        title = 'listing editing1 title'
        description = 'listing editing1 description'
        category_id = '5'  # arbitrary value, not important for this test
        user_id = '5'  # ibid
        time_posted = datetime.utcnow()
        price = '50'  # ibid
        image = None
        listing = Listing(title, description, category_id, user_id, time_posted, price, image)

        session.add(user)
        session.commit()

        user_in_database = session.query(User).filter(User.email == email).first()
        listing.user_id = user_in_database.id
        listing.id = listing_id

        session.add(listing)
        session.commit()

        with self.app as c:

            new_title = 'new listing editing1 title'
            new_description = 'new listing editing1 description'
            new_category_id = '8'
            new_price = '751'
            rv = c.post('/listing/' + str(listing_id) + '/edit', data=dict(
                title=new_title,
                description=new_description,
                category=new_category_id,
                price=new_price,
                ), follow_redirects=True)

        edited_listing = session.query(Listing).get(listing_id)

        self.assertNotEqual(edited_listing.title, new_title)
        self.assertNotEqual(edited_listing.description, new_description)
        # self.assertEqual(edited_listing.category_id, new_category_id)  #Categories not yet implemented
        self.assertNotEqual(edited_listing.price, new_price)


    def test_user_that_did_not_create_listing_cannot_edit_it(self):

        email = 'listing editing2 email'
        password = 'listing editing2 password'
        user = User(email, pwd_context.encrypt(password))

        listing_id = 90000002
        title = 'listing editing2 title'
        description = 'listing editing2 description'
        category_id = '5'  # arbitrary value, not important for this test
        user_id = '5'  # ibid
        time_posted = datetime.utcnow()
        price = '50'  # ibid
        image = None
        # creating the listing object
        listing = Listing(title, description, category_id, user_id, time_posted, price, image)

        # adding the user to the db
        session.add(user)
        session.commit()

        # associating the user and the listing
        user_in_database = session.query(User).filter(User.email == email).first()
        listing.user_id = user_in_database.id + 1  # ensuring that our user's id and the listing's creator are not the same
        listing.id = listing_id

        session.add(listing)
        session.commit()

        with self.app as c:
            c.post('/login', data=dict(
            email=email,
            password=password))
            self.assertEqual(user, current_user, "Could not test user listing editing because login failed.")

            new_title = 'new listing editing2 title'
            new_description = 'new listing editing2 description'
            new_category_id = '8'
            new_price = '752'
            rv = c.post('/listing/' + str(listing_id) + '/edit', data=dict(
                title=new_title,
                description=new_description,
                category=new_category_id,
                price=new_price,
                ), follow_redirects=True)

        edited_listing = session.query(Listing).get(listing_id)

        self.assertNotEqual(edited_listing.title, new_title)
        self.assertNotEqual(edited_listing.description, new_description)
        # self.assertEqual(edited_listing.category_id, new_category_id)  #Categories not yet implemented
        self.assertNotEqual(edited_listing.price, new_price)


    def test_user_account_page_shows_listings(self):
        email = 'account test email'
        password = 'account test password'
        user = User(email, pwd_context.encrypt(password))

        listing_id = 90000003
        title = 'account test title'
        description = 'account test description'
        category_id = '5'  # arbitrary value, not important for this test
        user_id = '5'  # ibid
        time_posted = datetime.utcnow()
        price = '50'  # ibid
        image = None
        # creating the listing object
        listing = Listing(title, description, category_id, user_id, time_posted, price, image)

        # adding the user to the db
        session.add(user)
        session.commit()

        # associating the user and the listing
        user_in_database = session.query(User).filter(User.email == email).first()
        listing.user_id = user_in_database.id

        session.add(listing)
        session.commit()

        other_title = 'account test2 title'
        user_id = 777
        listing = Listing(other_title, description, category_id, user_id, time_posted, price, image)

        session.add(listing)
        session.commit()

        with self.app as c:
            c.post('/login', data=dict(
            email=email,
            password=password))
            self.assertEqual(user, current_user, "Could not test user listing editing because login failed.")

            rv = c.get('/account')

            self.assertIn(title, rv.data)
            # listing
            self.assertNotIn(other_title, rv.data)













if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    unittest.main()
