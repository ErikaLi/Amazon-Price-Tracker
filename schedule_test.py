from unittest import TestCase
from model import User, Product, UserProduct, db, connect_to_db, example_data
from server import app
from flask import session
from schedule_check_and_notify import (check_and_update_price, notify, 
                                        check_price, check_and_notify)

class FlaskTestsDatabase(TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""
        db.session.close()
        db.drop_all()

    # def test_check_price(self):
    #     old_price = Product.query.filter(Product.asin=='B06XKNYYWY').first().price
    #     check_and_update_price()
    #     new_price = Product.query.filter(Product.asin=='B06XKNYYWY').first().price
    #     self.assertNotEqual(old_price, new_price)

    def test_check_and_notify(self):
        user_id_lst = check_and_notify()
        self.assertEqual(user_id_lst, [1, 2])


if __name__ == "__main__":
    import unittest

    unittest.main()