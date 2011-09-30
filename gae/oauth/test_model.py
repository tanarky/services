# coding: utf-8
import unittest,logging,sys,time

#from test_base import GAETestBase
import test_base

from google.appengine.api import memcache

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
        #c = tanarky.cookie.User()
        #cookie_str = c.build(user)
        #logging.info(cookie_str)
        #assert c.parse(cookie_str)
        #assert c.value != None
        #assert c.version == 1
        #assert c.get("main_sid") == 1
        #assert c.get("facebook_uid") == user["facebook_uid"]

class TanarkyModel(unittest.TestCase):
    def testSome(self):
        pass
        #sid  = 1
        #uid  = "abc"
        #name = "tanarky"
        #key  = str(sid) + uid
        #user1 = tanarky.model.User(
        #    key_name=key,
        #    sid=sid,
        #    uid=uid,
        #    name=name)
        #assert user1.put()
        #user2 = tanarky.model.User.get_by_key_name(key)
        #assert user2.sid == sid

class TanarkyMemcache(unittest.TestCase):
    def testMemcache(self):
        key = "abc"
        indata = {"user":123, "foo":u"あいう", "bar":["a","b"]}
        memcache.set(key, indata, time=5*60)
        outdata = memcache.get(key)
        assert outdata == indata

        key1 = "abc"
        indata1 = {"user":123, "foo":u"あいう", "bar":["a","b"]}
        key2 = "cde"
        indata2 = {"aaa":123}

        memcache.set_multi({key1:indata1, key2:indata2}, time=10)
        outdata = memcache.get_multi([key1,key2])
        assert len(outdata) == 2
        assert outdata[key1]["foo"] == u"あいう"
        assert outdata[key2]["aaa"] == 123

        memcache.set(key, indata, time=1)
        time.sleep(1)
        outdata = memcache.get(key)
        assert outdata == None
