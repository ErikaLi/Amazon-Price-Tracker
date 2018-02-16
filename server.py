from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)

from model import User, Product, UserProduct, db, connect_to_db

from amazon_web_scrape import parse, get_asin

import datetime

import bcrypt

from password_check import password_check


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

    return render_template("index.html")


@app.route('/register')
def display_registration():
    """display registration form"""

    return render_template("register.html")


@app.route('/register', methods=["POST"])
def register_process():
    """Process registration form"""

    # ask the user to reenter password and then confirm they match.
    # get info from the AJAX request in register.js
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
                   "redirect_url": "/login",
                   "empty_password": False,
                    }
        return jsonify(results)

    else:
        # if the email is new, check that they enter every field in the correct format
        # enforce phone format
        if not(phone.isdigit() and len(phone) == 10):
            results = {"message": "Please enter a 10-digit phone number without any symbol",
                       "redirect": False,
                       "empty_password": True,
                    }
            return jsonify(results)

        # check if the two passwords match
        if password == password1:
            # enforce password format using a function in password_check.py
            # if the passwords do not match, alert a message and empty out the password fields
            if not password_check(password):
                results = {"message": "Please enter a password with at least one uppercase letter, one lowercase letter, one digit, and one special character with minimum length of 8.",
                           "redirect": False,
                           "empty_password": True,
                        }
                return jsonify(results)
            # if everything is in the right format, add the user to the database
            password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            current_user = User(email=email, password=password, fname=fname, lname=lname, phone=phone)
            db.session.add(current_user)
            db.session.commit()

            results = {"message": "Successfully registered! Log in to your account now.",
                       "redirect": True,
                       "redirect_url": "/login",
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
    if not bcrypt.checkpw(old_password.encode('utf-8'), user.password.encode('utf-8')):
        session.pop("user_id")
        results = {"message": "The password you entered is incorrect, please sign in again.",
                   "redirect": True,
                   'redirect_url': '/login',
                }
        return jsonify(results)

    # if the new passwords does not match, ask them to enter again and empty out all password fields
    elif new_password != new_password1:
        # use JS or AJAX to do this
        results = {"message": "The two passwords you enter do not match, please try again.",
                    "redirect": False,
                    'empty_password': True,
                }
        return jsonify(results)

    else:
        # if the new passwords are not in the right format, empty out all passwords and ask them to try again
        if not password_check(new_password):
            results = {"message": "Please enter a password with at least one uppercase letter, one lowercase letter, one digit, and one symbol with minimum length 8.",
                       "redirect": False,
                       "empty_password": True,
                        }
            return jsonify(results)

        user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        db.session.commit()
        session.pop("user_id")
        results = {"message": 'Your password was successfully reset, please sign in using your new password.',
                    "redirect": True,
                    'redirect_url': "/login",
                }
        return jsonify(results)


@app.route('/login', methods=["GET"])
def login_form():
    """Display login form"""

    if session.get("user_id"):
        flash("Congratulations, you are already logged in!")
        return redirect("/")

    return render_template('login.html')


@app.route('/login', methods=["POST"])
def login_process():
    """Process login form"""

    email = request.form['email']
    password = request.form['password']
    current_user = User.query.filter(User.email == email).first()

    if current_user and bcrypt.checkpw(password.encode('utf-8'), current_user.password.encode('utf-8')):
        session['user_id'] = current_user.user_id
        flash("Successfully logged in!")
        return redirect("/watchlist")
    else:
        flash("Invalid log in, please try again.")
        return redirect("/login")


@app.route('/logout', methods=["GET"])
def logout_process():
    """Process logout form"""

    if session.get("user_id"):
        session.pop("user_id")
        flash("Successfully logged out!")

    return redirect("/")

@app.route('/add_item', methods=["GET"])
def display_add_item():
    """display form to add item."""

    if not session.get("user_id"):
        return redirect("/")
    return render_template("add_item.html")



@app.route('/add_item', methods=["POST"])
def add_item():
    """Add an item to the UserProduct table, and add it to the products table
    if it does not already exist. If product already exists in the Product table,
    update its price."""

    url = request.form.get('url')
    threshold = float(request.form.get('threshold'))
    # get item info from url
    item_info = parse(url)
    # may not be the most stable case for handling none error
    if item_info.get('SALE_PRICE') == None:
        flash("The url you entered is not in the right format, please try again.")
        # return render_template('add_item.html')
        return redirect("/add_item")
    name = item_info.get('NAME')
    price = float(item_info.get('SALE_PRICE')[1:])
    url = item_info.get("URL")
    asin = get_asin(url)
    image = item_info.get("image_url")


# results = { "template": render_template_as_string("/product_list")}
    ### return jsonify(results)

    current_prod = Product.query.filter(Product.asin == asin).first()
    timestamp = datetime.datetime.now()
    # use AJAX to handle this
    if threshold >= price:
        flash("Please enter a wanted price lower than the price of the product.")
        return redirect("/add_item")

    if current_prod:
        # if the product already exists in the product table, check in the
        # userproduct table if the user has added this item before

        # if the user has already added this item, update the current price
        # and ask to see if the user wants to update the threshold

        # update the date_added, set original price to current price
        # and new threshold in the userproduct table
        current_userproduct = UserProduct.query.filter_by(product_id=current_prod.product_id, user_id=session.get("user_id")).first()

        if current_userproduct:
            # maybe ask the user to see if they want to redirect to watchlist&update the info
            flash("Item has already been added, you may update your wanted price in watch list.")
            return redirect("/watchlist")
        else:
            current_userproduct = UserProduct(#original_price=price,
                                              threshold=threshold,
                                              product_id=current_prod.product_id,
                                              user_id=session.get("user_id"),
                                              date_added=timestamp)
            db.session.add(current_userproduct)
            db.session.commit()

    else:
        # if the item is not in the product table, add it to product table
        current_prod = Product(name=name, asin=asin, image=image, url=url, price=price)
        db.session.add(current_prod)
        db.session.commit()

        # create a userproduct entry and add it to the userproduct table
        current_userproduct = UserProduct(#original_price=price,
                                          threshold=threshold,
                                          product_id=current_prod.product_id,
                                          user_id=session.get("user_id"),
                                          date_added=timestamp)
        db.session.add(current_userproduct)
        db.session.commit()


    # if threshold >= price:
    # # use ajax here to ask the user to reset the price
    #     pass
    flash("Your item has been successfully added!")
    return redirect("/watchlist")




@app.route('/watchlist')
def display_watchlist():
    """Display watchlist of current user."""
    # get all products that this user follows
    # order by date_added

    if not session.get('user_id'):
        return redirect("/")

    userproduct_list = UserProduct.query.filter_by(user_id=session.get('user_id')).all()
    # use relationships to connect to products table and get product name and url
    # maybe use userproduct.product, figure out why it does not work
    for userproduct in userproduct_list:
        userproduct.product_name = userproduct.product.name
        userproduct.image = userproduct.product.image
        userproduct.url = userproduct.product.url
        userproduct.current_price = userproduct.product.price
    # sort the watchlist by added_date


    return render_template("watchlist.html", userproducts=userproduct_list)


# @app.route('/update', methods=["POST"])
# def update_threshold():
#     """Update user's threshold for a certain item in the watchlist."""

#     new_threshold = request.form.get('new_threshold')
#     prod_id = request.form.get("product_id")
#     # if new_threshold is empty, redirect to wishilist
#     if not new_threshold:
#         flash("This field cannot be empty")
#         return redirect("/watchlist")

#     current_userproduct = UserProduct.query.filter_by(product_id=prod_id, user_id=session.get("user_id")).first()
#     current_userproduct.threshold = new_threshold
#     db.session.commit()
#     flash("Your wanted price has been successfully updated!")
#     return redirect("/watchlist")

@app.route('/update', methods=["POST"])
def update_threshold():
    """Update user's threshold for a certain item in the watchlist."""

    new_threshold = float(request.form.get('new_threshold'))
    prod_id = request.form.get("product_id")

    if new_threshold >= Product.query.get(prod_id).price:
        results = {'message': "Please enter a wanted price lower than the product price.",
                    'new': False,
                    'empty': True
        }
        return jsonify(results)
    
    current_userproduct = UserProduct.query.filter_by(product_id=prod_id, user_id=session.get("user_id")).first()
    current_userproduct.threshold = new_threshold
    db.session.commit()

    results = {'message': "Your wanted price has been successfully updated!",
                'new': True,
                'new_price': new_threshold,
                'empty': False
                }
    return jsonify(results)



@app.route('/remove', methods=["POST"])
def remove_item():
    """remove item from user's watchlist in the userproduct table
        and removes it from the product list if userproduct table does not contain 
        this product_id."""

    prod_id = request.form.get("product_id")
    current_userproduct = UserProduct.query.filter_by(product_id=prod_id, user_id=session.get("user_id")).first()
    db.session.delete(current_userproduct)
    db.session.commit()
    remaining_userproduct = UserProduct.query.filter_by(product_id=prod_id).all()
    
    if not remaining_userproduct:
        current_product = Product.query.get(prod_id)
        db.session.delete(current_product)
        db.session.commit()
    result = {'message': 'You successfully deleted your item!',
                'product_id': prod_id}
    return jsonify(result)

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