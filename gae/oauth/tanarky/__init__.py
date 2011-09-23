import ConfigParser, os, logging

logging.info("read conf __init__")

oauth = ConfigParser.ConfigParser()
oauth.read(os.path.join(os.path.dirname(__file__),
                        'oauth.password'))
