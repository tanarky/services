import ConfigParser, os, logging, urllib, urllib2, time, hmac, cgi, Cookie, email
import db, oauth
import tanarky.test

config = ConfigParser.ConfigParser()
config.read('oauth.password')

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from django.utils import translation,simplejson
from django.conf  import settings
from google.appengine.ext.webapp.util import run_wsgi_app

class BaseHandler(webapp.RequestHandler):
  @property
  def current_user(self):
    """Returns the logged in Facebook user, or None if unconnected."""
    if not hasattr(self, "_current_user"):
      self._current_user = None
      cookie_val = self.parse_cookie()
      if cookie_val:
        keystr = "|".join([cookie_val[0], cookie_val[1]])
        self._current_user = db.User.get_by_key_name(keystr)
      return self._current_user
  def parse_cookie(self):
    value = self.request.cookies.get("U")
    if not value: return None
    parts = value.split("|")
    if len(parts) != 2: return None
    return parts

class Home(BaseHandler):
  def get(self):
    template_values = {}
    user = self.current_user

    if user == None:
      path = os.path.join(os.path.dirname(__file__), 'guest.html')
      self.response.out.write(template.render(path, template_values))
      return

      keystr = "|".join([str(site_id),str(user_id)])
      user = db.User(key_name = keystr,
                     site_id  = site_id,
                     id       = int(user_id),
                     fb_name  = prof["name"],
                     fb_token = access_token)

    logging.info("site %s" % user.site_id);
    logging.info("user %s" % user.id);
    template_values["name"] = user.ya_name

    path = os.path.join(os.path.dirname(__file__), 'home.html')
    self.response.out.write(template.render(path, template_values))
    return

  def post(self):
    self.redirect("/");

class Logout(BaseHandler):
  def get(self):
    #set_cookie(self.response, "U", "", expires=time.time() - 86400)
    cookie = Cookie.BaseCookie()
    cookie["U"] = ""
    cookie["U"]["path"] = "/"
    cookie["U"]["expires"] = email.utils.formatdate(time.time() - 86400,
                                                    localtime=False,
                                                    usegmt=True)
    logging.info(cookie.output())
    self.response.headers._headers.append(("Set-Cookie", cookie.output()[12:]))
    self.redirect("/")

class FacebookLogin(BaseHandler):
  def get(self):
    verification_code = self.request.get("code")
    args = dict(client_id=config.get("facebook_test", "app_id"),
                redirect_uri=self.request.path_url,
                scope=",".join(["email",
                                "read_stream",
                                "publish_stream",
                                "offline_access"]))
    if verification_code:
      args["client_secret"] = config.get("facebook_test", "app_secret")
      args["code"] = verification_code
      logging.info(args);
      # FIXME: try except
      response = cgi.parse_qs(urllib2.urlopen(
          "https://graph.facebook.com/oauth/access_token?" +
          urllib.urlencode(args)).read())
      #logging.info(response);
      access_token = response["access_token"][-1]

      # get facebook user profile
      prof_api    = "https://graph.facebook.com/me?"
      prof_params = urllib.urlencode(dict(access_token=access_token))
      prof        = simplejson.load(urllib2.urlopen(prof_api + prof_params))
      logging.info(prof);

      # get user_id
      idmap = db.FacebookId2User.get_by_key_name(prof["id"])
      if idmap:
        user_id = idmap.user_id
        site_id = idmap.site_id
        logging.info("found idmap: facebookid is %s, user_id is %s",
                     idmap.id,
                     idmap.user_id)
      else:
        logging.info("NOT found idmap: %s", prof["id"])
        user_id = prof["id"]
        site_id = 1
        fid2uid = db.FacebookId2User(key_name = str(prof["id"]),
                                     id       = int(prof["id"]),
                                     site_id  = site_id,
                                     user_id  = int(prof["id"]))
        fid2uid.put()

      #logging.info("saving user: %s, %s", user_id, prof["name"])
      keystr = "|".join([str(site_id),str(user_id)])
      user = db.User(key_name = keystr,
                     site_id  = site_id,
                     id       = int(user_id),
                     fb_name  = prof["name"],
                     fb_token = access_token)
      user.put()

      # cookie save
      cookie = Cookie.BaseCookie()
      cookie["U"] = keystr
      cookie["U"]["path"] = "/"
      cookie["U"]["expires"] = email.utils.formatdate(time.time() + 30 * 86400,
                                                      localtime=False,
                                                      usegmt=True)
      self.response.headers._headers.append(("Set-Cookie", cookie.output()[12:]))
      self.redirect("/")
    else:
      self.redirect(
        "https://graph.facebook.com/oauth/authorize?" +
        urllib.urlencode(args))

class TwitterLogin(BaseHandler):
  def get(self):
    application_key = "FFPFZ8ai4ivvSE3QlTKRQ"
    application_secret = "bCh0IYf5lZSFB2uwnMhwPl3j9ZIJW59xBcTctsvncD4"

    callback = self.request.path_url
    client   = oauth.TwitterClient(application_key,
                                   application_secret,
                                   callback)

    auth_token    = self.request.get("oauth_token")
    auth_verifier = self.request.get("oauth_verifier")

    if not auth_token:
      return self.redirect(client.get_authorization_url())

    logging.info("token : %s" % auth_token)
    logging.info("secret: %s" % auth_verifier)

    prof = client.get_user_info(auth_token,
                                auth_verifier=auth_verifier)

    logging.info("prof [%s]" % prof)

    # get user_id
    idmap = db.TwitterId2User.get_by_key_name(str(prof["id"]))
    if idmap:
      site_id = idmap.site_id
      user_id = idmap.user_id
      logging.info("found idmap: twitter is %s, user_id is %s",
                   idmap.id,
                   idmap.user_id)
    else:
      logging.info("NOT found idmap: %s", prof["id"])
      site_id = 2 # twitter site id
      user_id = prof["id"]
      twid2uid = db.TwitterId2User(key_name = str(prof["id"]),
                                   id       = int(prof["id"]),
                                   site_id  = site_id,
                                   user_id  = int(prof["id"]))
      twid2uid.put()
      logging.info("saving user: %s, %s", user_id, prof["name"])

    keystr      = "|".join([str(site_id), str(user_id)])
    cookie      = Cookie.BaseCookie()
    cookie["U"] = keystr
    cookie["U"]["path"] = "/"
    cookie["U"]["expires"] = email.utils.formatdate(time.time() + 30 * 86400,
                                                    localtime=False,
                                                    usegmt=True)
    self.response.headers._headers.append(("Set-Cookie", cookie.output()[12:]))

    user = db.User(key_name  = keystr,
                   site_id   = site_id,
                   id        = str(prof["id"]),
                   tw_name   = prof["name"],
                   tw_token  = prof["token"],
                   tw_secret = prof["secret"])
    user.put()
    self.redirect("/")

class YahooLogin(BaseHandler):
  def get(self):
    application_key = "dj0yJmk9Q0RtQXZ2Rko3eGNyJmQ9WVdrOU4yRjJVMkZSTm1zbWNHbzlNemcwTURNeE9EZ3gmcz1jb25zdW1lcnNlY3JldCZ4PWEy"
    application_secret = "5f81fef94a8d575c7e1308ddffdf7500ea67d134"

    callback = self.request.path_url
    client   = oauth.YahooClient(application_key,
                                 application_secret,
                                 callback)

    auth_token    = self.request.get("oauth_token")
    auth_verifier = self.request.get("oauth_verifier")

    if not auth_token:
      return self.redirect(client.get_authorization_url())

    logging.info("token : %s" % auth_token)
    logging.info("secret: %s" % auth_verifier)

    prof = client.get_user_info(auth_token,
                                auth_verifier=auth_verifier)

    logging.info("prof [%s]" % prof)
    site_id = 3
    user_id = prof["id"]
    keystr      = "|".join([str(site_id), str(user_id)])
    cookie      = Cookie.BaseCookie()
    cookie["U"] = keystr
    cookie["U"]["path"] = "/"
    cookie["U"]["expires"] = email.utils.formatdate(time.time() + 30 * 86400,
                                                    localtime=False,
                                                    usegmt=True)
    self.response.headers._headers.append(("Set-Cookie", cookie.output()[12:]))

    user = db.User(key_name  = keystr,
                   site_id   = site_id,
                   id        = str(prof["id"]),
                   ya_name   = prof["name"],
                   ya_token  = prof["token"],
                   ya_secret = prof["secret"])
    user.put()
    self.redirect("/")

application = webapp.WSGIApplication(
                                     [(r'/',                  Home),
                                      (r'/test',              tanarky.test.foo),
                                      (r"/facebook/login",    FacebookLogin),
                                      (r"/yahoo/login",       YahooLogin),
                                      (r"/twitter/login",     TwitterLogin),
                                      (r"/logout",            Logout)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
