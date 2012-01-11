.PHONY: all

CONF := /etc/tanarky/leo/leo.conf
HOST := $(shell python -c 'from ConfigParser import ConfigParser as C;c=C();c.read("$(CONF)");print c.get("server","host")')
PORT := $(shell python -c 'from ConfigParser import ConfigParser as C;c=C();c.read("$(CONF)");print c.get("server","port")')

all: 
	python bootstrap.py --distribute && bin/buildout

clean:
	rm -rf bin/ develop-eggs/ eggs/ parts/ *.egg-info/ .installed.cfg
	find . -name "*.pyc" -or -name "*~" | perl -nle unlink

update_buildout:
	wget "http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py"

server:
	python tanarky-leo/main.py

deploy:
	rsync -av -e "ssh -p $(PORT)" --delete scripts tanarky-leo $(HOST):/usr/share/tanarky/leo/

