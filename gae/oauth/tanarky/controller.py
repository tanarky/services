# -*- coding: utf-8 -*-
import ConfigParser, os, logging, urllib, urllib2, time, hmac, cgi, Cookie, email,math, random

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from django.utils import simplejson

import tanarky
import tanarky.oauth
import tanarky.cookie
import tanarky.model

class PageBase(webapp.RequestHandler):
  def parse_result(self, result, user=None):
    r = {"id": result.key().id(),
         "from_name": result.from_name,
         "to_name": result.to_name,
         "win":0}

    for i in range(0,3):
      if result.from_hands[i] == result.to_hands[i]:
        continue

      if result.from_hands[i] == 1 and result.to_hands[i] == 2:
        r["win"] = 1
      elif result.from_hands[i] == 1 and result.to_hands[i] == 3:
        r["win"] = 2
      if result.from_hands[i] == 2 and result.to_hands[i] == 1:
        r["win"] = 2
      elif result.from_hands[i] == 2 and result.to_hands[i] == 3:
        r["win"] = 1
      if result.from_hands[i] == 3 and result.to_hands[i] == 1:
        r["win"] = 1
      elif result.from_hands[i] == 3 and result.to_hands[i] == 2:
        r["win"] = 2

      break

    if user != None:
      if result.from_sid == user["main_sid"] and result.from_uid == user["main_uid"]:
        r["you"] = 1
      elif result.to_sid == user["main_sid"] and result.to_uid == user["main_uid"]:
        r["you"] = 2

    return r

  def get_results_by_from_user(self, user):
    ret = []
    res = tanarky.model.Result.gql("WHERE from_sid=:sid and from_uid=:uid order by updated desc",
                                   sid = user["main_sid"],
                                   uid = user["main_uid"]).fetch(100,0)
    for r in res:
      logging.error(r)
      ret.append(self.parse_result(r))
    return ret

  def get_results_by_to_user(self, user):
    ret = []
    res = tanarky.model.Result.gql("WHERE to_sid=:sid and to_uid=:uid order by updated",
                                   sid = user["main_sid"],
                                   uid = user["main_uid"]).fetch(100,0)
    for r in res:
      ret.append(self.parse_result(r))
    return ret

  def get_alert(self, user):
    return tanarky.model.Alert.gql("WHERE sid=:sid and uid=:uid", 
                                   sid = user["main_sid"],
                                   uid = user["main_uid"]).get()

  def get_msg_from_cookie(self):
    msg_cookie= tanarky.cookie.Message()

    logging.debug(msg_cookie.name)
    logging.debug(self.request.cookies.get("M"))

    msg = msg_cookie.decode(self.request.cookies.get(msg_cookie.name))
    msg_cookie.clear(headers=self.response.headers._headers)
    logging.debug(msg)
    return msg

  def get_oauth_client(self, name):
    if name == "twitter":
      app_id     = tanarky.config.get("twitter_test", "app_id")
      app_secret = tanarky.config.get("twitter_test", "app_secret")
      return tanarky.oauth.TwitterClient(app_id,
                                         app_secret,
                                         self.request.path_url)
    elif name == "facebook":
      app_id     = tanarky.config.get("facebook_test", "app_id")
      app_secret = tanarky.config.get("facebook_test", "app_secret")
      return tanarky.oauth.FacebookClient(app_id,
                                          app_secret,
                                          self.request.path_url)
    return None

  def decode_u_cookie(self):
    return tanarky.cookie.User().decode(self.request.cookies.get("U"))

  def get_tmpl_path(self, name):
    return os.path.join(os.path.dirname(__file__),
                        'templates/%s.html' % name)

  def get_tmpl_vars_paging(self, link, hits, current=1):
    paging = {"current":current,
              "link":link,
              "hits":hits,
              "max":int(math.ceil(float(hits)/10))}

    if 1 < current:
      paging["prev"] = current - 1
    if hits == 0 or current < paging["max"]:
      paging["next"] = current + 1

    if 0 < hits:
      paging["navi"] = [current]
      for x in range(1,5):
        if current - x > 0:
          paging["navi"].insert(0,current-x)
        if current + x <= paging["max"]:
          paging["navi"].append(current+x)

    logging.debug(paging)
    return paging


class PageTest(PageBase):
  def get(self):
    self.response.out.write("ok")
  def post(self):
    self.response.out.write("ok")

class PageReceive(PageBase):
  """
  申し込みを受けて処理をするページ
  関係ない人が見たら、申込内容を表示する
  """
  def get(self):
    """
    URLのsigがあっているか確認
    必要なパラメータ:
      sig
      offer_id
    """
    # 略

    """
    ログインしていない場合はログインページへ?
    それとも、ログインしてくださいページを表示する?
    """
    user = self.decode_u_cookie()
    url  = "/login/twitter?rd=%s" % urllib.quote(self.request.path_qs)
    if user == None or not user["uid2"]:
      return self.redirect(url)

    """
    offerデータを取得、なければ/twitterへ
    """
    offer_id = self.request.get("offer")
    offer = tanarky.model.Offer.get_by_key_name(offer_id)
    if offer == None:
      return self.redirect(url)

    """
    offerデータのto_userと閲覧者が一致しているかを確認
    一致しなければ、現在の登録情報を表示して終了
    一致していれば、入力フォームを表示して終了
    """
    if offer.to_uid != user["uid2"]:
      # FIXME: エラー処理書くのがだるかったので、/に飛ばしてる
      return self.redirect("/")

    hands = []
    for i in range(1,4):
      h = {"index":i, "rand":random.randint(1,3)}
      hands.append(h)

    tmpl_vars = {}
    tmpl_vars["offer"]   = offer_id
    tmpl_vars["account"] = offer.from_name
    tmpl_vars["hands"]   = hands
    tmpl_vars["prize"]   = offer.prize
    path = os.path.join(os.path.dirname(__file__),
                        'templates/offer_receive.html')
    return self.response.out.write(template.render(path,tmpl_vars))

  def post(self):
    """
    必要なパラメータ:
      sig
      offer_id
      to_hands
    sigやuserデータが正しいかチェックなど
    """
    offer_id = self.request.get("offer")
    to_hands = [int(self.request.get("hand1")),
                int(self.request.get("hand2")),
                int(self.request.get("hand3"))]

    """
    offerデータを取得、なければ直近のResultページに飛ばす?
    """
    offer = tanarky.model.Offer.get_by_key_name(offer_id)
    if offer == None:
      logging.error("no offer")
      return self.redirect(url)

    """
    offerデータからResultデータに登録
    結果が成立したので、alertデータを消す
    userごとのLogデータに保存
    """
    result = tanarky.model.Result(
      from_sid = offer.from_sid,
      from_uid = offer.from_uid,
      from_hands = offer.from_hands,
      from_name = offer.from_name,
      to_sid = offer.to_sid,
      to_uid = offer.to_uid,
      to_hands = to_hands,
      to_name = offer.to_name,
      status = offer.status
      )
    result.put()
    result_id = result.key().id()
    logging.info("success: %s" % result_id)

    """
    データを消す
      offer, alert
    """
    offer.delete()
    alert = tanarky.model.Alert.gql("WHERE offer=:offer", 
                                    offer=offer_id).get()
    if alert:
      alert.delete()

    """
    Logデータ保存
    """
    # 略

    """
    結果ページにリダイレクト
    """
    return self.redirect("/result?id=%s" % result_id)

class PageResult(PageBase):
  def get(self):
    """
    データがない場合やresultデータがない場合は、/にリダイレクト
    閲覧者が、resultの関係者であるかを確認して?
    ページ表示
    """

    result_id = self.request.get("id")
    if result_id == "":
      return self.redirect("/");

    result = tanarky.model.Result.get_by_id(int(result_id))

    if result == None:
      return self.redirect("/");

    tmpl_vars = {}

    user = self.decode_u_cookie()
    if user == None:
      tmpl_vars["name"] = "guest"

    tmpl_vars["result"] = self.parse_result(result, user)

    path = os.path.join(os.path.dirname(__file__),
                        'templates/result.html')
    return self.response.out.write(template.render(path,tmpl_vars))

class PageTwitterOffer(PageBase):
  def get(self):
    user = self.decode_u_cookie()
    if user == None:
      return self.redirect("/");

    logging.info(user)

    to_uid     = self.request.get("uid", "")
    # 表示名 like Satoshi Tanaka
    to_name    = self.request.get("name", "")
    # アカウント like tanarky
    to_account = self.request.get("account", "")
    req_sig    = self.request.get("sig", "")

    """ 必須パラメータが空の場合は/twitterに戻す """
    if to_uid == "" or to_name == "" or to_account == "":
      return self.redirect("/twitter");

    """
    sigチェック
    """
    helper = tanarky.Helper()
    s = "/".join([to_uid,to_name,to_account])
    sig = helper.get_params_signature(s)
    if sig != req_sig:
      return self.redirect("/twitter");

    """
    すでにofferがある場合はその情報を使う
    """
    from_sid = user["main_sid"]
    from_uid = user["main_uid"]
    to_sid   = 2
    key   = "%d-%s:%d-%s" % (from_sid,from_uid,to_sid,to_uid)
    offer = tanarky.model.Offer.get_by_key_name(key)
    hands = []
    if offer != None:
      logging.info("offer exist")
      logging.info(offer)
      for i in range(1,4):
        h = {"index":i, "rand":offer.from_hands[i-1]}
        hands.append(h)
    else:
      logging.info("offer NOT exist")
      for i in range(1,4):
        h = {"index":i, "rand":random.randint(1,3)}
        hands.append(h)

    tmpl_vars = {}
    tmpl_vars["name"]    = to_name
    tmpl_vars["sid"]     = 2
    tmpl_vars["uid"]     = to_uid
    tmpl_vars["account"] = to_account
    tmpl_vars["hands"]   = hands
    path = os.path.join(os.path.dirname(__file__),
                        'templates/twitter_offer.html')
    return self.response.out.write(template.render(path,tmpl_vars))

  def post(self):
    user = self.decode_u_cookie()
    if user == None:
      return self.redirect("/")

    helper   = tanarky.Helper()
    from_sid = user["main_sid"]
    from_uid = user["main_uid"]
    to_sid   = 2
    to_uid   = self.request.get("uid")

    to_user_exists = False
    """
    ここでUserに対戦相手のデータがないか確認
    あったら、to_sid, to_uidを上書き & to_user_exist = True
    """
    user_model = tanarky.model.get_user_by_twitter_uid(to_uid)
    if user_model != None:
      to_user_exists = True
      if user_model.main_sid != 2:
        to_sid = user_model.main_sid
        to_uid = user_model.__dict__["uid%d" % to_sid]

    """
    offerデータ登録
    """
    offer_exists = False
    offer_key = "%d-%s-%d-%s" % (from_sid,from_uid,to_sid,to_uid)
    offer = tanarky.model.Offer.get_by_key_name(offer_key)
    if offer != None:
      offer_exists = True
      offer.from_sid   = from_sid
      offer.from_name  = user["name"]
      offer.from_uid   = from_uid
      offer.from_hands = [int(self.request.get("hand1")),
                          int(self.request.get("hand2")),
                          int(self.request.get("hand3"))]
      offer.to_sid     = to_sid
      offer.to_uid     = to_uid
      offer.to_name    = self.request.get("name")
      offer.prize      = self.request.get("prize", "")
      offer.status     = 0
    else:
      offer = tanarky.model.Offer(
        key_name   = offer_key,
        from_sid   = from_sid,
        from_name  = user["name"],
        from_uid   = from_uid,
        from_hands = [int(self.request.get("hand1")),
                      int(self.request.get("hand2")),
                      int(self.request.get("hand3"))],
        to_sid     = to_sid,
        to_uid     = to_uid,
        to_name    = self.request.get("name"),
        prize      = self.request.get("prize", ""),
        status     = 0
        )
    offer.put()
    offerk = offer.key()
    logging.info(offerk.id())
    logging.info(offerk.name())

    """
    to_userが存在したら、alertに登録
    """
    if to_user_exists == True:
      link  = "/receive?offer=%s" % urllib.quote(offer_key)
      title = u"あなたに挑戦状が届いています"
      body  = u"%sさんから挑戦状が届いています。" % offer.from_name
      if offer.prize != "":
        body += u"賞品は「%s」です!" % offer.prize

      alert = tanarky.model.Alert(
        sid   = to_sid,
        uid   = to_uid,
        offer = offerk.name(),
        link  = link,
        title = title,
        body  = body,
        )
      alert.put()

    """
    offerがあったことをtwitterに投稿
    """
    user_model = helper.get_user_by_twitter_uid(user["uid2"])
    logging.error(user_model)
    client = self.get_oauth_client("twitter")
    client.tweet(user_model.token2,
                 user_model.secret2,
                 u"@%s じゃんけんしようぜ。%s" % (self.request.get("name"),
                                                  "http://janken.example.com/"))
    """
    表示用メッセージ登録して/twitterにリダイレクト
    """
    msg_cookie = tanarky.cookie.Message()
    msg_str = msg_cookie.encode(body="申し込みを受け付けました")
    msg_cookie.set(value=msg_str,
                   headers=self.response.headers._headers)
    return self.redirect("/twitter");

class PageFacebookOffer(PageBase):
  def get(self):
    user = self.decode_u_cookie()
    if user == None:
      return self.redirect("/");

    tmpl_vars = {}
    tmpl_vars["name"] = user["name"]
    path = os.path.join(os.path.dirname(__file__),
                        'templates/challenge.html')
    self.response.out.write(template.render(path,
                                            tmpl_vars))
    return

class PageReject(PageBase):
  def get(self):
    user = self.decode_u_cookie()
    if user == None:
      return self.redirect("/");

    # do something
    return self.redirect("/");

class PageTwitter(PageBase):
  def get(self):
    # 
    # user cookie check
    # 
    user = self.decode_u_cookie()
    if user == None or user.has_key("uid2") == False:
      return self.redirect("/login/twitter")
    logging.info(user)

    #
    # 必要な変数定義
    #
    helper = tanarky.Helper()
    client = self.get_oauth_client("twitter")

    friend_uids_key = "friend_uids_twitter_%s" % user["uid2"]
    fids = memcache.get(friend_uids_key)
    user_model = None
    if fids == None:
      user_model = helper.get_user_by_twitter_uid(user["uid2"])
      if user_model == None:
        return self.redirect("/logout");

      res = client.make_request("https://api.twitter.com/1/friends/ids.json",
                                token=user_model.token2,
                                secret=user_model.secret2,
                                additional_params={"user_id":user["uid2"]},
                                protected=True)

      logging.info(res.headers)
      logging.info(res.content)

      fids = simplejson.loads(res.content)
      memcache.set(friend_uids_key,
                   fids,
                   int(tanarky.config.get("cache", "friend_uids")))
    else:
      logging.debug("friend_ids cache hit.")

    try:
      page = int(self.request.get("page", "1"))
      if page < 1:
        page = 1
    except ValueError:
      logging.debug("value error")
      page = 1

    logging.info(fids)
    need_ids = fids[(10*(page-1)):(10*page)]
    logging.debug(need_ids)
    profs    = []
    no_ids   = []
    for i in need_ids:
      prof_key = "prof_twitter_%s" % i
      prof = memcache.get(prof_key)
      if prof == None:
        no_ids.append(str(i))
      else:
        profs.append(prof)

    f = []
    if len(no_ids) == 0:
      logging.debug("all ids cache hit.")
      f = profs
    else:
      logging.debug("no cache about these ids. %s" % no_ids)
      if user_model == None:
        user_model = helper.get_user_by_twitter_uid(user["uid2"])

      response = client.make_request(
        "https://api.twitter.com/1/users/lookup.json",
        token=user_model.token2,
        secret=user_model.secret2,
        additional_params={"user_id":",".join(no_ids),
                           "include_entities":"0"},
        protected=True)
      r = simplejson.loads(response.content)
      logging.info(response.content)
      logging.info(r)
      cache_dic = {}
      for ff in r:
        logging.info(ff)
        s = "/".join([unicode(ff["id"]),ff["name"],ff["screen_name"]])
        cache_val = {"img":ff["profile_image_url"],
                     "uid":str(ff["id"]),
                     "name":ff["name"],
                     "account":ff["screen_name"],
                     "encoded_name":urllib.quote(ff["name"].encode("utf-8")),
                     "sig":helper.get_params_signature(s),
                     "desc":ff["description"]}
        f.append(cache_val)
        cache_key = "prof_twitter_%s" % ff["id"]
        cache_dic[cache_key] = cache_val
      memcache.set_multi(cache_dic,
                         int(tanarky.config.get("cache", "user_prof")))

    tmpl_vars = {}
    tmpl_vars["name"]    = user["name"]
    tmpl_vars["friends"] = f
    tmpl_vars["message"] = self.get_msg_from_cookie()
    tmpl_vars["alert"]   = self.get_alert(user)
    tmpl_vars["paging"]  = self.get_tmpl_vars_paging(link="/twitter",
                                                     hits=len(fids),
                                                     current=page)
    path = os.path.join(os.path.dirname(__file__),
                        'templates/twitter.html')
    self.response.out.write(template.render(path,
                                            tmpl_vars))
    return

class PageFacebook(PageBase):
  def get(self):
    user = self.decode_u_cookie()
    if user == None or user.has_key("uid1") == False:
      logging.debug("no uid1. redirect to facebook login page")
      return self.redirect("/login/facebook")

    try:
      page = int(self.request.get("page", "1"))
      if page < 1:
        page = 1
    except ValueError:
      logging.debug("value error")
      page = 1

    cache_key = "facebook_online_%s_%d" % (user["uid1"],page)
    friends   = memcache.get(cache_key)

    limit = 10
    if friends == None:
      helper     = tanarky.Helper()
      user_model = helper.get_user_by_facebook_uid(user["uid1"])
      if user_model == None:
        return self.redirect("/login/facebook")

      friends = helper.get_facebook_friends_online(user_model.token1,
                                                   limit=limit,
                                                   page=page)
      cache_dic = {}
      cache_dic[cache_key] = friends
      memcache.set_multi(cache_dic,
                         int(tanarky.config.get("cache", "facebook_online")))
    else:
      logging.info("cache hit")

    #logging.info(friends)

    hits = -1
    if len(friends) == limit + 1:
      friends.pop()
      hits = 0
    logging.debug("len %d" % len(friends))

    tmpl_vars = {}
    tmpl_vars["name"] = user["name"]
    tmpl_vars["friends"] = friends
    tmpl_vars["paging"]  = self.get_tmpl_vars_paging(link="/facebook",
                                                     hits=hits,
                                                     current=page)

    path = os.path.join(os.path.dirname(__file__),
                        'templates/facebook.html')
    self.response.out.write(template.render(path,
                                            tmpl_vars))

class PageHome(PageBase):
  def get(self):
    user = self.decode_u_cookie()
    tmpl_vars = {}

    if user == None:
      tmpl_path = self.get_tmpl_path('guest')
      tmpl_vars["name"] = "ゲスト"
    else:
      tmpl_path = self.get_tmpl_path('home')
      tmpl_vars["name"]    = user["name"]
      tmpl_vars["from_results"] = self.get_results_by_from_user(user)
      tmpl_vars["to_results"]   = self.get_results_by_to_user(user)

    self.response.out.write(template.render(tmpl_path,tmpl_vars))
    return

#
# 1. querystringにoauth_token,oauth_verifierがない場合(1回目アクセス)
#
#    1.1 self.request_urlにアクセスして、oauth_token+oauth_token_secretを取得
#    1.2 oauth_tokenをkey,oauth_token_secretをvalueにしてmemcacheに保存
#    1.3 authorization_url(oauth_tokenのみが必要なURL)にリダイレクト
#
# 2. querystringにoauth_token,oauth_verifierがある場合(2回目アクセス)
#
#    2.1 oauth_tokenをもとにmemcacheからoauth_token_secretを取得
#    2.2 oauth_token,oauth_token_secret,oauth_verifierの3つをリクエストに付与して、self.access_urlに送信
#    2.3 responseに含まれる(access_)token,(access_)secretをDBに保存する
#
class LoginTwitter(PageBase):
  def get(self):
    c = tanarky.cookie.User()

    client        = self.get_oauth_client("twitter")
    auth_token    = self.request.get("oauth_token")
    auth_verifier = self.request.get("oauth_verifier")

    if not auth_token:
      return self.redirect(client.get_authorization_url())

    # login成功
    prof = client.get_user_info(auth_token,auth_verifier)
    logging.debug(prof)

    user = self.decode_u_cookie()
    sid  = None
    uid  = None
    uid2 = unicode(prof["id"])
    #
    # Cookieを持っていない場合
    #
    if user == None:
      logging.debug("no cookie")
      sid  = 2
      uid  = uid2
      user = {
        "main_sid": sid,
        "name": unicode(prof["name"]),
        "uid2": uid2,
      }
      user_model = tanarky.model.User(
        key_name = "%d-%s" % (sid,uid),
        main_sid = sid,
        name     = user["name"],
        uid2     = uid2,
        token2   = unicode(prof["token"]),
        secret2  = unicode(prof["secret"]),
        )
    #
    # すでにCookieを持っている場合
    #
    else:
      logging.debug("cookie exists")
      user["uid2"] = uid2
      sid = user["main_sid"]
      uid = user["uid%d" % sid]
      user_model = tanarky.model.User.get_by_key_name("%d-%s" % (sid, uid))
      user_model.uid2    = uid2
      user_model.token2  = unicode(prof["token"])
      user_model.secret2 = unicode(prof["secret"])
      # FIXME: merge
      if user_model.main_sid != 2:
        pass

    # Userデータ登録
    user_model.put()

    user_cookie = tanarky.cookie.User()
    cookie_str  = user_cookie.encode(**user)
    user_cookie.set(value=cookie_str,
                    headers=self.response.headers._headers)

    redirect_to = self.request.get("rd", "/twitter")
    return self.redirect(redirect_to)

#
# 1. querystringにcodeがない場合(1回目アクセス)
#    1.1 /oauth/authorizeに必要パラメータをつけてリダイレクト
# 2. querystringにcodeがある場合(2回目アクセス)
#    2.1 必要パラメータに、codeとAPP_SECRETをつけて、/oauth/access_tokenにリクエスト
#    2.2 レスポンスのaccess_tokenを保存
#
class LoginFacebook(PageBase):
  def get(self):
    client = self.get_oauth_client("facebook")
    code   = self.request.get("code")
    scope  = tanarky.config.get("facebook_test", "scope")

    if not code:
      return self.redirect(client.get_authorization_url(scope))

    access_token = client.get_access_token(code, scope)
    prof = client.lookup_user_info(access_token)

    user = self.decode_u_cookie()
    sid  = None
    uid  = None
    uid1 = unicode(prof["id"])
    #
    # Cookieを持っていない場合
    #
    if user == None:
      logging.debug("no cookie")
      sid  = 1
      uid  = uid1
      user = {
        "main_sid": sid,
        "name": unicode(prof["name"]),
        "uid1": uid1,
      }
      user_model = tanarky.model.User(
        key_name = "%d-%s" % (sid,uid),
        main_sid = sid,
        name     = user["name"],
        uid1     = uid,
        token1   = access_token)
    #
    # すでにCookieを持っている場合
    #
    else:
      logging.debug("cookie exists")
      user["uid1"] = uid1
      sid = user["main_sid"]
      uid = user["uid%d" % sid]
      user_model = tanarky.model.User.get_by_key_name("%d-%s" % (sid, uid))
      if user_model == None:
        return self.redirect("/logout")
      user_model.uid1   = uid1
      user_model.token1 = access_token
      if user_model.main_sid != 1:
        # FIXME: merge
        pass

    # Userデータ登録
    user_model.put()

    user_cookie = tanarky.cookie.User()
    cookie_str  = user_cookie.encode(**user)
    user_cookie.set(value=cookie_str,
                    headers=self.response.headers._headers)

    redirect_to = self.request.get("rd", "/facebook")
    return self.redirect(redirect_to)

class Logout(PageBase):
  def get(self):
    c = tanarky.cookie.User()
    c.clear(self.response.headers._headers)
    return self.redirect("/");

class Error(PageBase):
  def get(self):
    self.error(404)
    self.response.out.write('error')

