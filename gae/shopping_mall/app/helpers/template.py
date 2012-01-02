# -*- coding: utf-8 -*-

from google.appengine.api import users
from flask import Flask, render_template, url_for, redirect, abort, make_response, escape, request, flash
import logging

def get_user(T={}, path="/"):
    user = users.get_current_user()
    if user:
        T['user'] = user
        T["logouturl"] = users.create_logout_url(path)
    else:
        T["loginurl"]  = users.create_login_url(path)

