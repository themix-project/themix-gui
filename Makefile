SASS=scss
SASSFLAGS=--sourcemap=none
GLIB_COMPILE_RESOURCES=glib-compile-resources
RES_DIR=gtk-3.0
SCSS_DIR=$(RES_DIR)/scss
DIST_DIR=$(RES_DIR)/dist
RES_DIR320=gtk-3.20
SCSS_DIR320=$(RES_DIR320)/scss
DIST_DIR320=$(RES_DIR320)/dist
INSTALL_DIR=$(DESTDIR)/usr/share/themes/Numix

all: clean gresource

css:
	$(SASS) --update $(SASSFLAGS) $(SCSS_DIR):$(DIST_DIR)
	$(SASS) --update $(SASSFLAGS) $(SCSS_DIR320):$(DIST_DIR320)

gresource: css
	$(GLIB_COMPILE_RESOURCES) --sourcedir=$(RES_DIR) $(RES_DIR)/gtk.gresource.xml
	$(GLIB_COMPILE_RESOURCES) --sourcedir=$(RES_DIR320) $(RES_DIR320)/gtk.gresource.xml

watch: clean
	while true; do \
		make gresource; \
		inotifywait @gtk.gresource -qr -e modify -e create -e delete $(RES_DIR); \
	done

clean:
	rm -rf $(DIST_DIR)
	rm -f $(RES_DIR)/gtk.gresource
	rm -rf $(DIST_DIR320)
	rm -f $(RES_DIR320)/gtk.gresource

install: all
	install -d -m755 $(INSTALL_DIR)

	mkdir -p			$(INSTALL_DIR)/gtk-3.0
	mkdir -p			$(INSTALL_DIR)/gtk-3.20
	cp -pr gtk-2.0			$(INSTALL_DIR)
	cp -p  gtk-3.0/gtk.css		$(INSTALL_DIR)/gtk-3.0
	cp -p  gtk-3.0/gtk-dark.css	$(INSTALL_DIR)/gtk-3.0
	cp -p  gtk-3.0/gtk.gresource	$(INSTALL_DIR)/gtk-3.0
	cp -p  gtk-3.0/thumbnail.png	$(INSTALL_DIR)/gtk-3.0
	cp -p  gtk-3.20/gtk.css		$(INSTALL_DIR)/gtk-3.20
	cp -p  gtk-3.20/gtk-dark.css	$(INSTALL_DIR)/gtk-3.20
	cp -p  gtk-3.20/gtk.gresource	$(INSTALL_DIR)/gtk-3.20
	cp -p  gtk-3.20/thumbnail.png	$(INSTALL_DIR)/gtk-3.20
	cp -pr metacity-1		$(INSTALL_DIR)
	cp -pr openbox-3		$(INSTALL_DIR)
	cp -pr xfce-notify-4.0		$(INSTALL_DIR)
	cp -pr xfwm4			$(INSTALL_DIR)
	cp -pr unity			$(INSTALL_DIR)
	cp -p  index.theme		$(INSTALL_DIR)

uninstall:
	rm -rf $(INSTALL_DIR)

.PHONY: all
.PHONY: css
.PHONY: watch
.PHONY: gresource
.PHONY: clean
.PHONY: install
.PHONY: uninstall

.DEFAULT_GOAL := all

# vim: set ts=4 sw=4 tw=0 noet :
