# coding: utf-8
from google.appengine.ext import db

class Seller(db.Expando):
    # アカウント 半角英数のみ
    name    = db.StringProperty(required=True)
    # 店舗名 utf-8文字列可
    title   = db.StringProperty(required=False, default='')
    # 0=Hidden, 1=Opened, 2=Deactivated
    status  = db.IntegerProperty(required=True)
    desc    = db.TextProperty(required=False)
    # 店舗画像 1=jpg, 2=png, 3=gif
    image   = db.IntegerProperty(required=False, default=0)

    # 取扱通貨 0=Yen, 1=Doller
    currency= db.IntegerProperty(required=False, default=0)

    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

class SellerAndUsers(db.Expando):
    seller = db.StringProperty(required=True)
    user   = db.StringProperty(required=True)
    # 1=Owner, 2=Member
    grant  = db.IntegerProperty(required=True)
    # 0=Created, 1=Approved, 2=Denied
    status  = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
