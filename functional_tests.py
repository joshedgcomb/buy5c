from app import app
import unittest
from selenium import webdriver
from flask.ext.testing import TestCase
from flask import Flask
from models import *

app.config['TESTING'] = True
engine = create_engine('sqlite:///:memory')
Session = sessionmaker(bind=engine)
session = Session()
app.config['SESSION'] = session


class Buy5cTestCase(unittest.TestCase):
    # browser = webdriver.Firefox()
    # browser.implicitly_wait(3)

    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_user_can_create_new_account(self):
        rv = self.app.post('/register', data=dict(
            email='barfyq',
            password='barf'))
        print rv.data
        user = session.query(User).all()
        print user
        assert user is not None






if __name__ == '__main__':
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    unittest.main()
    browser.quit()
