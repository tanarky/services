.PHONY: all

all: 
	python bootstrap.py --distribute && bin/buildout

clean:
	rm -rf bin/ develop-eggs/ eggs/ parts/ *.egg-info/ .installed.cfg downloads/
	find . -name "*.pyc" -or -name "*~" | perl -nle unlink

server:
	bin/dev_appserver --enable_sendmail app/

update_buildout:
	wget "http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py"

