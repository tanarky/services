# coding: utf-8
from google.appengine.ext import db

class User(db.Expando):
    main_sid        = db.IntegerProperty(required=True)
    name            = db.StringProperty(required=True)
    parent_sid      = db.IntegerProperty(required=False)
    parent_uid      = db.StringProperty(required=False)
    status          = db.IntegerProperty(required=False)
    created         = db.DateTimeProperty(auto_now_add=True)
    updated         = db.DateTimeProperty(auto_now=True)

    # facebook
    uid1            = db.StringProperty(required=False)
    token1          = db.StringProperty(required=False)
    # twitter
    uid2            = db.StringProperty(required=False)
    token2          = db.StringProperty(required=False)
    secret2         = db.StringProperty(required=False)

    ## yahoo.co.jp
    #uid3             = db.BlobProperty(required=False)
    #token3           = db.BlobProperty(required=False)
    #secret3          = db.BlobProperty(required=False)
    #expire_ut3       = db.IntegerProperty(required=False)
    #auth_expire_ut3  = db.IntegerProperty(required=False)
    #session_handle3  = db.DateProperty(required=False)
    #has_child_id3    = db.BooleanProperty(required=False)

class Game(db.Expando):
    from_sid   = db.IntegerProperty(required=True)
    from_uid   = db.StringProperty(required=True)
    from_hands = db.ListProperty(int)
    from_name  = db.StringProperty(required=True)
    to_sid     = db.IntegerProperty(required=True)
    to_uid     = db.StringProperty(required=True)
    to_hands   = db.ListProperty(int)
    to_name    = db.StringProperty(required=True)
    status     = db.IntegerProperty(required=True)
    created    = db.DateTimeProperty(auto_now_add=True)
    updated    = db.DateTimeProperty(auto_now=True)

