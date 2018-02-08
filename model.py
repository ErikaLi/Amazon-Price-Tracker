from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of price tracking website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    fname = db.Column(db.String(64), nullable=False)
    lname = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(16), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "\n<User user_id={} email={}>".format(self.user_id,
                                                     self.email)


class Product(db.Model):
    """Information of a certain product."""

    __tablename__ = "products"

    # The ASIN of the item, a 10 character string that uniquely defines a product
    # the user has to pass it in
    product_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    # have to use regex to grab asin
    asin = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(500), nullable=True)
    #category = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "\n<Product product_id={} name={}>".format(self.product_id,
                                                          self.name)
    # image_url = db.Column(db.String(64), nullable=True)


class UserProduct(db.Model):
    """Middle table of users and products that stores price threshold
    and added date of user for a certain product."""

    __tablename__ = 'userproducts'

    userproducts_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    original_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    threshold = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    user = db.relationship('User', backref='userproducts')
    product = db.relationship('Product', backref='userproducts')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "\n<Threshold user_id={} product_id={} threshold={}>".format(self.user_id, self.product_id, self.threshold)



# only use to implement visualizations for price history
# class Price(db.Model):
#     """A table that keeps track of price history of all products, each product may have multiple pricing history entries."""
#     __tablename__ = 'prices'

#     price_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
#     time = db.Column(db.DateTime, nullable=False)
#     price = db.Column(db.Integer, nullable=False)
#     product = db.relationship('Product', backref='prices')

#     def __repr__(self):
#         """Provide helpful representation when printed."""

#         return "\n<Price price_id={} product_id={} price={}>".format(self.price_id,
#                                                                      self.product_id, self.price)


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///tracker'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    db.create_all()
    print "Connected to DB."