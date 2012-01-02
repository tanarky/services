# -*- coding: utf-8 -*-

import sys, cgi
sys.path.insert(0, './lib')
sys.path.insert(0, './distlib.zip')

import re,logging,binascii,urllib2
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db, blobstore

from flask import Flask, render_template, url_for, redirect, abort, make_response, escape, request, flash
from models.seller import Seller, SellerAndUsers
from models.product import Product, ProductStock
import helpers.template

app = Flask(__name__)
app.secret_key = 'tanarky_secret'

from google.appengine.api import mail

@app.route('/mail')
def test_mail():
    mail.send_mail(sender="Example.com Support <support@example.com>",
                   to="Satoshi Tanaka <tanarky@yahoo.co.jp>",
                   subject="Your account has been approved",
                   body="""
Dear Albert:

Your example.com account has been approved.  You can now visit
http://www.example.com/ and sign in using your Google Account to
access new features.

Please let us know if you have any questions.

The example.com Team

""")
    return redirect('/')


#
# admin pages
#
@app.route('/ADMIN/')
def admin_index():
    tmpl_vars = {"name":"tanarky"}
    return render_template('admin_index.html', T=tmpl_vars)

# seller list
@app.route('/ADMIN/sellers', methods=['GET','POST','DELETE'])
def admin_sellers():
    T = {}
    helpers.template.get_user(T=T, path=request.path)
    if not "user" in T:
        flash(u'ログインしてください', category='warning')
        return redirect(url_for('index'))
    if not users.is_current_user_admin():
        flash(u'管理者ユーザでログインしてください', category='warning')
        return redirect(url_for('user_index'))

    if request.method == 'GET':
        T['sellers'] = SellerAndUsers.all().fetch(limit=10)
        return render_template('admin_sellers.html', T=T)
    elif request.method == 'POST':
        for s in request.form.getlist('seller'):
            seller = SellerAndUsers.gql('WHERE seller = :seller',
                                        seller=s).get()
            seller.status = 1
            seller.put()
        flash(u'承認しました', category='success')
        return redirect(url_for('admin_sellers'))
    elif request.method == 'DELETE':
        flash(u'未実装', category='warning')
        return redirect(url_for('admin_sellers'))

#
# seller tool page
# 
def seller_tool_check_login(seller, T):
    helpers.template.get_user(T=T, path=request.path)
    if not "user" in T:
        flash(u'ログインしてください', category='warning')
        return redirect(url_for('index'))
    seller_and_users = SellerAndUsers.gql('WHERE seller=:seller and user=:user',
                                          seller=seller,
                                          user=T["user"].user_id()).get()
    if not seller_and_users:
        flash(u'sellerは存在しないか権限がありません', category='warning')
        return redirect(url_for('user_index'))
    if seller_and_users.status != 1:
        flash(u'承認されていません', category='warning')
        return redirect(url_for('user_index'))
    T["grant"] = seller_and_users.grant
    return True

# 新規注文確認
def seller_tool_check_new_order(T):
    #flash(u'<a href="%s">新しい注文</a>があります' % url_for('admin_sellers'),
    #      category='success')
    return True

@app.route('/SELLER/<seller>/')
def seller_tool_index(seller):
    T = {"sellername":seller}
    ret = seller_tool_check_login(seller, T)
    if ret is not True:
        return ret
    seller_tool_check_new_order(T)
    return render_template('seller_tool_index.html', T=T)

@app.route('/SELLER/<seller>/product/new', methods=['GET','POST'])
def seller_tool_product_new(seller):
    T = {"sellername":seller}
    ret = seller_tool_check_login(seller, T)
    if ret is not True:
        return ret
    if request.method == 'GET':
        seller_tool_check_new_order(T)

        T["breadcrumbs"] = [{"url":url_for("seller_tool_index",seller=seller),
                             "title":u"ツールトップ"},
                            {"url":url_for("seller_tool_products",seller=seller),
                             "title":u"商品一覧"},
                            {"title":u"新規商品情報追加"}]

        return render_template('seller_tool_product_new.html',
                               T=T)
    else:        
        try:
            new_product = Product(
                key_name = "%s-%s" % (seller, request.form['product_code']),
                seller   = seller,
                code     = request.form['product_code'],
                title    = request.form['product_title'],
                price    = float(request.form['product_price']),
                currency = int(request.form['product_currency']),
                desc     = request.form['product_desc'],
                )
            new_product.put()

            new_product_stock = ProductStock(
                key_name = "%s-%s" % (seller, request.form['product_code']),
                seller   = seller,
                code     = request.form['product_code'],
                quantity = int(request.form['product_stock']),
                )
            new_product_stock.put()

            flash(u'保存しました', category='success')
            return redirect(url_for('seller_tool_products', seller=seller))
        except:
            logging.error(sys.exc_info())
            flash(u'失敗しました', category='warning')
            return render_template('seller_tool_product_new.html',
                                   T=T)

@app.route('/SELLER/<seller>/product/<code>', methods=['GET','POST'])
def seller_tool_product_edit(seller,code):
    T = {"sellername":seller}
    ret = seller_tool_check_login(seller, T)
    if ret is not True:
        return ret
    if request.method == 'GET':
        seller_tool_check_new_order(T)

        key_name = "%s-%s" % (seller, code)
        product = Product.get_by_key_name("%s-%s" % (seller, code))
        stock   = ProductStock.get_by_key_name("%s-%s" % (seller, code))

        T["product_title"]    = product.title
        T["product_code"]     = product.code
        T["product_price"]    = product.price
        T["product_desc"]     = product.desc
        T["product_currency"] = product.currency
        T["product_stock"]    = stock.quantity

        T["breadcrumbs"] = [{"url":url_for("seller_tool_index",seller=seller),
                             "title":u"ツールトップ"},
                            {"url":url_for("seller_tool_products",seller=seller),
                             "title":u"商品一覧"},
                            {"title":u"商品情報編集: %s" % product.code}]

        return render_template('seller_tool_product_edit.html',
                               T=T)
    else:
        try:
            logging.error(seller)
            logging.error(code)
            product = Product.get_by_key_name("%s-%s" % (seller, code))
            stock   = ProductStock.get_by_key_name("%s-%s" % (seller, code))

            product.title    = request.form['product_title']
            product.desc     = request.form['product_desc']
            product.price    = float(request.form['product_price'])
            product.currency = int(request.form['product_currency'])
            product.put()

            stock.quantity = int(request.form['product_stock'])
            stock.put()

            flash(u'保存しました', category='success')
            return redirect(url_for('seller_tool_products', seller=seller))
        except:
            logging.error(sys.exc_info())
            flash(u'失敗しました', category='warning')
            return render_template('seller_tool_product_edit.html',
                                   T=T)

def get_image_path(seller, code, num, width, height, extint):
    if extint == 2:
        ext = 'png'
    elif extint == 3:
        ext = 'gif'
    else:
        ext = 'jpeg'

    S = 'tanarky'
    return '%02x/%02x/%s/%s-%d-%s-%s.%s' % (binascii.crc32(seller) % 256,
                                            binascii.crc32(seller + S) % 256,
                                            seller, code, num,
                                            width, height, ext)


@app.route('/SELLER/<seller>/product/<code>/image',methods=["GET","POST"])
def seller_tool_product_image(seller,code):
    T = {"sellername":seller}
    ret = seller_tool_check_login(seller, T)
    if ret is not True:
        return ret

    if request.method == "GET":
        seller_tool_check_new_order(T)

        T["breadcrumbs"] = [{"url":url_for("seller_tool_index",seller=seller),
                             "title":u"ツールトップ"},
                            {"title":u"商品一覧",
                             "url":url_for("seller_tool_products",seller=seller)},
                            {"title":u"商品画像編集"}]

        key_name = "%s-%s" % (seller, code)
        product = Product.get_by_key_name("%s-%s" % (seller, code))

        T["product_title"] = product.title

        for x in range(1,4):
            logging.error(product.__dict__["_image%d" % x])
            if 0 < product.__dict__["_image%d" % x]:
                path = get_image_path(seller,
                                      code,
                                      x,
                                      '300',
                                      '300',
                                      product.__dict__["_image%d" % x])
                host = "http://localhost:5000/"
                T["product_image%d" % x] = '%s%s' % (host, path)

        T["upload_url"] = blobstore.create_upload_url(request.base_url)
        return render_template('seller_tool_product_image.html', T=T)
    else:
        try:
            logging.error(request)
            imgnum   = request.values['product_image_num']
            filename = 'product_image%s' % imgnum

            headers   = request.files[filename].headers['Content-Type']

            msgtype, params = cgi.parse_header(headers)
            blob_key = blobstore.BlobKey(params['blob-key'])
            blob = blobstore.BlobInfo.get(blob_key)

            logging.error(blob.size)
            if 262144 < blob.size:
                raise Exception('size error')

            logging.error(blob.content_type)
            if blob.content_type == 'image/jpeg':
                imgtype = 'jpeg'
                imgtypenum = 1
            elif blob.content_type == 'image/png':
                imgtype = 'png'
                imgtypenum = 2
            elif blob.content_type == 'image/gif':
                imgtype = 'gif'
                imgtypenum = 3
            else:
                raise Exception('invalid image type: %s' % blob.content_type)

            blob_reader = blobstore.BlobReader(blob_key, buffer_size=262144)
            imgbody = blob_reader.read()

            # thumbsize
            imgsizes = '60x60,120x120,300x300'
            
            # API POST
            url   = 'http://localhost:8000/upload/product'
            query = 'group=%s&name=%s&type=%s&resizes=%s&num=%s' % (seller,
                                                                    code,
                                                                    imgtype,
                                                                    imgsizes,
                                                                    imgnum)
            req = urllib2.Request('%s?%s' % (url,query),
                                  data=imgbody,
                                  headers={'Content-type':'image/%s' % imgtype})
            req.get_method= lambda: 'PUT'
            ret = urllib2.urlopen(req)
            ret.read(1024)

            product = Product.get_by_key_name("%s-%s" % (seller, code))
            product.__dict__["_image%s" % imgnum] = imgtypenum
            product.put()

            # cleanup
            blob.delete()
        except:
            logging.error(sys.exc_info())
            flash(u'失敗しました', category='warning')
        return redirect(request.base_url)
    
@app.route('/SELLER/<seller>/products')
def seller_tool_products(seller):
    T = {"sellername":seller}
    ret = seller_tool_check_login(seller, T)
    if ret is not True:
        return ret
    seller_tool_check_new_order(T)

    products = []

    pp = Product.all().fetch(limit=10)
    for p in pp:
        product = {}
        product['seller'] = p.seller
        product['code']   = p.code
        product['title']  = p.title
        product['desc']   = p.desc

        host = "http://localhost:5000/"
        if p.image1:
            path = get_image_path(p.seller,
                                  p.code,
                                  1,
                                  '120',
                                  '120',
                                  p.image1)
            product['imgurl'] = '%s%s' % (host, path)
        else:
            product['imgurl'] = 'http://placehold.it/120x120'
        products.append(product)

    T["products"] = products

    T["breadcrumbs"] = [{"url":url_for("seller_tool_index",seller=seller),
                         "title":u"ツールトップ"},
                        {"title":u"商品一覧"}]

    return render_template('seller_tool_products.html',
                           T=T)

#
# user page
#
@app.route('/USER/')
def user_index():
    T = {}
    helpers.template.get_user(T=T, path=request.path)
    if not "user" in T:
        flash(u'ログインしてください', category='warning')
        return redirect(url_for('index'))

    T["sellers"] = SellerAndUsers.gql('WHERE user = :user',
                                      user=T["user"].user_id()).fetch(10)
    return render_template('user_index.html', T=T)

@app.route('/USER/seller/create', methods=['POST'])
def user_seller_create():
    T = {}
    helpers.template.get_user(T=T, path=request.path)
    if not "user" in T:
        flash(u'ログインしてください', category='warning')
        return redirect(url_for('index'))

    p = re.compile(r'^[a-z0-9]{1}[a-z0-9_]{2,31}$')
    if not p.match(request.form['seller']):
        flash(u'seller名は半角英数+"_"で構成される32文字以内の文字列です',
              category='warning')
        return redirect(url_for('user_index'))

    #
    # sellerが存在しないかチェック
    #
    user   = T["user"].user_id()
    seller = request.form['seller']
    exist_seller = SellerAndUsers.gql('WHERE seller = :seller',
                                      seller=seller,
                                      keys_only=True).get()
    if exist_seller:
        flash(u'そのseller名はすでに使用されています', category="warning")
        return redirect(url_for('user_index'))

    #
    # 上限Overしてないかチェック
    #
    exist_rec = SellerAndUsers.gql('WHERE user = :user',
                                   user=user,
                                   keys_only=True).fetch(3)
    if len(exist_rec) == 3:
        flash(u'作成できるのは、お一人様 3 sellerまでです', category="warning")
        return redirect(url_for('user_index'))

    new_seller_and_users = SellerAndUsers(
        key_name = seller + "-" + user,
        seller   = seller,
        user     = user,
        grant    = 1, # owner
        status   = 0, # created
        )
    new_seller_and_users.put()

    new_seller = Seller(
        key_name = seller,
        name     = seller,
        status   = 0, # hidden
        )
    new_seller.put()

    flash(u'新規sellerを申請しました', category="success")
    return redirect(url_for('user_index'))

@app.route('/USER/seller/adduser', methods=['POST'])
def user_seller_adduser():
    flash(u'未実装', category='warning')
    return redirect(url_for('user_index'))

@app.route('/')
def index():
    T = {}
    helpers.template.get_user(T=T, path=request.path)

    return render_template('index.html', T=T)

@app.route('/flash')
def flash_mes():
    flash('test error message', category='error')
    flash('test success message', category='success')
    flash('test info message', category='info')
    flash('test warning message', category='warning')
    return redirect(url_for('index'))

# seller top ページ
@app.route('/<seller>/')
@app.route('/<seller>/index.html')
def seller_index(seller):
    tmpl_vars = {"name":seller}
    return render_template('seller_index.html', T=tmpl_vars)

# seller 商品ページ
@app.route('/<seller>/product/<product>')
def seller_product(seller, product):
    tmpl_vars = {"name":seller, "product":product}
    return render_template('seller_product.html', T=tmpl_vars)

# seller カスタムページ

# seller その他URL
@app.route('/<seller>/product/')
@app.route('/<seller>/product/index.html')
def seller_403(seller):
    return redirect(url_for('seller_index', seller=seller))

# seller 編集ツール top

# seller 編集ツール items get
# seller 編集ツール item get
# seller 編集ツール item put
# seller 編集ツール item delete

# seller 編集ツール orders get
# seller 編集ツール order get

# seller 編集ツール common page

# seller 編集ツール each page

# cart top

# cart finish

# order history

# order list


#
# error pages
# 
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    run_wsgi_app(app)
