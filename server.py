from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)

from model import User, Product, UserProduct, Recommendation, db, connect_to_db

from product_detail import *

import datetime

from helper import *


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    # if this user exists, get all products that this user is watching, and find
    # recommended items related to these products
    if session.get("user_id"):
        user = User.query.get(session.get("user_id"))
        # get all recommended products for this user
        recommended = Recommendation.query.filter_by(user_id=session.get('user_id')).all()
        # recommended = user.userproducts.products.recommendations
        return render_template("index.html", name=user.fname, recommendations=recommended)

    return render_template("index.html")


@app.route('/register')
def display_registration():
    """display registration form"""

    return render_template("register.html")


@app.route('/register', methods=["POST"])
def register_process():
    """Process registration form"""
    # all of the info will be in string format
    email = request.form.get('email')
    password = request.form.get('password')
    password1 = request.form.get('password1')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    phone = request.form.get("phone")

    # check to see if the email was already in use
    current_user = User.query.filter(User.email == email).first()

    if current_user:
        # redirects them to login if the email is already in use
        results = {"message": "This email is already in use. Please log in to your account.",
                   "redirect": True,
                   "redirect_url": "/",
                   "empty_password": False,
                    }
        return jsonify(results)

    else:
        # enforce phone format
        if not phone_check(phone):
            results = {"message": "Please enter a 10-digit phone number without any symbol",
                       "redirect": False,
                       "empty_password": True,
                    }
            return jsonify(results)

        # check if the two passwords match
        if password_match(password, password1):
            # enforce password format
            if not password_check(password):
                results = {"message": "Please enter a password with at least one uppercase letter, one lowercase letter, one digit, and one special character.",
                           "redirect": False,
                           "empty_password": True,
                        }
                return jsonify(results)
            # if everything is in the right format, add the user to the database
            password = encrypt(password)
            current_user = User(email=email, password=password, fname=fname, lname=lname, phone=phone)
            db.session.add(current_user)
            db.session.commit()

            results = {"message": "Successfully registered! Log in to your account now.",
                       "redirect": True,
                       "redirect_url": "/",
                       "empty_password": False,
                    }
            return jsonify(results)

        else:
            results = {"message": "The password you entered did not match, try again.",
                       "redirect": False,
                       "empty_password": True,
                    }
            return jsonify(results)

            
@app.route("/change_password", methods=['GET'])
def display_password_form():
    """Display the form to change password, ask the user to fill in existing and 
    new passwords."""

    if not session.get('user_id'):
        return redirect("/")

    return render_template("change_password.html")


@app.route("/change_password", methods=['POST'])
def process_password_change():
    """Change the password of user if they provide the correct password,
    pop the current_user from session, and redirect to login page."""

    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    new_password1 = request.form.get("new_password1")

    user = User.query.get(session.get("user_id"))

    # if the user does not enter a correct current password, logout and redirect to login again
    if not validate_password(old_password, user.password):
        session.pop("user_id")
        results = {"message": "The password you entered is incorrect, please sign in again.",
                   "redirect": True,
                   'redirect_url': '/',
                }
        return jsonify(results)

    # if the new passwords does not match, ask them to enter again and empty out all password fields
    elif not password_match(new_password, new_password1):
        # use JS or AJAX to do this
        results = {"message": "The two passwords you enter do not match, please try again.",
                    "redirect": False,
                    'empty_password': True,
                }
        return jsonify(results)

    # if the new passwords are not in the right format, empty out all passwords and ask them to try again
    elif not password_check(new_password):
        results = {"message": "Please enter a password with at least one uppercase letter, one lowercase letter, one digit, and one special character.",
                   "redirect": False,
                   "empty_password": True,
                    }
        return jsonify(results)

    # if everything is in the right format, update password for current user and ask them to login again.
    user.password = encrypt(new_password)
    db.session.commit()
    session.pop("user_id")
    results = {"message": 'Your password was successfully reset, please sign in using your new password.',
                "redirect": True,
                'redirect_url': "/",
            }
    return jsonify(results)


# @app.route('/login', methods=["GET"])
# def login_form():
#     """Display login form"""

#     if session.get("user_id"):
#         flash("Congratulations, you are already logged in!")
#         return redirect("/")

#     return render_template('login.html')


@app.route('/login', methods=["POST"])
def login_process():
    """Process login form"""

    email = request.form['email']
    password = request.form['pw']
    current_user = User.query.filter(User.email == email).first()

    if current_user and validate_password(password, current_user.password):
        session['user_id'] = current_user.user_id
        flash("Successfully logged in!")
        return redirect("/")

    else:
        flash("Invalid log in, please try again.")
        return redirect("/")


@app.route('/logout', methods=["GET"])
def logout_process():
    """Process logout form"""

    if session.get("user_id"):
        session.pop("user_id")
        flash("Successfully logged out!")

    return redirect("/")

# @app.route('/add_item', methods=["GET"])
# def display_add_item():
#     """display form to add item."""

#     if not session.get("user_id"):
#         return redirect("/")
#     return render_template("add_item.html")



@app.route('/wishlist_add', methods=["POST"])
def add_item():
    """Add an item to the UserProduct table, and add it to the products table
    if it does not already exist. If user is already watching the item, flask
    a message and ask the user to update the wanted price in watchlist page.
    When adding an item, also add its similar items to recommendation table."""

    url = request.form.get('url')
    asin = get_asin(url)

    # if cannot find asin from url, tell user to enter a correct url
    if not asin:
        return jsonify({'message': "The url you entered is not in the right format, please try again.",
        # return render_template('add_item.html')
                "redirect": False,
                "empty": True
        })

    # user input of their wanted price
    threshold = float(request.form.get('threshold'))
    threshold = threshold

    # item info retrieve from amazon api
    item_info = get_item_info(asin) 
    name = item_info.get('title')
    price = item_info.get('price')
    price = price
    image_url = item_info.get("image_url")
    category = item_info.get("category")

    # if price is not available, item is usually free
    if not price:
        return jsonify({'message': "The item may be available for free, no need to add to watch list.",
                "redirect": False,
                "empty": True
        })


    # if the wanted price is greater than the current price of the product, ask user to enter again
    if threshold >= price:
        return jsonify({'message': "Please enter a wanted price lower than the price of the product.",
                    "redirect": False,
                    "empty_threshold": True,
                    "added": False
        })


    # get the current product from database 
    current_prod = Product.query.filter(Product.asin == asin).first()

    # content to prepend to the existing page

    # if the product already exists in the product table, check in the
        # userproduct table if the user has added this item before
    if not current_prod:
        # if the item is not in the product table, add it to product table
        current_prod = Product(name=name, asin=asin, image=image_url, url=url, price=price, category=category)
        db.session.add(current_prod)
        db.session.commit()

    current_userproduct = UserProduct.query.filter_by(product_id=current_prod.product_id, user_id=session.get("user_id")).first()
        
    # if the user has already added this item, ask them to update in the wishlist
    # maybe jump to that item and ask them to update?
    if current_userproduct:
        return jsonify({'message': "Item has already been added, you may update your wanted price in watch list.",
            "redirect": False,
            "empty": True})

    # if the user has not added this product before, add this to the userproduct table
    # if it's on the add_item route, should redirect to watchlist, else prepend content in watchlist
    else:
        timestamp = datetime.datetime.now()
        current_userproduct = UserProduct(threshold=threshold,
                                          product_id=current_prod.product_id,
                                          user_id=session.get("user_id"),
                                          date_added=timestamp)
        db.session.add(current_userproduct)
        db.session.commit()

        # if the product already exists in the recommendation table, delete it from recommendations table
        recommendation = Recommendation.query.filter_by(asin=asin, user_id=session.get("user_id")).first()
        if recommendation:
            db.session.delete(recommendation)
            db.session.commit()


        # add similar items of this product to the recommendation table
        similar_products = search_by_keywords(category)
        for similar_product in similar_products:
            # check if product already exists in the user's recommended list
            curr_similar = Recommendation.query.filter_by(asin=similar_product.asin, user_id=session.get("user_id")).first()
            # check if this recommended product is in the user's watchlist
            existence = None
            curr_prod = Product.query.filter_by(asin = similar_product.asin).first()
            if curr_prod:
                existence = UserProduct.query.filter_by(user_id=session.get("user_id"), product_id=curr_prod.product_id).first()
            if not curr_similar and not existence:
                item = Recommendation(name=similar_product.title, asin=similar_product.asin,
                                     price='{0:.2f}'.format(similar_product.price_and_currency[0]), image=similar_product.large_image_url,
                                     product_id=current_prod.product_id, url=similar_product.offer_url, user_id=session.get("user_id"))
                db.session.add(item)
                db.session.commit()

        prod_id = current_prod.product_id
        return jsonify({'message': "Item is successfully added!",
            "redirect": False,
            "empty": True,
            "added": True,
            "product_id": prod_id,
            "prod_name": current_prod.name,
            "price": float(price),
            "url": url,
            "image_url": image_url,
            'threshold': threshold
        })


@app.route('/watchlist')
def display_watchlist():
    """Display watchlist of current user."""
    # get all products that this user follows
    # order by date_added

    if not session.get('user_id'):
        return redirect("/")

    userproduct_list = UserProduct.query.filter_by(user_id=session.get('user_id')).order_by(UserProduct.date_added.desc()).all()
    # use relationships to connect to products table and get product name and url
    # maybe use userproduct.product, figure out why it does not work
    for userproduct in userproduct_list:
        userproduct.product_name = userproduct.product.name
        userproduct.image = userproduct.product.image
        userproduct.url = userproduct.product.url
        userproduct.current_price = userproduct.product.price
    # sort the watchlist by added_date


    return render_template("watchlist.html", userproducts=userproduct_list)


@app.route('/update', methods=["POST"])
def update_threshold():
    """Update user's threshold for a certain item in the watchlist."""

    new_threshold = float(request.form.get('new_threshold'))
    prod_id = request.form.get("product_id")

    if new_threshold >= Product.query.get(prod_id).price:
        results = {'message': "Please enter a wanted price lower than the product price.",
                    'valid_threshold': False,
                    'empty': True,
                    'product_id': prod_id
        }
        return jsonify(results)
    
    current_userproduct = UserProduct.query.filter_by(product_id=prod_id, user_id=session.get("user_id")).first()
    current_userproduct.threshold = new_threshold
    db.session.commit()

    results = {'message': "Your wanted price has been successfully updated!",
                'valid_threshold': True,
                'new_price': new_threshold,
                'empty': True,
                'product_id': prod_id

                }
    return jsonify(results)



@app.route('/remove', methods=["POST"])
def remove_item():
    """remove item from user's watchlist in the userproduct table
        and removes it from the product list and recommendations related to this 
        product if userproduct table does not contain this product_id."""

    prod_id = request.form.get("product_id")
    userproduct = UserProduct.query.filter_by(product_id=prod_id, user_id=session.get("user_id")).first()
    db.session.delete(userproduct)
    db.session.commit()

    # remove recommendations for this user and product combination
    recommended_products = Recommendation.query.filter_by(product_id=prod_id, user_id=session.get("user_id")).all()
    for rec in recommended_products:
        db.session.delete(rec)
        db.session.commit()

    # if no one else is watching this product, remove this product from the products table
    remaining_userproduct = UserProduct.query.filter_by(product_id=prod_id).all()
    if not remaining_userproduct:
        current_product = Product.query.get(prod_id)       
        db.session.delete(current_product)
        db.session.commit()
    result = {'message': 'You successfully deleted your item!',
                'product_id': prod_id}
    return jsonify(result)

# this requires some user reference for each recommendation so that what the user 
# is watching will not be display on the homepage.

# @app.route('/add_rec', methods=["POST"])
# def add_recommendation():
#     """add the recommended item to the product table and UserProduct table
#      if it does not alreay exist. Remove it"""

#     prod_id = request.form.get("product_id")
#     current_userproduct = UserProduct.query.filter_by(product_id=prod_id, user_id=session.get("user_id")).first()
#     db.session.delete(current_userproduct)
#     db.session.commit()
#     remaining_userproduct = UserProduct.query.filter_by(product_id=prod_id).all()
    
#     if not remaining_userproduct:
#         # remove recommendations for this product
#         current_product = Product.query.get(prod_id)
#         recommended_products = Recommendation.query.filter_by(product_id=prod_id).all()
#         for rec in recommended_products:
#             db.session.delete(rec)       
#         db.session.delete(current_product)
#         db.session.commit()
#     result = {'message': 'You successfully deleted your item!',
#                 'product_id': prod_id}
#     return jsonify(result)


@app.route("/profile", methods=["GET"])
def display_profile():
    """Display the profile page of a particular user based on the user_id in current session."""

    if not session.get('user_id'):
        return redirect("/")

    user = User.query.get(session.get('user_id'))
    return render_template("profile.html", user=user)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)
    db.create_all()

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')