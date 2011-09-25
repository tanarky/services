import unittest,logging,sys

from test_base import GAETestBase

import tanarky.model
import tanarky.cookie

class TanarkyCookie(unittest.TestCase):
    def testBuildAndParse1(self):
        user = {
            "version": 1,
            "main_sid": 1,
            "facebook_uid": "12345",
            "yahoocom_uid": "foobar",
            }
        c = tanarky.cookie.User()
        cookie_str = c.build(user)
        logging.info(cookie_str)

        assert c.parse(cookie_str)
        assert c.value != None
        assert c.version == 1
        assert c.get("main_sid") == 1
        assert c.get("facebook_uid") == user["facebook_uid"]

class TanarkyModel(unittest.TestCase):
    def testSome(self):
        sid  = 1
        uid  = "abc"
        name = "tanarky"
        key  = str(sid) + uid
        user1 = tanarky.model.User(
            key_name=key,
            sid=sid,
            uid=uid,
            name=name)
        assert user1.put()
        user2 = tanarky.model.User.get_by_key_name(key)
        assert user2.sid == sid

