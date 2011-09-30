# -*- coding: utf-8 -*-
import ConfigParser, os, logging, urllib, urllib2, time, hmac, cgi, Cookie, email,math

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from django.utils import simplejson

import tanarky
import oauth
import tanarky.cookie
import tanarky.model

class PageTest(webapp.RequestHandler):
  def get(self):
    c = tanarky.cookie.User()
    user = c.decode(self.request.cookies.get("U"))
    if user == None:
      self.redirect("/");
      return
    self.response.out.write('ok')
    return


class PageResult(webapp.RequestHandler):
  def get(self):
    c = tanarky.cookie.User()
    user = c.decode(self.request.cookies.get("U"))
    if user == None:
      self.redirect("/");
    else:
      tmpl_vars = {}
      tmpl_vars["name"] = user["name"]
      path = os.path.join(os.path.dirname(__file__),
                          'templates/result.html')
      self.response.out.write(template.render(path,
                                              tmpl_vars))
    return

class PageChallenge(webapp.RequestHandler):
  def get(self):
    c = tanarky.cookie.User()
    user = c.decode(self.request.cookies.get("U"))
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

class PageReject(webapp.RequestHandler):
  def get(self):
    c = tanarky.cookie.User()
    user = c.decode(self.request.cookies.get("U"))
    if user == None:
      self.redirect("/");
    else:
      self.redirect("/");
    return

class PageTwitter(webapp.RequestHandler):
  def get(self):
    c = tanarky.cookie.User()
    user = c.decode(self.request.cookies.get("U"))
    if user == None:
      self.redirect("/");
      return

    callback = self.request.path_url
    client   = oauth.TwitterClient(tanarky.config.get("twitter_test", "app_id"),
                                   tanarky.config.get("twitter_test", "app_secret"),
                                   callback)

    friend_uids_key = "friend_uids_twitter_%s" % user["twitter_uid"]
    fids = memcache.get(friend_uids_key)
    user_model = None

    if fids == None:
      user_model = tanarky.model.User.gql("WHERE twitter_uid = :1",
                                          user["twitter_uid"]).get()
      response = client.make_request("https://api.twitter.com/1/friends/ids.json",
                                     token=user_model.twitter_token,
                                     secret=user_model.twitter_secret,
                                     additional_params={"user_id":str(user["twitter_uid"]),
                                                        "cursor":str(-1)},
                                     protected=True)
      r = simplejson.loads(response.content)
      fids = r["ids"]
      #logging.info(fids)
      memcache.set(friend_uids_key,
                   fids,
                   int(tanarky.config.get("cache", "friend_uids")))
    else:
      logging.info("friend_ids cache hit.")

    try:
      page = int(self.request.get("page", "1"))
      if page < 1:
        page = 1
    except ValueError:
      logging.info("value error")
      page = 1

    need_ids = fids[(10*(page-1)):(10*page)]
    logging.info(need_ids)
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
      logging.info("all ids cache hit.")
      f = profs
    else:
      logging.info("no cache about these ids. %s" % no_ids)
      if user_model == None:
        user_model = tanarky.model.User.gql("WHERE twitter_uid = :1",
                                            user["twitter_uid"]).get()

      response = client.make_request("https://api.twitter.com/1/users/lookup.json",
                                     token=user_model.twitter_token,
                                     secret=user_model.twitter_secret,
                                     additional_params={"user_id":",".join(no_ids),
                                                        "include_entities":"0"},
                                     protected=True)
      r = simplejson.loads(response.content)
      cache_dic = {}
      for ff in r:
        logging.info(ff)
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

    logging.info(paging)

    tmpl_vars = {}
    tmpl_vars["paging"]  = paging
    tmpl_vars["name"]    = user["name"]
    tmpl_vars["friends"] = f
    path = os.path.join(os.path.dirname(__file__),
                        'templates/twitter.html')
    self.response.out.write(template.render(path,
                                            tmpl_vars))
    return

class PageFacebook(webapp.RequestHandler):
  def get(self):
    c = tanarky.cookie.User()
    user = c.decode(self.request.cookies.get("U"))
    if user == None:
      self.redirect("/");
    else:
      tmpl_vars = {}
      tmpl_vars["name"] = user["name"]
      tmpl_vars["friends"] = range(0,10)
      path = os.path.join(os.path.dirname(__file__),
                          'templates/facebook.html')
      self.response.out.write(template.render(path,
                                              tmpl_vars))
    return

class PageHome(webapp.RequestHandler):
  def get(self):
    c = tanarky.cookie.User()
    user = c.decode(self.request.cookies.get("U"))
    if user == None:
      name = "ゲスト"
      tmpl_vars = {}
      path = os.path.join(os.path.dirname(__file__),
                          'templates/guest.html')
      self.response.out.write(template.render(path,
                                              tmpl_vars))
    else:
      tmpl_vars = {}
      tmpl_vars["name"] = user["name"]
      tmpl_vars["friends"] = range(0,10)
      path = os.path.join(os.path.dirname(__file__),
                          'templates/home.html')
      self.response.out.write(template.render(path,
                                              tmpl_vars))
    return

class LoginTwitter(webapp.RequestHandler):
  def get(self):
    c = tanarky.cookie.User()
    user_cookie = c.decode(self.request.cookies.get("U"))
    # Cookieがあり、かつ、twitter_uidも登録済みならば、
    # することはないのでリダイレクト
    # tokenのpermissionを追加した場合などは再発行したほうがいいかも
    if user_cookie != None and user_cookie.has_key("twitter_uid"):
      logging.info("already logged in.")
      self.redirect("/twitter")

    # twitter oauth login処理(詳細はoauth.pyを参照)
    callback = self.request.path_url
    client   = oauth.TwitterClient(tanarky.config.get("twitter_test", "app_id"),
                                   tanarky.config.get("twitter_test", "app_secret"),
                                   callback)
    auth_token    = self.request.get("oauth_token")
    auth_verifier = self.request.get("oauth_verifier")
    if not auth_token:
      return self.redirect(client.get_authorization_url())
    prof = client.get_user_info(auth_token,auth_verifier)

    # login成功
    logging.info(prof)

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
    logging.info(cookie_str)
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

class Logout(webapp.RequestHandler):
  def get(self):
    c = tanarky.cookie.User()
    cookie_str = ""
    c.set(value = cookie_str,
          name  = "U",
          expires_in = -1 * 86400,
          headers=self.response.headers._headers)
    self.redirect("/");

class Error(webapp.RequestHandler):
  def get(self):
    self.error(404)
    self.response.out.write('error')

