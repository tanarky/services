# coding: utf-8

from google.appengine.ext import db

"""
key_name = seller + code
"""
class Product(db.Expando):
    seller  = db.StringProperty(required=True)
    code    = db.StringProperty(required=True)
    title   = db.StringProperty(required=True, default='')
    price   = db.FloatProperty(required=True)
    desc    = db.TextProperty(required=False)
    # 1=jpeg, 2=png, 3=gif
    image1  = db.IntegerProperty(required=False, default=0)
    image2  = db.IntegerProperty(required=False, default=0)
    image3  = db.IntegerProperty(required=False, default=0)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

class ProductStock(db.Expando):
    seller  = db.StringProperty(required=True)
    code    = db.StringProperty(required=True)
    quantity= db.IntegerProperty(required=True)
    updated = db.DateTimeProperty(auto_now=True)

