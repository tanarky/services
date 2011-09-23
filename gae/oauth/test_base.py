# -*- coding: utf-8 -*-
import os
import unittest

from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.api import mail_stub
from google.appengine.api import urlfetch_stub
from google.appengine.api import user_service_stub
from google.appengine.ext import db, search

from google.appengine.api import users

APP_ID = u'tanargle'
AUTH_DOMAIN = 'gmail.com'
LOGGED_IN_USER = 'test@example.com'

class GAETestBase(unittest.TestCase):
    def setUp(self):
        # API Proxyを登録する
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()

        # ダミーのDatastoreを登録する
        stub = datastore_file_stub.DatastoreFileStub(APP_ID,
                                                     '/dev/null',
                                                     '/dev/null')
        apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)

        # ダミーのユーザ認証用サービスを登録する
        apiproxy_stub_map.apiproxy.RegisterStub(
            'user', user_service_stub.UserServiceStub())
        os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
        os.environ['USER_EMAIL'] = LOGGED_IN_USER

        # ダミーのurlfetchを登録
        apiproxy_stub_map.apiproxy.RegisterStub(
            'urlfetch', urlfetch_stub.URLFetchServiceStub())

        # ダミーのメール送信サービスを登録
        apiproxy_stub_map.apiproxy.RegisterStub(
            'mail', mail_stub.MailServiceStub()) 
