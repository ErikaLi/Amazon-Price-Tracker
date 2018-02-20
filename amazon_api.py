# https://github.com/Saraislet/asin/blob/master/lookup.py
# https://docs.aws.amazon.com/AWSECommerceService/latest/DG/rest-signature.html
import os, sys, datetime, urllib
import hashlib, hmac, base64
import requests
import xmltodict
from amazon_web_scrape import get_asin


access_key = os.environ['Access_Key']
secret_key = os.environ['Secret_Key']
secret = secret_key.encode('utf-8')

method = "GET"
endpoint = "webservices.amazon.com"
region = 'us-east-1'
uri = "/onca/xml"
url = endpoint + uri+"?"

# Time string format (must be in UTC): 2017-11-19T20:47:19Z
t = datetime.datetime.utcnow()
amzdate = t.strftime('%Y%m%dT%H%M%SZ')
datestamp = t.strftime('%Y%m%d')
print(amzdate)
print(datestamp)


payload = {
    "Service": "AWSECommerceService",
    "Operation": "ItemLookup",
    "AWSAccessKeyId": access_key,
    "AssociateTag": "mobilead0cd46-20",
    "ItemId": "B075XWFGT7",
    #"IdType": "ASIN",
    "ResponseGroup": "Images,ItemAttributes,Offers",
    "Timestamp": datestamp,
    "Version": '2013-10-15',
    'SignatureVersion': '4',
}

request_parameters = 'AWSAccessKeyId=' + payload['AWSAccessKeyId']
request_parameters += '&AssociateTag=' + payload['AssociateTag']
request_parameters += '&ItemId=' + payload['ItemId']
request_parameters += '&Operation=' + payload['Operation']
request_parameters += '&ResponseGroup=' + payload['ResponseGroup']
request_parameters += '&Service=' + payload['Service']
request_parameters += '&SignatureVersion=' + payload['SignatureVersion']
request_parameters += '&Timestamp=' + payload['Timestamp']
request_parameters += '&Version=' + payload['Version']

msg = method + '\n'
msg += endpoint + '\n'
msg += uri + '\n'
msg += request_parameters


# def sign(key, msg):
#     return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def sign(key, msg):
    hash = hmac.new(key, msg, hashlib.sha256)
    return base64.b64encode(hash.digest())

# Sign the message
print('Message to sign: ' + msg)
signature = sign(secret, msg)
print('Signature: ' + str(signature))

msg += "&Signature=" + str(signature)
print msg


def parse_response(xml):
    # Given xml response, return dictionary of needed values.
    response = xmltodict.parse(xml.text)
    return response

payload['Signature'] = signature
r = requests.post('http://webservices.amazon.com/onca/xml?', params=payload)
print(r.text)
response = parse_response(r)


# .format(AWSAccessKeyId, ItemId, Timestamp, signature)
#request_url = 'http://webservices.amazon.com/onca/xml?AWSAccessKeyId={}&AssociateTag=mobilead0cd46-20&ItemId={}&Operation=ItemLookup&ResponseGroup=Images%2CItemAttributes%2COffers%2CReviews&Service=AWSECommerceService&Timestamp={}&Version=2013-08-01&Signature={}'.format(AWSAccessKeyId, ItemId, Timestamp, signature)


