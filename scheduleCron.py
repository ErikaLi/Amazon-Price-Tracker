from model import Product, db, connect_to_db
from amazon_web_scrape import parse
from flask import Flask
import schedule
import time


app = Flask(__name__)
connect_to_db(app)


def check_and_update_price():
    """web scrape prices for all products and update price if needed."""
    products = Product.query.all()

    for product in products:
        product_info = parse(product.url)
        price = float(product_info.get('SALE_PRICE')[1:])
        if product.price != price:
            product.price = price
            db.session.commit()

def check_and notify():
    """Right after the update, check if the price of items that users
    are watching falls below their threshold and send email to notify 
    them."""

    # get all userproduct group by user
    # compare each product and save any item that falls below threshold
    # email users if the list is not empty

# def test_print():
#     print "hello world!"

# schedule.every(1).minutes.do(test_print)

schedule.every(10).minutes.do(check_and_update_price)


while True:
    schedule.run_pending()
    time.sleep(1)



