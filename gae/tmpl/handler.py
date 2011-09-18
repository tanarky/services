import ConfigParser, os, logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from django.utils import translation
from django.conf import settings

from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
  def get(self):

    if users.get_current_user():
      user = users.get_current_user()
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
      nickname = user.nickname()
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      nickname = ''

    template_values = {
      'user': nickname,
      'url': url,
      'url_linktext': url_linktext,
      }

    config = ConfigParser.ConfigParser()
    config.read('sample.password')

    template_values["config_user"] = config.get("foo", "user")
    template_values["config_pass"] = config.get("foo", "password")

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
                                     [('/', MainPage)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
