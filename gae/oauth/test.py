import unittest,logging

import tanarky.cookie

class TanarkyTestCase(unittest.TestCase):
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

    def testBuildAndParse2(self):
        user = {
            "main_sid": "string not allowed",
            "facebook_uid": "12345",
            "yahoocom_uid": "foobar",
            }
        c = tanarky.cookie.User()
        cookie_str = c.build(user)
        logging.info(cookie_str)

        assert cookie_str == None
        assert c.parse(cookie_str) == False
        assert c.value == None
        assert c.version == None

    def testBuildAndParse3(self):
        user = {
            "main_sid": "string not allowed",
            "facebook_uid": "12345",
            "yahoocom_uid": "foobar",
            }
        c = tanarky.cookie.User()
        cookie_str = c.build(user)
        logging.info(cookie_str)

        assert cookie_str == None
        assert c.parse(cookie_str) == False
        assert c.value == None
        assert c.version == None

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

