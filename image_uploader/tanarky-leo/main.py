# coding: utf-8

# version 0.0.1

from flask import Flask,request,abort,make_response,render_template
import logging,binascii,ConfigParser,os.path,sys
import os,json
from operator import methodcaller
import Image, StringIO

config = ConfigParser.ConfigParser()
config.read('/etc/tanarky/leo/leo.conf')

VERSION = '1.0.3'
ROOT = config.get("data","root")
SEED = config.get("data","seed")
NUM  = int(config.get("data","num"))

app = Flask(__name__)

def group2path(g):
    return '%02x/%02x/%s' % (binascii.crc32(g) % NUM,
                             binascii.crc32(g + SEED) % NUM,
                             g)

@app.route('/')
def index():
    return VERSION

@app.route('/list')
def list():
    try:
        world    = request.args['world']
        group    = request.args['group']
        hashpath = group2path(group)
        path     = u'%s/%s/%s' % (ROOT, world, hashpath)

        T = {}
        T['url']   = u'http://%s.tanarky.com/%s/' % (world, hashpath)
        T['files'] = os.listdir(path)
        return render_template('list.html', T=T)
    except:
        logging.error(sys.exc_info())
        return abort(400)

@app.route('/upload', methods=['PUT', 'GET', 'DELETE'])
def upload():
    try:
        world    = request.args['world']
        group    = request.args['group']
        name     = request.args['name']
        filetype = request.args['type']

        if 'resizes' in request.args:
            p = request.args['resizes']
            resizes = map(lambda x : tuple(map( lambda y : int(y),
                                                x.split('x'))) ,
                          request.args['resizes'].split(','))
        else:
            resizes = []

        hashpath = group2path(group)

        if request.method == 'GET':
            path = u'/%s' % (hashpath)
            ret = []
            if not resizes:
                filepath = u"%s/%s.%s" % (path,
                                          name,
                                          filetype)
                ret.append(filepath)
            else:
                for r in resizes:
                    filepath = u"%s/%s-%d-%d.%s" % (path,
                                                    name,
                                                    r[0],
                                                    r[1],
                                                    filetype)
                    ret.append(filepath)
            response = make_response(json.dumps(ret))
            response.headers['Content-type'] = u'application/json; charset=utf-8;'
            return response
        elif request.method == 'PUT':
            data = request.data
            if not data:
                raise Exception('no data')

            path = u'%s/%s/%s' % (ROOT, world, hashpath)
            if os.path.isdir(path) == False:
                logging.debug(path)
                os.makedirs(path)

            if not resizes:
                filepath = u"%s/%s.%s" % (path, name, filetype)
                logging.debug(path)
                logging.debug(name)
                logging.debug(filepath)
                f = open(filepath, 'w')
                f.write(data)
                f.close()
            else:
                for r in resizes:
                    im = Image.open(StringIO.StringIO(data))
                    im.thumbnail(r, Image.ANTIALIAS)
                    filepath = u"%s/%s-%d-%d.%s" % (path,
                                                    name,
                                                    r[0],
                                                    r[1],
                                                    filetype)
                    im.save(filepath, filetype)
                    os.chmod(filepath, 0666)
            response = make_response(u'{"status":"OK"}')
            response.headers['Content-type'] = u'application/json; charset=utf-8;'
            return response
    except:
        logging.error(sys.exc_info())
        return abort(400)

@app.errorhandler(400)
def page_not_found(error):
    return 'error', 400

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    app.run(debug=True, port=8000)
