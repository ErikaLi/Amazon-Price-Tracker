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
    password = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(16), nullable=False)

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
    price = db.Column(db.Float, nullable=False)
    # use category to give recommendations
    category = db.Column(db.String(128), nullable=True)

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
    #original_price = db.Column(db.Float, nullable=False)
    threshold = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    user = db.relationship('User', backref='userproducts')
    product = db.relationship('Product', backref='userproducts')

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "\n<Threshold user_id={} product_id={} threshold={}>".format(self.user_id, self.product_id, self.threshold)

class Recommendation(db.Model):
    """A table that contains recommended products for a user. 
    Each product in the product table has a list of recommened products."""

    __tablename__ = "recommendations"

    # use asin as primary key to avoid collision
    recommendation_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    asin = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(500), nullable=True)
    price = db.Column(db.Float, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'), nullable=False)
    product = db.relationship('Product', backref='recommendations')


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


def connect_to_db(app, link='postgresql:///tracker'):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = link
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


def example_data():
    yingying = User(fname='yingying', lname='li', email='yingying@gmail.com', password='yingyings', phone='510-520-2299')
    henry = User(fname='henry', lname='u', email='henry@gmail.com', password='henrys', phone='510-520-2299')
    chloe = User(fname='chloe', lname='u', email='chloe@gmail.com', password='chloes', phone='510-520-2299')

    watch = Product(name="Burgi Women's BUR128RD Diamond Accented Flower Dial Rose Gold & Red Leather Strap Watch",
        asin='B00ROY5VRC', 
        url='https://www.amazon.com/Burgi-BUR128RD-Diamond-Accented-Leather/dp/B00ROY5VRC/ref=pd_bxgy_241_img_2?_encoding=UTF8&pd_rd_i=B00ROY5VRC&pd_rd_r=J2PHWBRJFMJ68422KWSZ&pd_rd_w=SLDKl&pd_rd_wg=yuw9O&psc=1&refRID=J2PHWBRJFMJ68422KWSZ&dpID=416fCO-HE6L&preST=_SY300_QL70_&dpSrc=detail', 
        price=50)

    sunglasses = Product(name="SojoS Fashion Polarized Sunglasses UV Mirrored Lens Oversize Metal Frame SJ1057",
        asin='B06XKNYYWY', 
        url='https://www.amazon.com/dp/B06XKNYYWY/ref=sspa_dk_detail_1?psc=1&pd_rd_i=B06XKNYYWY&pd_rd_wg=i2ZAC&pd_rd_r=2JGB9BJ5SAGYXSD3PJQN&pd_rd_w=Pts4c', 
        price=1)

    yingying_watch = UserProduct(threshold=1000, product_id=1, user_id=1)
    henry_watch = UserProduct(threshold=30, product_id=1, user_id=2)
    henry_sunglasses = UserProduct(threshold=50, product_id=2, user_id=2)

    db.session.add_all([yingying, henry, chloe, watch, sunglasses, yingying_watch, henry_watch, henry_sunglasses])
    db.session.commit()



if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    db.create_all()
    print "Connected to DB."