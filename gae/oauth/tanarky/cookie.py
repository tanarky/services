# -*- coding: utf-8 -*-
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
    self.services = ["facebook","twitter","yahoocom","yahoojp","mixi"]
    self.version  = float(tanarky.config.get("cookie", "version"))

  def get(self, key, default=None):
    if isinstance(self.value, dict) and self.value.has_key(key):
      return self.value[key]
    else:
      return default

  def decode(self,rawstr):
    if rawstr == None:
      return None

    if isinstance(rawstr, str):
      rawstr = rawstr.decode('utf-8')

    if isinstance(rawstr, unicode) and rawstr[0:2] == "1.":
      logging.debug("version1")
      return self.decode_version1(rawstr)
    else:
      logging.debug("version none")
      return None

  def decode_version1(self,rawstr):
    # parameters check
    params = rawstr.split(":",2)
    if len(params) != 3:
      return None

    version   = float(params[0])
    if version < self.version:
      return None

    signature = params[1]
    body      = params[2]
    uids      = body.split("|")
    #logging.info(uids)

    # uids value check
    if len(uids) != len(self.services) + 2: # +2 is (main_sid,name)
      return None

    # signature check
    hash = hmac.new(tanarky.config.get("cookie","secret"),
                    digestmod=hashlib.sha1)
    hash.update(body)
    if hash.hexdigest() != signature:
      return None

    # value check
    ret = { "version": version }
    main_sid = uids.pop(0)
    #logging.debug(uids)
    #logging.debug(main_sid)
    try:
      ret["main_sid"] = int(main_sid)
    except ValueError:
      return None

    # name check
    name = uids.pop(0)
    logging.debug(type(name))
    ret["name"] = urllib.unquote(name.encode('utf-8')).decode('utf-8')
    logging.debug(type(ret["name"]))

    for i in range(0,len(self.services)):
      try:
        key = "%s_uid" % self.services[i]
        if uids[i] != "":
          ret[key] = uids[i]
      except IndexError:
        return None

    return ret

  """
  def encode2(self,params={}):
    if self.version == None or self.version != 1:
      return None

    vals = []
    if params.has_key("main_sid") and isinstance(params["main_sid"],int):
      vals.append(str(params["main_sid"]))
    else:
      return None

    for service in self.services:
      key = "%s_uid" % service
      if params.has_key(key) and isinstance(params[key], str):
        vals.append(params[key])
      else:
        vals.append("")
    value = "|".join(vals)
    hash = hmac.new(tanarky.config.get("cookie","secret"),
                    digestmod=hashlib.sha1)
    hash.update(value)
    return ":".join([str(self.version), hash.hexdigest(), value])
  """

  def encode(self,**params):
    #if self.version == None or self.version != 1.0:
    #  return None

    vals = []
    if isinstance(params["main_sid"],int):
      vals.append(str(params["main_sid"]))
    else:
      return None

    if not params.has_key("name"):
      return None

    name = params["name"]
    if isinstance(name, str):
      name = name.decode('utf-8')
    if isinstance(name, unicode):
      name = urllib.quote(name.encode('utf-8')).decode('utf-8')
    logging.debug(name)
    logging.debug(type(name))
    vals.append(name)

    for service in self.services:
      key = "%s_uid" % service
      if params.has_key(key) and isinstance(params[key], unicode):
        vals.append(params[key])
      else:
        vals.append("")
    value = "|".join(vals)
    hash = hmac.new(tanarky.config.get("cookie","secret"),
                    digestmod=hashlib.sha1)
    hash.update(value)
    return ":".join([str(self.version), hash.hexdigest(), value])

  def set(self, value, headers, name="U", path="/", expires_in=30*36400):
    cookie = Cookie.BaseCookie()
    cookie[name]            = value
    cookie[name]["path"]    = path
    cookie[name]["expires"] = email.utils.formatdate(time.time()+expires_in,
                                                     localtime=False,
                                                     usegmt=True)
    headers.append(("Set-Cookie", cookie.output()[12:]))
    return True
    

      
