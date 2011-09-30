import ConfigParser, os, logging
#logging.info("read conf __init__")

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__),
                         'oauth.password'))
