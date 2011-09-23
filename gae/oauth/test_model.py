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

#class TanarkyModelTest(GAETestBase):
class TanarkyModel(unittest.TestCase):
    def testSome(self):
        user = tanarky.model.User(sid=1,
                                  uid="abc",
                                  name="tanarky")
        print user
        assert True
