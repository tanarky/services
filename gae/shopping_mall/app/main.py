# -*- coding: utf-8 -*-

import sys, cgi
sys.path.insert(0, './lib')
sys.path.insert(0, './distlib.zip')

import re,logging,binascii,urllib2,random,datetime,json
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users, memcache
from google.appengine.ext import db, blobstore

from flask import Flask, render_template, url_for, flash
from flask import redirect, abort, make_response, escape, request
from models.seller import Seller, SellerAndUsers
from models.product import Product, ProductStock
from models.order import Order
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

@app.route('/SELLER/<seller>/orders')
def seller_tool_orders(seller):
    T = {"sellername":seller}
    ret = seller_tool_check_login(seller, T)
    if ret is not True:
        return ret

    orders = Order.gql('where seller=:seller', seller=seller).fetch(limit=10)
    T['orders'] = orders
    T["breadcrumbs"] = [{"url":url_for("seller_tool_index",seller=seller),
                         "title":u"ツールトップ"},
                        {"title":u"注文一覧"}]

    return render_template('seller_tool_orders.html', T=T)

@app.route('/SELLER/<seller>/orders/<orderid>', methods=['GET','POST'])
def seller_tool_orders_edit(seller,orderid):
    T = {"sellername":seller}
    ret = seller_tool_check_login(seller, T)
    if ret is not True:
        return ret
    order = Order.get_by_key_name(orderid)
    if not order:
        return redirect('seller_tool_orders', seller=seller)

    if request.method == 'POST':
        order.status = int(request.form['status'])
        order.put()
        flash(u'注文ステータスを更新しました', category='success')

    T['order'] = order
    T["cart"] = json.loads(order.cart)

    T["breadcrumbs"] = [{"url":url_for("seller_tool_index",seller=seller),
                         "title":u"ツールトップ"},
                        {"title":u"注文一覧",
                         "url":url_for('seller_tool_orders',seller=seller)},
                        {"title":order.key().name()}]

    return render_template('seller_tool_orders_edit.html', T=T)

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
    return '%02x/%02x/%s/%s-%d-%d-%d.%s' % (binascii.crc32(seller) % 256,
                                            binascii.crc32(seller + S) % 256,
                                            seller, code, num,
                                            int(width), int(height), ext)


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
            if 524288 < blob.size:
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

            blob_reader = blobstore.BlobReader(blob_key, buffer_size=524288)
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

    pp = Product.gql('where seller=:seller', seller=seller).fetch(limit=10)
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
    if not p.match(request.form['name']):
        flash(u'seller名は半角英数+"_"で構成される32文字以内の文字列です',
              category='warning')
        return redirect(url_for('user_index'))

    #
    # sellerが存在しないかチェック
    #
    user = T["user"].user_id()
    name = request.form['name']
    exist_seller = SellerAndUsers.gql('WHERE seller = :seller',
                                      seller=name,
                                      keys_only=True).get()
    if exist_seller:
        flash(u'そのsellerアカウントはすでに使用されています', category="warning")
        return redirect(url_for('user_index'))

    #
    # 上限Overしてないかチェック
    #
    exist_rec = SellerAndUsers.gql('WHERE user = :user',
                                   user=user,
                                   keys_only=True).fetch(3)
    if len(exist_rec) == 3:
        flash(u'1ユーザ3店舗までです', category="warning")
        return redirect(url_for('user_index'))

    new_seller_and_users = SellerAndUsers(
        key_name = name + "-" + user,
        seller   = name,
        user     = user,
        grant    = 1, # owner
        status   = 0, # created
        )
    new_seller_and_users.put()

    new_seller = Seller(
        key_name = name,
        name     = name,
        title    = request.form['title'],
        currency = int(request.form['currency']),
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

# seller top ページ
@app.route('/<seller>/')
@app.route('/<seller>/index.html')
def seller_index(seller):
    T = {'sellername':seller}
    helpers.template.get_user(T=T, path=request.path)

    products = []

    pp = Product.all().fetch(limit=10)
    host = "http://localhost:5000/"
    for p in pp:
        product = {}
        product['seller'] = p.seller
        product['code']   = p.code
        product['title']  = p.title
        product['desc']   = p.desc
        product['price']  = u"%d 円" % p.price
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

    return render_template('seller_index.html', T=T)

# seller 商品ページ
@app.route('/<seller>/product/<code>.html')
def seller_product(seller, code):
    T = {"sellername":seller, "code":code}
    ret = seller_tool_check_login(seller, T)

    s = Seller.get_by_key_name('%s' % seller)
    if not 2:
        abort(404)

    p = Product.get_by_key_name('%s-%s' % (seller,code))
    if not p:
        abort(404)

    T['seller']  = s
    T['product'] = p
    host = "http://localhost:5000/"

    if p.image1:
        T['imageurl1'] = "%s%s" % (host,
                                   get_image_path(seller,code,1,300,300,p.image1))
    else:
        T['imageurl1'] = 'http://placehold.it/300x300'

    if p.image2:
        T['imageurl2'] = "%s%s" % (host,
                                   get_image_path(seller,code,2,120,120,p.image2))

    if p.image3:
        T['imageurl3'] = "%s%s" % (host,
                                   get_image_path(seller,code,3,120,120,p.image3))

    T['cart_url'] = url_for('cart_add', seller=seller, code=p.code)
    return render_template('seller_product.html', T=T)

# seller カスタムページ

# seller その他URL
@app.route('/<seller>/product/')
@app.route('/<seller>/product/index.html')
def seller_403(seller):
    return redirect(url_for('seller_index', seller=seller))

# カートトップ
@app.route('/CART/<seller>/')
def cart_index(seller):
    T = {'sellername':seller}
    helpers.template.get_user(T=T, path=request.path)
    if not "user" in T:
        flash('ログインしてから再度カートに追加してください', category='warning')
        return redirect(url_for('seller_product', seller=seller, code=code))

    cart_cache_key = 'C-%s' % (T["user"].user_id())
    cart = memcache.get(cart_cache_key)
    if cart and seller in cart:
        T["cart"] = helpers.template.calc_cart(cart[seller])
        logging.error(T["cart"])
    return render_template('cart_index.html', T=T)

# カートに追加
@app.route('/CART/<seller>/add/<code>', methods=["POST"])
def cart_add(seller,code):
    T = {'sellername':seller}
    helpers.template.get_user(T=T, path=request.path)
    if not "user" in T:
        flash('ログインしてから再度カートに追加してください', category='warning')
        return redirect(url_for('seller_product', seller=seller, code=code))

    cart_cache_key = 'C-%s' % (T["user"].user_id())
    cart = memcache.get(cart_cache_key)
    if not cart:
        cart = {seller:{}}
    elif not seller in cart:
        cart[seller] = {}

    item = {"title":request.form["title"],
            "price":float(request.form["price"]),
            "quantity":int(request.form['quantity'])}
    cart[seller][code] = item

    logging.error(cart)

    memcache.set(cart_cache_key, cart, 86400)
    return redirect(url_for('cart_index', seller=seller))

# カート注文前最終確認
# FIXME: try except
@app.route('/CART/<seller>/confirm', methods=['GET','POST'])
def cart_confirm(seller):
    T = {'sellername':seller}
    helpers.template.get_user(T=T, path=request.path)
    if not "user" in T:
        flash('ログインしてから再度カートに追加してください', category='warning')
        return redirect(url_for('seller_index', seller=seller))

    cart_cache_key = 'C-%s' % (T["user"].user_id())
    cart = memcache.get(cart_cache_key)
    if not cart or not seller in cart:
        flash('カートが空です', category='warning')
        return redirect(url_for('cart_index', seller=seller))

    if request.method == 'POST':
        # 入力チェック
        # FIXME: flask-wtformsを使う

        cart['BUYER'] = {"mail": request.form["mail"],
                         "note": request.form["note"],
                         'ship':{"country":request.form["country"],
                                 "postalcode":request.form["postalcode"],
                                 "pref":request.form["pref"],
                                 "city":request.form["city"],
                                 "addr1":request.form["addr1"],
                                 "addr2":request.form["addr2"]}}
        memcache.set(cart_cache_key, cart, 86400)

        return redirect(url_for('cart_confirm', seller=seller))
    else:
        T["cart"]  = helpers.template.calc_cart(cart[seller])
        T['buyer'] = cart["BUYER"]
        return render_template('cart_confirm.html', T=T)

# カート注文完了処理
@app.route('/CART/<seller>/finalize', methods=['POST'])
def cart_finalize(seller):
    T = {'sellername':seller}
    helpers.template.get_user(T=T, path=request.path)
    if not "user" in T:
        flash(u'ログインしてから再度カートに追加してください', category='warning')
        return redirect(url_for('cart_index', seller=seller))

    # FIXME: ブラウザ2重起動によるセッション情報の変更検知

    cart_cache_key = 'C-%s' % (T["user"].user_id())
    cart = memcache.get(cart_cache_key)
    if not cart or not seller in cart:
        flash(u'カートが空です', category='warning')
        return redirect(url_for('cart_index', seller=seller))

    has_error = None
    reserved  = {}
    for code, item in cart[seller].items():
        stock = ProductStock.get_by_key_name("%s-%s" % (seller, code))
        stock.quantity -= item['quantity']
        if stock.quantity < 0:
            has_error = code
            break
        stock.put()
        reserved[code] = item['quantity']

    if has_error:
        for code, quatity in reserved.items():
            stock = ProductStock.get_by_key_name("%s-%s" % (seller, code))
            stock.quantity += quantity
            stock.put()
        flash(u'商品コード %s の在庫がなくなりました' % has_error,
              category='warning')
        return redirect(url_for('cart_index', seller=seller))
    
    content = {"cart" : helpers.template.calc_cart(cart[seller]),
               "buyer": cart["BUYER"]}

    key_name = "-".join([seller,
                         T["user"].user_id(),
                         datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
                         str(random.randint(0,256))])

    order = Order(key_name = key_name,
                  cart = unicode(json.dumps(helpers.template.calc_cart(cart[seller]))),
                  seller   = seller,
                  status   = 0)

    order.buyer_mail = cart["BUYER"]["mail"]
    order.buyer_note = cart["BUYER"]["note"]
    order.buyer_ship_country    = cart["BUYER"]["ship"]['country']
    order.buyer_ship_postalcode = cart["BUYER"]["ship"]['postalcode']
    order.buyer_ship_pref       = cart["BUYER"]["ship"]['pref']
    order.buyer_ship_city       = cart["BUYER"]["ship"]['city']
    order.buyer_ship_addr1      = cart["BUYER"]["ship"]['addr1']
    order.buyer_ship_addr2      = cart["BUYER"]["ship"]['addr2']

    order.put()

    del(cart[seller])
    memcache.set(cart_cache_key, cart, 86400)

    return redirect(url_for('cart_finished', seller=seller))

# カート注文完了画面
@app.route('/CART/<seller>/finished')
def cart_finished(seller):
    T = {'sellername':seller}
    helpers.template.get_user(T=T, path=request.path)
    if not "user" in T:
        flash('ログインしてから再度カートに追加してください', category='warning')
        return redirect(url_for('seller_product', seller=seller, code=code))

    # FIXME: URL直叩き対策

    return render_template('cart_finished.html', T=T)

# TODO: 注文履歴(User)
# TODO: 注文履歴(Seller)
# TODO: 注文履歴一覧(User)
# TODO: 注文履歴一覧(Seller)

#
# error pages
# 
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    run_wsgi_app(app)
