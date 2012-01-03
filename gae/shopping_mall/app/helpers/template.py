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

"""

lines: [
         {title:"商品1", code:"", price:"", quantity:"", total:""},
         {title:"商品2", code:"", price:"", quantity:"", total:""},
         {title:"商品3", code:"", price:"", quantity:"", total:""},
         {title:"送料", total:300.0},
         {title:"割引", total:-20.0},
       ],
total: 1234.56

"""
def calc_cart(cache):
    cart = {'lines':[], 'total':0.0}
    if not cache:
        return cart
    for code, line in cache.items():
        line = {'title':line['title'],
                'code':code,
                'price':line['price'],
                'quantity':line['quantity'],
                'total':float(line['price']*line['quantity'])}
        cart['total'] += line['total']
        cart['lines'].append(line)
    return cart
        

