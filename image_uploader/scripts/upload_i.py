# coding: utf8
import os, sys, urllib2, urllib, logging, json

files   = sys.argv[1:]
world   = 'i'
group   = 'tanarky.com'
baseurl = 'http://img.tanarky.com:23456'
#baseurl = 'http://localhost:8000'
upload  = '/upload'
imglist = '/list'
url     = '%s%s' % (baseurl, upload)
url2    = '%s%s?world=%s&group=%s' % (baseurl,
                                      imglist,
                                      world,
                                      group)

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

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    for f in files:
        basename = os.path.basename(f)
        ff  = basename.split(".")
        logging.debug(f)
        req = {'world': world,
               'group': group,
               'name' : ff[0],
               'type' : ff[1]}
        if upload(f, req) == False:
            logging.debug('Failed: %s' % f)
    print 'finished uploading files: %s' % url2


