# -*- coding: utf-8 -*-
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import logging
import tanarky.controller

application = webapp.WSGIApplication(
                                     [(r'/', tanarky.controller.Home),
                                      (r'/home2', tanarky.controller.Home2),
                                      ],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  logging.getLogger().setLevel(logging.DEBUG)
  main()
