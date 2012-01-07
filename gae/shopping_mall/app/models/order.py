# coding: utf-8

from google.appengine.ext import db

"""
key_name = seller + "-YYYY-mm-dd-hh-mm-ss-" + str(rand(0, 256))
"""
class Order(db.Expando):
    seller  = db.StringProperty(required=True)
    """
    content = 
    {lines:[{title:"",price:123.4,quantity:3},{},{}],
     others:[{name:"discount", price:-100.0},{}]}
    """
    cart = db.TextProperty(required=True)

    # 0=New, 1=PaymentOffered, 2=Sending, 3=Finished, 4=Canceled, 5=Pending
    status  = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
