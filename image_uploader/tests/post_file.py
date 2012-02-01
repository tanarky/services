# coding: utf8
"""
test pattern

1. type

  a. jpeg
  b. gif
  c. png
  d. html
  e. css
  f. jpeg and resizes


#confファイルを入れ替える(rootをどこにするか,/tmp?) -> サーバを起動する
データディレクトリの初期化をする(sh)
  sudo rm -rf ROOT
  sudo mkdir -m 755 ROOT
  sudo -u nobody mkdir ROOT. '/'. TEST_WORLD
ファイルアップロードする
アップロードされたファイルが正しいか確認する
#confを元に戻す

"""
import os, sys, urllib2, urllib, logging, json

"""
files = ['test.jpeg',
         'test.gif',
         'test.png',
         'test.html',
         'test.css']
"""
#files = ['nozomi.jpeg']
#files = ['test.html']
#files = ['test.css']
#files = ['test.png']
files = ['android.gif']
world = 'img.product'
group = 'tanarky'
#url   = 'http://localhost:8000/upload'
url   = 'http://img.tanarky.com:10080/upload'

def upload(f, req):
    try:
        data = open(f).read()
        if req['type'] == 'jpeg' or req['type'] == "gif" or req['type'] == "png":
            headers = {'Content-type':'image/%s' % req['type']}
        elif req['type'] == 'html' or req['type'] == 'css':
            headers = {'Content-type':'text/%s' % req['type']}
        else:
            raise Exception('type error')

        req  = urllib2.Request('%s?%s' % (url, urllib.urlencode(req)),
                               data=data,
                               headers=headers)
        req.get_method= lambda: 'PUT'
        ret = urllib2.urlopen(req)
        return True
    except:
        logging.error(sys.exc_info())
        return False

for f in files:
    ff  = f.split(".")
    req = {'world': world,
           'group': group,
           'resizes': "200x100,1200x1000",
           'name' : ff[0],
           'type' : ff[1]}
    if upload(f, req) == False:
        logging.error('Failed: %s' % f)




