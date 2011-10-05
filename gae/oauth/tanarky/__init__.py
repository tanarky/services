import urllib, urllib2
from django.utils import simplejson

import ConfigParser, os, logging
import tanarky.model
import tanarky.oauth
import tanarky.facebook

#logging.info("read conf __init__")

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__),
                         'oauth.password'))

class Helper():
    def __init__(self):
        self.fql = "https://api.facebook.com/method/fql.query?"

    def get_user_by_twitter_uid(self, uid):
        return tanarky.model.User.gql("WHERE uid2 = :1",uid).get()
    def get_user_by_facebook_uid(self, uid):
        return tanarky.model.User.gql("WHERE uid1 = :1",uid).get()
    def get_facebook_friends_online(self, access_token):
        query = \
            "SELECT uid, name, pic_square,online_presence FROM user "   + \
            "WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me()) " + \
            "order by online_presence limit 10"
        url = self.fql + urllib.urlencode({"access_token":access_token,
                                           "format":"json",
                                           "query":query})
        response = urllib2.urlopen(url).read()
        return simplejson.loads(response)
