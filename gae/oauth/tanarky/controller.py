# -*- coding: utf-8 -*-
import ConfigParser, os, logging, urllib, urllib2, time, hmac, cgi, Cookie, email

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from tanarky import oauth

class Home(webapp.RequestHandler):
  def get(self):
    tmpl_vars = {}
    tmpl_vars["hello"] = 'hello あいうえお %s' % oauth.get("twitter","app_id")
    path = os.path.join(os.path.dirname(__file__),
                        'templates/test.html')
    self.response.out.write(template.render(path,
                                            tmpl_vars))
    return

class Home2(webapp.RequestHandler):
  def get(self):
    self.response.out.write('hello')

