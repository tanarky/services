# coding: utf-8
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
    #facebook_uid            = db.StringProperty(required=False)
    #facebook_token          = db.StringProperty(required=False)
    #has_child_id_facebook   = db.BooleanProperty(required=False)
    ## twitter
    #twitter_uid             = db.StringProperty(required=False)
    #twitter_token           = db.StringProperty(required=False)
    #twitter_secret          = db.StringProperty(required=False)
    #has_child_id_twitter    = db.BooleanProperty(required=False)
    ## yahoo.com
    #yahoocom_uid            = db.BlobProperty(required=False)
    #yahoocom_token          = db.BlobProperty(required=False)
    #yahoocom_secret         = db.BlobProperty(required=False)
    #yahoocom_expire_ut      = db.IntegerProperty(required=False)
    #yahoocom_auth_expire_ut = db.IntegerProperty(required=False)
    #yahoocom_session_handle = db.DateProperty(required=False)
    #has_child_id_yahoocom   = db.BooleanProperty(required=False)
    ## yahoo.co.jp
    #yahoojp_uid             = db.BlobProperty(required=False)
    #yahoojp_token           = db.BlobProperty(required=False)
    #yahoojp_secret          = db.BlobProperty(required=False)
    #yahoojp_expire_ut       = db.IntegerProperty(required=False)
    #yahoojp_auth_expire_ut  = db.IntegerProperty(required=False)
    #yahoojp_session_handle  = db.DateProperty(required=False)
    #has_child_id_yahoojp    = db.BooleanProperty(required=False)

## 1:1じゃんけんの結果
#class Result(db.Expando):
#    from_sid   = db.IntegerProperty(required=True)
#    from_uid   = db.StringProperty(required=True)
#    from_hands = db.ListProperty(long, required=True)
#    to_sid     = db.IntegerProperty(required=True)
#    to_uid     = db.StringProperty(required=True)
#    to_hands   = db.ListProperty(long, required=False)
#    status     = db.IntegerProperty(required=True)
#    updated    = db.DateTimeProperty(auto_now=True)
#
## 1:多じゃんけん大会情報
#class Game(db.Expando):
#    # createしたUserのMain ID
#    sid     = db.IntegerProperty(required=True)
#    uid     = db.StringProperty(required=True)
#    # じゃんけん大会名
#    title   = db.StringProperty(required=False)
#    # 
#    hands   = db.ListProperty(long, required=False)
#    created = db.DateTimeProperty(auto_now_add=True)
#
## -----------------------
#
## 1:1じゃんけんの結果
#class UserResult(db.Expando):
#    gid     = db.StringProperty(required=True)
#    sid     = db.IntegerProperty(required=True)
#    uid     = db.StringProperty(required=True)
#    hands   = db.ListProperty(long, required=True)
#    status  = db.IntegerProperty(required=True)
#    updated = db.DateTimeProperty(auto_now=True)
#
## 1:多じゃんけん大会情報
#class Game(db.Expando):
#    # createしたUserのMain ID
#    sid     = db.IntegerProperty(required=True)
#    uid     = db.StringProperty(required=True)
#    # じゃんけん大会名
#    title   = db.StringProperty(required=False)
#    # 
#    hands   = db.ListProperty(long, required=False)
#    created = db.DateTimeProperty(auto_now_add=True)






