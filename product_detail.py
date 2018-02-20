# use AmazonAPI for item lookup
from amazon.api import AmazonAPI
# use bottle nose for item search
# import bottlenose
# from bs4 import BeautifulSoup
import os

# has cart functionalities

access_key = os.environ['Access_Key']
secret_key = os.environ['Secret_Key']
associate_tag = "mobilead0cd46-20"

# product lookup
amazon = AmazonAPI(access_key, secret_key, associate_tag)
product = amazon.lookup(ItemId='B075XWFGT7')
print product.price_and_currency
print product.title
print product.availability
print product.large_image_url
