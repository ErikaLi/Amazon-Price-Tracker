# use AmazonAPI for item lookup
from amazon.api import AmazonAPI
# use bottle nose for item search
# import bottlenose
# from bs4 import BeautifulSoup
import os
import re

# has cart functionalities

access_key = os.environ['Access_Key']
secret_key = os.environ['Secret_Key']
associate_tag = "mobilead0cd46-20"

# product lookup
amazon = AmazonAPI(access_key, secret_key, associate_tag)

def get_item_info(asin):
    product = amazon.lookup(ItemId=asin)
    return {"price": product.price_and_currency[0],
    'title': product.title,
    'image_url': product.large_image_url

    }
    # print product.price_and_currency
    # print product.title
    # print product.availability
    # print product.large_image_url

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
            return m.group()[4:-1]
        else:
            m = re.search(r'(/dp/)[a-zA-Z0-9_]{10}(\?)', string)
            if m:
                return m.group()[4:-1]
            else:
                return None
