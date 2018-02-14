from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import (Flask, render_template, redirect, request, flash,
                   session, jsonify)

from model import User, Product, UserProduct, db, connect_to_db

from amazon_web_scrape import parse, get_asin

import datetime

import bcrypt


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

    email = request.form.get('email')
    password = request.form.get('password')
    password1 = request.form.get('password1')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    current_user = User.query.filter(User.email == email).first()

    if current_user:
        flash("This email is already in use. Please log in to your account.")
        return redirect("/login")
    else:
        if password == password1:
            password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            current_user = User(email=email, password=password, fname=fname, lname=lname)
            db.session.add(current_user)
            db.session.commit()
            flash("Successfully registered! Log in to your account now.")
            return redirect("/login")
        else:
            # use AJAX to do this
            flash("The password you entered did not match, try again.")
            return redirect("/register")



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
        flash("Invalid log in, please try again or register as a new user.")
        return redirect("/")


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

    # impose that threshold must be less than or equal to price by setting max
    # in html, example: https://www.w3schools.com/html/html_form_input_types.asp
    url = request.form.get('url')
    threshold = request.form.get('threshold')

    # get item info from url
    # may want to display image later
    item_info = parse(str(url))
    # may not be the most stable case for handling none error
    if item_info.get('SALE_PRICE') == None:
        flash("The url you entered is not in the right format, please try again.")
        return redirect("/add_item")
    name = item_info.get('NAME')
    price = float(item_info.get('SALE_PRICE')[1:])
    url = item_info.get("URL")
    asin = get_asin(url)
    image = item_info.get("image_url")

    current_prod = Product.query.filter(Product.asin == asin).first()
    timestamp = datetime.datetime.now()

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

    new_threshold = request.form.get('new_threshold')
    prod_id = request.form.get("product_id")

    if not new_threshold:
        flash("This field cannot be empty")
        return redirect("/watchlist")
    
    current_userproduct = UserProduct.query.filter_by(product_id=prod_id, user_id=session.get("user_id")).first()
    current_userproduct.threshold = new_threshold
    db.session.commit()
    flash("Your wanted price has been successfully updated!")
    return redirect("/watchlist")



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
    flash("The item is successfully removed from your list!")
    return redirect("/watchlist")

@app.route("/profile", methods=["GET"])
def display_profile():
    """Display the profile page of a particular user based on the user_id in current session."""

    if not session.get('user_id'):
        return redirect("/")

    user = User.query.get(session.get('user_id'))
    return render_template("profile.html", user=user)

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
    pop the current_user from session, and redirect to signin page."""

    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    new_password1 = request.form.get("new_password1")

    # consider writing a separate function to validate the password
    # a separate function to confirm that the two new passwords matched.
    user = User.query.get(session.get("user_id"))
    if not bcrypt.checkpw(old_password.encode('utf-8'), user.password.encode('utf-8')):
        session.pop("user_id")
        flash("The password you entered is incorrect. Please sign in again.")
        return redirect("/login")
    elif new_password != new_password1:
        # use JS or AJAX to do this
        flash('The passwords you entered did not match, please try again.')
        return redirect("/change_password")
    else:
        user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        db.session.commit()
        session.pop("user_id")
        flash("Your password is successfully reset, please sign in again.")
        return redirect("login")


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