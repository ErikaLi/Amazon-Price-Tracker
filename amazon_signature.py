#https://associates-amazon.s3.amazonaws.com/signed-requests/helper/index.html
import requests
r = requests.get("http://ecs.amazonaws.com/onca/xml?AWSAccessKeyId=AKIAIWGMBIUM6R76HQ6Q&AssociateTag=mobilead0cd46-20&ItemId=B075XWFGT7&Operation=ItemLookup&Service=AWSECommerceService&Timestamp=2018-02-20T21%3A49%3A11.000Z&Version=2013-10-15&Signature=I2zjbMUeBpOMlZJnvB5ReG%2FfY8o9cG020rNNnn5pMiA%3D")
print r.text