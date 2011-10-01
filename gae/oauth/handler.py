# -*- coding: utf-8 -*-
import os
## warningが出るのでコメントアウト
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import logging
import tanarky.controller

application = webapp.WSGIApplication(
  [(r'/', tanarky.controller.PageHome),
   (r'/challenge',      tanarky.controller.PageChallenge),
   (r'/reject',         tanarky.controller.PageReject),
   (r'/result',         tanarky.controller.PageResult),
   (r'/twitter',        tanarky.controller.PageTwitter),
   (r'/facebook',       tanarky.controller.PageFacebook),
   (r'/login/twitter',  tanarky.controller.LoginTwitter),
   (r'/login/facebook', tanarky.controller.LoginFacebook),
   (r'/test/twf',       tanarky.controller.PageTest),
   (r'/logout', tanarky.controller.Logout),
   (r'/.*',     tanarky.controller.Error),
   ],
  debug=True)

def main():
  #logging.getLogger().setLevel(logging.DEBUG)
  #logging.info(__name__)
  run_wsgi_app(application)

if __name__ == "__main__":
  #logging.getLogger().setLevel(logging.DEBUG)
  logging.getLogger().setLevel(logging.INFO)
  main()
