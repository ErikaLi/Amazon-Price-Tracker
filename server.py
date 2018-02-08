from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from model import User, Product, UserProduct, db, connect_to_db

from amazon_web_scrape import parse, get_asin

import datetime


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

    return render_template('login.html')


@app.route('/login', methods=["POST"])
def login_process():
    """Process login form"""

    email = request.form['email']
    password = request.form['password']
    current_user = User.query.filter(User.email == email).first()

    if current_user and password == current_user.password:
        session['user_id'] = current_user.user_id
        flash("Successfully logged in!")
        return redirect("/")
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
            # maybe ask the user to see if they want to redirect to wishlist&update the info
            flash("Item has already been added, you may update your threshold in the wishlist.")
            return redirect("/wishlist")
        else:
            current_userproduct = UserProduct(original_price=price,
                                              current_price=price,
                                              threshold=threshold,
                                              product_id=current_prod.product_id,
                                              user_id=session.get("user_id"),
                                              date_added=timestamp)
            db.session.add(current_userproduct)
            db.session.commit()

    else:
        # if the item is not in the product table, add it to product table
        current_prod = Product(name=name, asin=asin, image=image, url=url)
        db.session.add(current_prod)
        db.session.commit()

        # create a userproduct entry and add it to the userproduct table
        current_userproduct = UserProduct(original_price=price,
                                          current_price=price,
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
    return redirect("/wishlist")




@app.route('/wishlist')
def display_wishlist():
    """Display wishlist of current user."""
    # get all products that this user follows
    # order by date_added

    if not session.get('user_id'):
        return redirect("/")

    userproduct_list = UserProduct.query.filter_by(user_id=session.get('user_id')).all()
    # use relationships to connect to products table and get product name and url
    for userproduct in userproduct_list:
        userproduct.product_name = userproduct.product.name
        userproduct.image = userproduct.product.image
        userproduct.url = userproduct.product.url
    # sort the wishlist by added_date


    return render_template("wishlist.html", userproducts=userproduct_list)


@app.route('/update', methods=["POST"])
def update_threshold():
    """Update user's threshold for a certain item in the wishlist."""

    new_threshold = request.form.get('new_threshold')
    prod_id = request.form.get("product_id")
    # if new_threshold is empty, redirect to wishilist
    if not new_threshold:
        flash("This field cannot be empty")
        return redirect("/wishlist")

    current_userproduct = UserProduct.query.filter_by(product_id=prod_id, user_id=session.get("user_id")).first()
    current_userproduct.threshold = new_threshold
    db.session.commit()
    flash("Your wanted price has been successfully updated!")
    return redirect("/wishlist")



@app.route('/remove', methods=["POST"])
def remove_item():
    """remove item from user's wishlist in the userproduct table
        but does not remove it from the product list.
        May want to consider that later as there are many products."""

    prod_id = request.form.get("product_id")
    current_userproduct = UserProduct.query.filter_by(product_id=prod_id, user_id=session.get("user_id")).first()
    db.session.delete(current_userproduct)
    db.session.commit()
    flash("The item is successfully removed from your list!")
    return redirect("/wishlist")

@app.route("/profile", methods=["GET"])
def display_profile():
    """Display the profile page of a particular user based on the user_id in current session."""
    
    return render_template("profile.html", )


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