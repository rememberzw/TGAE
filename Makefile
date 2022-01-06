VERSION=2.0.1
PLATFORM=debian10_all

PYTHON_HOME=/opt/somf/python-somf/bin
INSTALL_HOME=/opt/somf
PREFIX=$(INSTALL_HOME)/tgae
DEB=/root/deb-tgae

all: version
	echo > ./log/agent.log
	echo > ./log/manage.log
	echo > ./log/relay.log
	echo > ./log/run.log
	$(PYTHON_HOME)/python3 -OO -m compileall -b ./*

install:
	mkdir -p $(PREFIX)/agent
	mkdir -p $(PREFIX)/etc
	mkdir -p $(PREFIX)/lib
	mkdir -p $(PREFIX)/log
	mkdir -p $(PREFIX)/manage
	mkdir -p $(PREFIX)/relay
	mkdir -p $(PREFIX)/tools
	cp -r agent/*.pyc $(PREFIX)/agent
	cp -r etc/*.pyc etc/config.py $(PREFIX)/etc
	cp -r lib/*.pyc $(PREFIX)/lib
	cp -r log/*.log $(PREFIX)/log
	cp -r manage/*.pyc $(PREFIX)/manage
	cp -r relay/*.pyc $(PREFIX)/relay
	cp -r relay/ssh_host_rsa_key* $(PREFIX)/relay
	cp -r tools/*.pyc $(PREFIX)/tools
	cp -r *.pyc $(PREFIX)/
	cp -r logging.config $(PREFIX)/

uninstall:
	rm -fr $(PREFIX)
	rm -fr $(DEB)

deb: version
	mkdir -p $(DEB)/DEBIAN
	mkdir -p $(DEB)/lib/systemd/system
	mkdir -p $(DEB)$(INSTALL_HOME)
	cp -r tools/control tools/postinst $(DEB)/DEBIAN
	cp -r tools/tgae.service $(DEB)/lib/systemd/system
	cp -r $(PREFIX) $(DEB)$(INSTALL_HOME)
	dpkg-deb -b $(DEB) tgae-$(VERSION)-$(shell date +%Y%m%d)_$(PLATFORM).deb

version:
	@sed -i '/^Version:/ c\Version: $(VERSION)' tools/vendor_banner
	@sed -i '/^Version:/ c\Version: $(VERSION)-$(shell date +%Y%m%d)' tools/control

clean:
	find . -name '*.pyc' | xargs rm -fr
	find . -name '__pycache__' | xargs rm -fr
	echo > ./log/agent.log
	echo > ./log/manage.log
	echo > ./log/relay.log
	echo > ./log/run.log
