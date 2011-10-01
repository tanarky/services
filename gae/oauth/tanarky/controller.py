# -*- coding: utf-8 -*-
import ConfigParser, os, logging, urllib, urllib2, time, hmac, cgi, Cookie, email,math

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from django.utils import simplejson

import tanarky
import tanarky.oauth
import tanarky.cookie
import tanarky.model

class PageBase(webapp.RequestHandler):
  def get_oauth_client(self, name):
    if name == "twitter":
      tw_appid   = tanarky.config.get("twitter_test", "app_id")
      tw_secret  = tanarky.config.get("twitter_test", "app_secret")
      return tanarky.oauth.TwitterClient(tw_appid,
                                         tw_secret,
                                         self.request.path_url)
    return None

  def decode_u_cookie(self):
    return tanarky.cookie.User().decode(self.request.cookies.get("U"))
  def get_tmpl_path(self, name):
    return os.path.join(os.path.dirname(__file__),
                        'templates/%s.html' % name)

class PageTest(PageBase):
  def get(self):
    user = self.decode_u_cookie()
    if user == None:
      self.redirect("/");

    self.response.out.write('ok')
    return

class PageResult(PageBase):
  def get(self):
    user = self.decode_u_cookie()
    if user == None:
      self.redirect("/");

    tmpl_vars = {}
    tmpl_vars["name"] = user["name"]
    path = os.path.join(os.path.dirname(__file__),
                        'templates/result.html')
    self.response.out.write(template.render(path,
                                            tmpl_vars))
    return

class PageChallenge(PageBase):
  def get(self):
    user = self.decode_u_cookie()
    if user == None:
      self.redirect("/");
    else:
      tmpl_vars = {}
      tmpl_vars["name"] = user["name"]
      path = os.path.join(os.path.dirname(__file__),
                          'templates/challenge.html')
      self.response.out.write(template.render(path,
                                              tmpl_vars))
    return

class PageReject(PageBase):
  def get(self):
    user = self.decode_u_cookie()
    if user == None:
      self.redirect("/");

    # do something
    self.redirect("/");
    return

class PageTwitter(PageBase):
  def get(self):
    # 
    # user cookie check
    # 
    user = self.decode_u_cookie()
    if user == None:
      self.redirect("/");

    #
    # 必要な変数定義
    #
    helper = tanarky.Helper()
    client = self.get_oauth_client("twitter")

    friend_uids_key = "friend_uids_twitter_%s" % user["twitter_uid"]
    fids = memcache.get(friend_uids_key)
    user_model = None
    if fids == None:
      user_model = helper.get_user_by_twitter_uid(user["twitter_uid"])
      if user_model == None:
        self.redirect("/logout");
        return

      res = client.make_request("https://api.twitter.com/1/friends/ids.json",
                                token=user_model.twitter_token,
                                secret=user_model.twitter_secret,
                                additional_params={"user_id":user["twitter_uid"]},
                                protected=True)
      fids = simplejson.loads(res.content)
      memcache.set(friend_uids_key,
                   fids,
                   int(tanarky.config.get("cache", "friend_uids")))
    else:
      logging.debug("friend_ids cache hit.")

    try:
      page = int(self.request.get("page", "1"))
      if page < 1:
        page = 1
    except ValueError:
      logging.debug("value error")
      page = 1

    need_ids = fids[(10*(page-1)):(10*page)]
    logging.debug(need_ids)
    profs    = []
    no_ids   = []
    for i in need_ids:
      prof_key = "prof_twitter_%s" % i
      prof = memcache.get(prof_key)
      if prof == None:
        no_ids.append(str(i))
      else:
        profs.append(prof)

    f = []
    if len(no_ids) == 0:
      logging.debug("all ids cache hit.")
      f = profs
    else:
      logging.debug("no cache about these ids. %s" % no_ids)
      if user_model == None:
        user_model = helper.get_user_by_twitter_uid(user["twitter_uid"])

      response = client.make_request("https://api.twitter.com/1/users/lookup.json",
                                     token=user_model.twitter_token,
                                     secret=user_model.twitter_secret,
                                     additional_params={"user_id":",".join(no_ids),
                                                        "include_entities":"0"},
                                     protected=True)
      r = simplejson.loads(response.content)
      cache_dic = {}
      for ff in r:
        logging.debug(ff)
        cache_val = {"img":ff["profile_image_url"],
                     "id":str(ff["id"]),
                     "name":ff["name"],
                     "screen_name":ff["screen_name"],
                     "desc":ff["description"]}
        f.append(cache_val)
        cache_key = "prof_twitter_%s" % ff["id"]
        cache_dic[cache_key] = cache_val
      memcache.set_multi(cache_dic,
                         int(tanarky.config.get("cache", "user_prof")))

    paging = {"current":page,
              "navi":[page],
              "hits":len(fids)}
    paging["max"] = int(math.ceil(float(len(fids))/10))

    if page > 1:
      paging["prev"] = page - 1

    if page < paging["max"]:
      paging["next"] = page + 1

    for x in range(1,5):
      if page - x > 0:
        paging["navi"].insert(0,page-x)
      if page + x <= paging["max"]:
        paging["navi"].append(page+x)

    logging.debug(paging)

    tmpl_vars = {}
    tmpl_vars["paging"]  = paging
    tmpl_vars["name"]    = user["name"]
    tmpl_vars["friends"] = f
    path = os.path.join(os.path.dirname(__file__),
                        'templates/twitter.html')
    self.response.out.write(template.render(path,
                                            tmpl_vars))
    return

class PageFacebook(PageBase):
  def get(self):
    user = self.decode_u_cookie()
    if user == None:
      self.redirect("/");

    tmpl_vars = {}
    tmpl_vars["name"] = user["name"]
    tmpl_vars["friends"] = range(0,10)
    path = os.path.join(os.path.dirname(__file__),
                        'templates/facebook.html')
    self.response.out.write(template.render(path,
                                            tmpl_vars))
    return

class PageHome(PageBase):
  def get(self):
    user = self.decode_u_cookie()
    tmpl_vars = {}

    if user == None:
      tmpl_path = self.get_tmpl_path('guest')
      tmpl_vars["name"] = "ゲスト"
    else:
      tmpl_path = self.get_tmpl_path('home')
      tmpl_vars["name"]    = user["name"]
      tmpl_vars["friends"] = range(0,10)

    self.response.out.write(template.render(tmpl_path,tmpl_vars))
    return

class LoginTwitter(PageBase):
  def get(self):
    c = tanarky.cookie.User()

    client        = self.get_oauth_client("twitter")
    auth_token    = self.request.get("oauth_token")
    auth_verifier = self.request.get("oauth_verifier")

    if not auth_token:
      return self.redirect(client.get_authorization_url())

    prof = client.get_user_info(auth_token,auth_verifier)

    # login成功
    logging.debug(prof)

    user_model = tanarky.model.User(
      sid  = 2,
      uid  = unicode(prof["id"]),
      name = unicode(prof["username"]),
      twitter_uid    = unicode(prof["id"]),
      twitter_token  = unicode(prof["token"]),
      twitter_secret = unicode(prof["secret"]),
      )
    user_model.put()

    user = {
      "main_sid": 2,
      "name" : unicode(prof["username"]),
      "twitter_uid": unicode(prof["id"])
      }
    cookie_str = c.encode(**user)
    logging.debug(cookie_str)
    c.set(value=cookie_str,
          headers=self.response.headers._headers)
    self.redirect("/twitter")

class LoginFacebook(webapp.RequestHandler):
  def get(self):
    user = {
      "main_sid": 1,
      #"name":"たなか",
      "name":u"たなか",
      #"name":"tanarky",
      "facebook_uid": "12345",
      "yahoocom_uid": "foobar",
      }
    c = tanarky.cookie.User()
    cookie_str = c.encode(**user)
    c.set(value=cookie_str,
          headers=self.response.headers._headers)
    self.redirect("/facebook");

class Logout(PageBase):
  def get(self):
    c = tanarky.cookie.User()
    c.set(value = "",
          name  = "U",
          expires_in = -1 * 86400,
          headers=self.response.headers._headers)
    self.redirect("/");

class Error(PageBase):
  def get(self):
    self.error(404)
    self.response.out.write('error')

