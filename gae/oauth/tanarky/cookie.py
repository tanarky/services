import os, logging, urllib, urllib2, time, hmac, cgi, Cookie, email, hashlib

import tanarky

"""
* params
1. version      : int
2. signature    : string
3. main_sid     : int
4. facebook_uid : string
5. twitter_uid  : string
6. yahoocom_uid : string
7. yahoojp_uid  : string
8. mixi_uid     : string

* format
1,2,2|3|4|5|...
"""

class User():
  def __init__(self):
    self.default_version = 1
    self.services = ["facebook","twitter","yahoocom","yahoojp","mixi"]
    self.version  = None
    self.value    = None

  def get(self, key, default=None):
    if isinstance(self.value, dict) and self.value.has_key(key):
      return self.value[key]
    else:
      return default

  def parse(self,rawstr):
    if isinstance(rawstr, str) and rawstr[0:2] == "1:":
      self.version = 1
      return self.parse_version1(rawstr)
    else:
      self.clear()
      return False

  def clear(self):
    self.version = None
    self.value = None

  def parse_version1(self,rawstr):
    # parameters check
    params = rawstr.split(":",2)
    if len(params) != 3:
      self.clear()
      return False

    #version   = params[0]
    signature = params[1]
    body      = params[2]
    uids      = body.split("|")
    logging.info(uids)

    # uids value check
    if len(uids) != len(self.services) + 1: # +1 is main_sid
      self.clear()
      return False

    # signature check
    hash = hmac.new(tanarky.oauth.get("cookie","secret"),
                    digestmod=hashlib.sha1)
    hash.update(body)
    if hash.hexdigest() != signature:
      self.clear()
      return False

    # value check
    ret = {}
    main_sid = uids.pop(0)
    logging.info(uids)
    logging.info(main_sid)
    try:
      ret["main_sid"] = int(main_sid)
    except ValueError:
      self.clear()
      return False

    for i in range(0,len(self.services)):
      try:
        key = "%s_uid" % self.services[i]
        if uids[i] != "":
          ret[key] = uids[i]
      except IndexError:
        self.clear()
        return False

    self.value = ret
    return True

  def build(self, params={}):
    version = self.default_version
    if params.has_key("version"):
      if isinstance(params["version"],int):
        version = params["version"]
      else:
        return None

    vals = []
    if params.has_key("main_sid") and isinstance(params["main_sid"],int):
      vals.append(str(params["main_sid"]))
    else:
      return None

    for service in self.services:
      key = "%s_uid" % service
      if params.has_key(key):
        vals.append(params[key])
      else:
        vals.append("")
    value = "|".join(vals)
    hash = hmac.new(tanarky.oauth.get("cookie","secret"),
                    digestmod=hashlib.sha1)
    hash.update(value)
    return ":".join([str(version), hash.hexdigest(), value])

      
