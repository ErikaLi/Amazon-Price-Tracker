import os, datetime, urllib
import hashlib, hmac, base64
import requests
import xmltodict


# https://github.com/Saraislet/asin/blob/master/lookup.py
# https://docs.aws.amazon.com/AWSECommerceService/latest/DG/rest-signature.html
t = datetime.datetime.utcnow()
amz_date = t.strftime('%Y-%m-%dT%H:%M:%SZ')
amz_date_encoded = t.strftime('%Y-%m-%dT%H%%3A%M%%3A%SZ')

def get_signature(ItemId):
    AWSAccessKeyId=os.environ['AWSAccessKeyId']
    AssociateTag="mobilead0cd46-20"
    ItemId=ItemId
    Operation='ItemLookup'
    ResponseGroup='Images%2CItemAttributes%2COffers%2CReviews'
    Service='AWSECommerceService'
    Timestamp=amz_date_encoded
    Version='2013-08-01'


# .format(AWSAccessKeyId, ItemId, Timestamp, signature)
request_url = 'http://webservices.amazon.com/onca/xml?AWSAccessKeyId={}&AssociateTag=mobilead0cd46-20&ItemId={}&Operation=ItemLookup&ResponseGroup=Images%2CItemAttributes%2COffers%2CReviews&Service=AWSECommerceService&Timestamp={}&Version=2013-08-01&Signature={}'.format(AWSAccessKeyId, ItemId, Timestamp, signature)