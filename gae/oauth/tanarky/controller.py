# -*- coding: utf-8 -*-
import ConfigParser, os, logging, urllib, urllib2, time, hmac, cgi, Cookie, email

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import tanarky.cookie

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
    else:
      tmpl_vars = {}
      tmpl_vars["name"] = user["name"]
      tmpl_vars["friends"] = range(0,10)
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
    self.redirect("/twitter");

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

