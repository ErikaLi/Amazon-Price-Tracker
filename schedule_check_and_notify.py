from model import Product, Userproduct, User, db, connect_to_db
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

def notify(user_id, product_id_lst):
    """Send notification(email or text) to users
    containing info about products that drops below threshold."""
    curr_user = User.query.get(user_id)
    email = curr_user.email
    # phone = curr_user.phone
    # use email library to send email to user regarding their products
    


def check_price(user_id):
    """For each product of user of user_id, check its current price.
    If its current price is below the wanted price of the user,
    save the product_id to a list."""
    # get all userproducts of this user
    # for each userproduct, check the product price in the products table
    # and compare the price to the wanted price in the userproduct table

    # initialize a list of underpriced products
    underpriced_product_id = []

    # join userproducts table and products table
    prods = db.session.query(Userproduct.threshold,
                             Product.price,
                             Product.product_id).join(Product).filter(Userproduct.user_id==user_id).all()

    for threshold, price, product_id in prods:
        if price < threshold:
            underpriced_product_id.append(product_id)
    return underpriced_product_id


def check_and_notify():
    """Right after the update, check if the price of items that users
    are watching falls below their threshold and send email/SMS to notify 
    them."""
    # get all userproduct group by user
    # compare each product and save any item that falls below threshold
    # email users if the list is not empty
    all_users = User.query.all()
    for user in all_users:
        product_id_lst = check_price(user.user_id)
        if product_id_lst:
            notify(user_id, product_id_lst)


schedule.every(10).minutes.do(check_and_update_price)


while True:
    schedule.run_pending()
    time.sleep(1)



