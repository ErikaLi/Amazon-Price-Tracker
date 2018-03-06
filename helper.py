import re
import bcrypt
from amazon.api import AmazonAPI
import os

access_key = os.environ['Access_Key']
secret_key = os.environ['Secret_Key']
associate_tag = "mobilead0cd46-20"

# product lookup
amazon = AmazonAPI(access_key, secret_key, associate_tag)

def get_item_info(asin):
    """Call Amazon API to get product info using asin."""
    product = amazon.lookup(ItemId=asin)
    return {"price": product.price_and_currency[0],
    'title': product.title,
    'image_url': product.large_image_url,
    'category': product.brand

    }
    # print product.price_and_currency
    # print product.title
    # print product.availability
    # print product.large_image_url

# def search_by_keywords(title, n=2):
#     products = amazon.search_n(n, Keywords=title, SearchIndex='All')
#     return products


def get_similar_item(asin, price):
    """Call Amazon API to get similar products but of lower prices."""
    products = amazon.similarity_lookup(ItemId=asin)
    cheaper = [product for product in products if product.price_and_currency[0] < price]
    if len(cheaper) > 3:
        return cheaper[:3]
    return cheaper


def get_asin(string):
    """ Get ASIN string from Amazon url
    >>> get_asin("https://www.amazon.com/Amazon-Echo-Show-Alexa-Enabled-Black/dp/B01J24C0TI/ref=br_msw_pdt-5?_encoding=UTF8&smid=ATVPDKIKX0DER&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=&pf_rd_r=FBTRTYTVP97H1R7Y5NCR&pf_rd_t=36701&pf_rd_p=60c4776a-4178-4e76-81d3-5620b07a5e78&pf_rd_i=desktop")
    'B01J24C0TI'

    >>> get_asin('https://www.amazon.com/Mxson-Sneakers-Lightweight-Breathable-Walking/dp/B074QN2TSS/ref=sr_1_1?s=amazon-devices&ie=UTF8&qid=1518039592&sr=8-1&keywords=shoes')
    'B074QN2TSS'


    >>> get_asin("https://www.amazon.com/Guess-Seductive-2-5-EDT-Spray/dp/B0041FXETY/ref=sr_1_2?s=apparel&ie=UTF8&qid=1518039638&sr=1-2&nodeID=7141123011&psd=1&keywords=perfume&th=1")
    'B0041FXETY'

    """

    #/gp/product/B00JM5GW10/re
    m = re.search(r'(/dp/)[a-zA-Z0-9_]{10}(/)', string)
    if m:
        return m.group()[4:-1]
    else:
        m = re.search(r'(gp/product/)[a-zA-Z0-9_]{10}(/)', string)
        if m:
            return m.group()[11:-1]
        else:
            m = re.search(r'(/dp/)[a-zA-Z0-9_]{10}(\?)', string)
            if m:
                return m.group()[4:-1]
            else:
                return None


def phone_check(phone_num):
    """Check the format of phone number."""
    return phone_num.isdigit() and len(phone_num) == 10


def password_match(p1, p2):
    """Check that the two passwords matched."""
    return p1 == p2


def validate_password(password_entered, real_password):
    """Validate the password user entered matches the password in database."""
    entered = password_entered.encode('utf-8')
    real = real_password.encode('utf-8')
    return bcrypt.checkpw(entered, real)


def encrypt(password):
    """encrypt password using the bcrypt library in python."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


# https://stackoverflow.com/questions/16709638/checking-the-strength-of-a-password-how-to-check-conditions
def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"\W", password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error )

    return password_ok