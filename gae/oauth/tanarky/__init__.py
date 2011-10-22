# coding: utf-8
import urllib, urllib2
from django.utils import simplejson

import ConfigParser, os, logging, urllib, hmac, hashlib
import tanarky.model
import tanarky.oauth
import tanarky.facebook

#logging.info("read conf __init__")

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__),
                         'oauth.password'))

class Helper(object):
    def __init__(self):
        self.fql = "https://api.facebook.com/method/fql.query?"

    def get_main_uid(self, user_model):
        if user_model == None:
            return None

        if user_model.main_sid == 1:
            return user_model.uid1

    def get_user_by_twitter_uid(self, uid):
        return tanarky.model.get_user_by_twitter_uid(uid)

    def get_user_by_facebook_uid(self, uid):
        return tanarky.model.User.gql("WHERE uid1 = :1",uid).get()

    def get_facebook_friends_online(self, access_token, limit=10, page=1):
        offset = limit * (page - 1)
        logging.debug("%d , %d" % (limit, offset))

        query = \
            "SELECT uid, name, username, pic_square,online_presence " + \
            "FROM user WHERE uid IN " + \
            "(SELECT uid2 FROM friend WHERE uid1 = me()) " + \
            "order by online_presence limit %d offset %d" % (limit+1, offset)
        url = self.fql + urllib.urlencode({"access_token":access_token,
                                           "format":"json",
                                           "query":query})
        res = urllib2.urlopen(url).read()
        friends = simplejson.loads(res)
        for f in friends:
            f["encoded_name"] = urllib.quote(f["name"].encode('utf-8'))
            s = unicode(f["uid"]) + "=" + f["name"]
            logging.info(s)
            f["sig"] = self.get_params_signature(s)
        logging.info(friends)
        return friends

    def get_params_signature(self, msg):
        hash = hmac.new(config.get("cookie","secret"),
                        digestmod=hashlib.sha1)
        # utf-8フラグを落とす
        if isinstance(msg, unicode):
            msg = msg.encode("utf-8")
        hash.update(msg)
        return hash.hexdigest()









