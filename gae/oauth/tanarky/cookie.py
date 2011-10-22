# -*- coding: utf-8 -*-
import os, logging, urllib, urllib2, time, hmac, cgi, Cookie, email, hashlib

import tanarky

"""
* params
1. signature : string
2. version   : float
3. main_sid  : int
4. name      : unicode
5. uid1      : string
6. uid2      : string
7. uid3      : string
8. uid4      : string
9. uid5      : string

* format
signature:version|main_sid|name|uid1|uid2|uid3|uid4|uid5..

1 = facebook
2 = twitter
3 = yahoo.com
4 = yahoo.co.jp
5 = mixi.jp
"""

class Base(object):

  def decode(self,rawstr):
    if rawstr == None:
      return None

    if isinstance(rawstr, str):
      rawstr = rawstr.decode('utf-8')

    if not isinstance(rawstr, unicode):
      return None

    #
    # signature check
    #
    params = rawstr.split(":",1)
    if len(params) != 2:
      return None

    signature = params[0]
    body      = params[1]
    hash = hmac.new(tanarky.config.get("cookie","secret"),
                    digestmod=hashlib.sha1)
    hash.update(body)
    if hash.hexdigest() != signature:
      return None

    #
    # version check
    #
    if body[0:2] == "1.":
      logging.debug("version1")
      return self.decode_version1(body)
    else:
      logging.debug("version none")
      return None

  def set(self, value, headers, expires_in=None):
    if expires_in == None:
      expires_in = self.expires_in

    cookie = Cookie.BaseCookie()
    cookie[self.name]            = value
    cookie[self.name]["path"]    = self.path
    cookie[self.name]["expires"] = email.utils.formatdate(
      time.time()+expires_in,
      localtime=False,
      usegmt=True)
    headers.append(("Set-Cookie", cookie.output()[12:]))
    return True

  def clear(self, headers):
    self.set(value = "",
             expires_in = -1 * 86400,
             headers=headers)
    return True

class Message(Base):
  def __init__(self):
    self.name    = "M"
    self.path    = "/"
    self.expires_in = 900
    self.version = float(tanarky.config.get("cookie", "version"))

  def decode_version1(self,rawstr):
    params  = rawstr.split("|")
    version = float(params[0])
    #body    = urllib.unquote(unicode(params[1]).encode('utf-8')).decode('utf-8')
    body    = urllib.unquote(params[1].encode('utf-8')).decode('utf-8')
    return {"version":version,
            "body":body}

  def encode(self,**params):
    if not params.has_key("body"):
      return None
    if isinstance(params["body"], str):
      params["body"] = params["body"].decode('utf-8')
    if not isinstance(params["body"], unicode):
      return None

    vals = []
    vals.append(str(self.version))
    vals.append(urllib.quote(params["body"].encode('utf-8')).decode('utf-8'))

    value = "|".join(vals)
    hash  = hmac.new(tanarky.config.get("cookie","secret"),
                     digestmod=hashlib.sha1)
    hash.update(value)
    return "%s:%s" % (hash.hexdigest(), value)


class User(Base):
  def __init__(self):
    self.name     = "U"
    self.path     = "/"
    self.expires_in = 30*36400
    self.services = ["facebook","twitter","yahoocom","yahoojp","mixi"]
    self.version  = float(tanarky.config.get("cookie", "version"))

  def get(self, key, default=None):
    if isinstance(self.value, dict) and self.value.has_key(key):
      return self.value[key]
    else:
      return default

  def decode_version1(self,rawstr):
    #
    # parameters check
    #
    params = rawstr.split("|")
    if len(params) != (len(self.services) + 3):
      logging.debug("cookie version 1 len error")
      return None

    version = float(params[0])
    if version < self.version:
      logging.debug("cookie version 1 min version error")
      return None

    main_sid = int(params[1])
    name     = params[2]
    uids     = params[3:]

    #
    # uids value check
    #
    if len(uids) != len(self.services):
      logging.debug("cookie version 1 service num error")
      return None

    #
    # value check
    #
    ret = { "version": version }
    ret["main_sid"] = main_sid
    ret["name"] = urllib.unquote(name.encode('utf-8')).decode('utf-8')

    for i in range(0,len(self.services)):
      key = "uid%d" % (i + 1)
      if uids[i] != "":
        ret[key] = uids[i]

    ret["main_uid"] = ret["uid%d" % ret["main_sid"]]
    return ret

  def encode(self,**params):
    if not params.has_key("name"):
      return None
    if isinstance(params["name"], str):
      params["name"] = params["name"].decode('utf-8')
    if not isinstance(params["name"], unicode):
      return None
    if not isinstance(params["main_sid"],int):
      return None

    vals = []
    vals.append(str(self.version))
    vals.append(str(params["main_sid"]))
    vals.append(urllib.quote(params["name"].encode('utf-8')).decode('utf-8'))

    for i in range(0,len(self.services)):
      key = "uid%d" % (i+1)

      if params.has_key(key):
        if isinstance(params[key], str):
          params[key] = params[key].decode('utf-8')
        if isinstance(params[key], unicode):
          vals.append(params[key])
        else:
          vals.append("")
      else:
        vals.append("")

    value = "|".join(vals)
    hash  = hmac.new(tanarky.config.get("cookie","secret"),
                     digestmod=hashlib.sha1)
    hash.update(value)

    return "%s:%s" % (hash.hexdigest(), value)

    

      
