
import os
import logging

for x in range(0,256):
    for y in range(0,256):
        try:
            os.makedirs('/var/tanarky/leo/%02x/%02x' % (x,y))
        except:
            #logging.error('exception')
            pass

#os.mkdir('/tmp/foo')
