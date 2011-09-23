from google.appengine.ext import db

class User(db.Expando):
    sid        = db.IntegerProperty(required=True)
    uid        = db.StringProperty(required=True)
    name       = db.StringProperty(required=True)
    parent_sid = db.IntegerProperty(required=False)
    parent_uid = db.StringProperty(required=False)
    status     = db.IntegerProperty(required=False)
    created    = db.DateTimeProperty(auto_now_add=True)
    updated    = db.DateTimeProperty(auto_now=True)

    ## expando
    ## facebook
    #facebook_id             = db.StringProperty(required=False)
    #facebook_token          = db.StringProperty(required=False)
    #has_child_id_facebook   = db.BooleanProperty(required=False)
    ## twitter
    #twitter_id              = db.StringProperty(required=False)
    #twitter_token           = db.StringProperty(required=False)
    #twitter_secret          = db.StringProperty(required=False)
    #has_child_id_twitter    = db.BooleanProperty(required=False)
    ## yahoo.com
    #yahoocom_id             = db.BlobProperty(required=False)
    #yahoocom_token          = db.BlobProperty(required=False)
    #yahoocom_secret         = db.BlobProperty(required=False)
    #yahoocom_expire_ut      = db.IntegerProperty(required=False)
    #yahoocom_auth_expire_ut = db.IntegerProperty(required=False)
    #yahoocom_session_handle = db.DateProperty(required=False)
    #has_child_id_yahoocom   = db.BooleanProperty(required=False)
    ## yahoo.co.jp
    #yahoojp_id              = db.BlobProperty(required=False)
    #yahoojp_token           = db.BlobProperty(required=False)
    #yahoojp_secret          = db.BlobProperty(required=False)
    #yahoojp_expire_ut       = db.IntegerProperty(required=False)
    #yahoojp_auth_expire_ut  = db.IntegerProperty(required=False)
    #yahoojp_session_handle  = db.DateProperty(required=False)
    #has_child_id_yahoojp    = db.BooleanProperty(required=False)
