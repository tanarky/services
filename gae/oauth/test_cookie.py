import unittest,logging

import tanarky.cookie

class TanarkyTestCase(unittest.TestCase):
    def testBuildAndParse1(self):
        user = {
            "main_sid": 1,
            "name": "tanarky",
            "uid1": "fb",
            "uid3": "yc",
            }
        c = tanarky.cookie.User()
        cookie_str = c.encode(main_sid=user["main_sid"],
                              name=user["name"],
                              uid1=user["uid1"],
                              uid3=user["uid3"])
        logging.info(cookie_str)
        cookie_dic = c.decode(cookie_str)

        assert cookie_dic != None
        #assert cookie_dic["facebook_uid"] == user["facebook_uid"]
        #assert cookie_dic["name"] == user["name"]
        #assert cookie_dic["version"] == 1
        #assert cookie_dic["main_sid"] == 1

    #def testBuildAndParse2(self):
    #    user = {
    #        "main_sid": "string not allowed",
    #        "facebook_uid": "12345",
    #        "yahoocom_uid": "foobar",
    #        }
    #    c = tanarky.cookie.User()
    #    cookie_str = c.build(user)
    #    logging.info(cookie_str)
    #
    #    assert cookie_str == None
    #    assert c.parse(cookie_str) == False
    #    assert c.value == None
    #    assert c.version == None

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()

