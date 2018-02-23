import re
import bcrypt


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