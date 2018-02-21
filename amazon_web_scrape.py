from lxml import html
import csv
import os
import requests
from exceptions import ValueError
from time import sleep
from random import randint
import re


# have to web scrape image using scrapy

def parse(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
    }

    try:
        # Retrying for failed requests
        for i in range(20):
            # Generating random delays
            sleep(randint(1,3))
            # Adding verify=False to avold ssl related issues
            response = requests.get(url, headers=headers, verify=False)

            if response.status_code == 200:
                doc = html.fromstring(response.content)
                XPATH_NAME = '//h1[@id="title"]//text()'
                XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id, "priceblock_dealprice") or contains(@id,"saleprice")]/text()'
                XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
                XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
                XPATH_AVAILABILITY = '//div[@id="availability"]//text()'
                XPATH_IMAGE = '//div[@id="imgTagWrapperId"]//img/@src'
                XPATH_OLD_IMAGE = '//div[@id="imgTagWrapperId"]//img/@data-old-hires'

                RAW_NAME = doc.xpath(XPATH_NAME)
                RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
                RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
                RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
                RAw_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)
                RAW_IMAGE = doc.xpath(XPATH_IMAGE)
                RAW_OLD_IMAGE = doc.xpath(XPATH_OLD_IMAGE)


                NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
                SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
                CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
                ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
                AVAILABILITY = ''.join(RAw_AVAILABILITY).strip() if RAw_AVAILABILITY else None
                if RAW_OLD_IMAGE:
                    IMAGE = RAW_OLD_IMAGE[0]
                elif RAW_IMAGE:
                    IMAGE = RAW_IMAGE[0]
                else:
                    IMAGE = None
                
                if not ORIGINAL_PRICE:
                    ORIGINAL_PRICE = SALE_PRICE
                # retrying in case of captcha
                # if not NAME:
                #     raise ValueError('captcha')

                data = {
                    'NAME': NAME,
                    'SALE_PRICE': SALE_PRICE,
                    'CATEGORY': CATEGORY,
                    'ORIGINAL_PRICE': ORIGINAL_PRICE,
                    'AVAILABILITY': AVAILABILITY,
                    'URL': url,
                    'image_url':IMAGE
                }
                return data

            elif response.status_code==404:
                break

    except Exception as e:
        print e, type(e)


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
                

# if __name__ == "__main__":
#     parse("https://www.amazon.com/dp/B01J94SWWU/ref=fs_ods_tab_ds")
#     get_asin("https://www.amazon.com/dp/B01J94SWWU/ref=fs_ods_tab_ds")
