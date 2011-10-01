import ConfigParser, os, logging
import tanarky.model
import tanarky.oauth

#logging.info("read conf __init__")

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__),
                         'oauth.password'))

class Helper():
    def get_user_by_twitter_uid(self, uid):
        return tanarky.model.User.gql("WHERE twitter_uid = :1",uid).get()
