from google.appengine.ext import db

class Seller(db.Expando):
    name    = db.StringProperty(required=True)
    # 0=Hidden, 1=Opened, 2=Deactivated
    status  = db.IntegerProperty(required=True)
    desc    = db.TextProperty(required=False)
    hasImg  = db.BooleanProperty(required=False)
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

class SellerImage(db.Expando):
    name    = db.StringProperty(required=True)
    img     = db.BlobProperty
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
