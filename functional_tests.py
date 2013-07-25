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
        rv = self.app.post('/register', data=dict(
            email=email,
            password=password))
        user = session.query(User).filter(User.email == email).first()
        assert user is not None

    def test_user_can_login(self):
        email = 'login_test'
        password = 'login_test'
        user = User(email, pwd_context.encrypt(password))
        session.add(user)
        session.commit()

        with app.test_client() as c:
            c.post('/login', data=dict(
            email=email,
            password=password))
            print current_user
            self.assertEqual(user, current_user)

    def test_user_can_logout(self):
        email = 'logout_test'
        password = 'logout_test'
        user = User(email, pwd_context.encrypt(password))
        session.add(user)
        session.commit()

        with app.test_client() as c:
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

        with app.test_client() as c:
            c.post('/login', data=dict(
            email=email,
            password=password))
            self.assertEqual(user, current_user, "Could not test user listing creation because login failed.")

            c.post('/sell', data=dict(
                title='listing creation test title',
                description='listing creation test description',
                category='listing creation test category',
                price='50', #arbitrary value since non number values are not accepted
                ))

            listing = session.query(Listing).filter(Listing.title == 'listing creation test title').first()
            self.assertIsNotNone(listing)

    #put tests covering listing editing and deletion here when functionality added


    def test_anonymous_user_can_view_a_listing(self):
        title = 'anonymous view title'
        description = 'anonymous view description'
        category_id = '5' # arbitrary value, not important for this test
        user_id = '5' # ibid
        time_posted = datetime.utcnow()
        price = '50' # ibid
        image = None
        listing = Listing(title, description, category_id, user_id, time_posted, price, image)

        session.add(listing)
        session.commit()
        listing_id = session.query(Listing).filter(Listing.title == title).first().id

        response_form = self.app.get('/listing/' + str(listing_id))
        self.assertIn(description, response_form.data)

    def test_attempt_to_view_invalid_listing_gives_404(self):
        response_form = self.app.get('/listing/79870907989870987') # arbitrary nonexistent listing
        self.assertIn('404', response_form.data)











if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    unittest.main()
