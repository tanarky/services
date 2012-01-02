# coding: utf-8
from flask import Flask,request,abort
import logging,binascii,ConfigParser,os.path,sys
import os
from operator import methodcaller
import Image, StringIO

config = ConfigParser.ConfigParser()
config.read('/etc/tanarky-leo/dir.conf')

ROOT = config.get("data","root")
SEED = config.get("data","seed")
NUM  = int(config.get("data","num"))

app = Flask(__name__)

def group2path(g):
    return '%02x/%02x/%s' % (binascii.crc32(g) % NUM,
                             binascii.crc32(g + SEED) % NUM,
                             g)

@app.route('/')
def hello_world():
    return u"はろーわーるど1"

@app.route('/upload/product', methods=['PUT', 'GET'])
def upload_product():
    try:
        group    = request.args['group']
        name     = request.args['name']
        filetype = request.args['type']
        num      = int(request.args['num'])

        resizes = map(lambda x : tuple(map( lambda y : int(y),
                                            x.split('x'))) ,
                      request.args['resizes'].split(','))
        
        data  = request.data

        if not data:
            raise Exception('no data')

        hashpath = group2path(group)
        path  = u'%s/%s' % (ROOT, hashpath)
        if os.path.isdir(path) == False:
            logging.debug(path)
            os.makedirs(path)

        for r in resizes:
            im = Image.open(StringIO.StringIO(data))
            im.thumbnail(r, Image.ANTIALIAS)
            filename = u"%s/%s-%d-%d-%d.%s" % (path,
                                               name,
                                               num,
                                               r[0], # width
                                               r[1], # height
                                               filetype)
            # FIXME: 他の拡張子ファイルを消す
            logging.debug(filename)
            im.save(filename, filetype)
            os.chmod(filename, 0666)

        return u"%s" % hashpath
    except:
        return abort(400)

@app.errorhandler(400)
def page_not_found(error):
    return 'error', 400

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    app.run(debug=True, port=8000)
