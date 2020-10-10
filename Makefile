DESTDIR = ./distrib
PREFIX = /usr
APPDIR = /opt/oomox

DEST_APPDIR = $(DESTDIR)$(APPDIR)
DEST_PLUGIN_DIR = $(DESTDIR)$(APPDIR)/plugins
DEST_PREFIX = $(DESTDIR)$(PREFIX)


install_gui: install_import_random
	$(eval PACKAGING_TMP_DIR := $(shell mktemp -d))

	mkdir -p $(DEST_APPDIR)
	cp -prf \
		CREDITS \
		LICENSE \
		README.md \
		scripted_colors \
		colors \
		gui.sh \
		oomox_gui \
		po \
		po.mk \
		terminal_templates \
			$(DEST_APPDIR)/

	cp -prf \
		packaging/ \
			$(PACKAGING_TMP_DIR)/
	sed -i -e 's|/opt/oomox/|$(APPDIR)/|g' $(PACKAGING_TMP_DIR)/packaging/bin/*
	chmod a+x "$(PACKAGING_TMP_DIR)/packaging/bin/"*

	install -d $(DEST_PREFIX)/bin/
	install -Dp -m 755 "$(PACKAGING_TMP_DIR)/packaging/bin/oomox-gui" "$(DEST_PREFIX)/bin/"
	install -Dp -m 755 "$(PACKAGING_TMP_DIR)/packaging/bin/themix-gui" "$(DEST_PREFIX)/bin/"

	install -d $(DEST_PREFIX)/share/applications/
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox.desktop" "$(DEST_PREFIX)/share/applications/"

	install -d $(DEST_PREFIX)/share/appdata/
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox.appdata.xml" "$(DEST_PREFIX)/share/appdata/"

	install -d $(DEST_PREFIX)/share/icons/hicolor/symbolic/apps/
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-symbolic.svg" "$(DEST_PREFIX)/share/icons/hicolor/symbolic/apps/com.github.themix_project.Oomox-symbolic.svg"

	install -d $(DEST_PREFIX)/share/icons/hicolor/scalable/apps/
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox.svg" "$(DEST_PREFIX)/share/icons/hicolor/scalable/apps/com.github.themix_project.Oomox.svg"

	$(RM) -r $(PACKAGING_TMP_DIR)

	# will update ./po and produce ./locale dir:
	make -C $(DEST_APPDIR) -f po.mk install
	rm $(DEST_APPDIR)/po.mk


install_theme_arc:
	$(eval PLUGIN_NAME := "theme_arc")

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


install_theme_oomox:
	$(eval PLUGIN_NAME := "theme_oomox")
	make -C plugins/$(PLUGIN_NAME) -f Makefile_oomox_plugin DESTDIR=$(DESTDIR)  APPDIR=$(APPDIR) PREFIX=$(PREFIX) install


install_theme_materia:
	$(eval PLUGIN_NAME := "theme_materia")
	$(eval CLI_NAME := "oomox-materia-cli")
	$(eval PACKAGING_TMP_DIR := $(shell mktemp -d))

	cp -prf \
		packaging/ \
			$(PACKAGING_TMP_DIR)/
	sed -i -e 's|/opt/oomox/|$(APPDIR)/|g' $(PACKAGING_TMP_DIR)/packaging/bin/*
	chmod a+x "$(PACKAGING_TMP_DIR)/packaging/bin/"*
	install -d $(DEST_PREFIX)/bin/
	install -Dp -m 755 "$(PACKAGING_TMP_DIR)/packaging/bin/$(CLI_NAME)" "$(DEST_PREFIX)/bin/"

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


install_export_oomoxify:
	$(eval PLUGIN_NAME := "oomoxify")
	make -C plugins/$(PLUGIN_NAME) -f Makefile_oomox_plugin DESTDIR=$(DESTDIR)  APPDIR=$(APPDIR) PREFIX=$(PREFIX) install


install_import_random:
	$(eval PLUGIN_NAME := "import_random")

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/


install_import_xresources:
	$(eval PLUGIN_NAME := "import_xresources")

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/


install_import_images:
	$(eval PLUGIN_NAME := "import_pil")

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/


install_plugin_base16:
	$(eval PLUGIN_NAME := "base16")
	make -C plugins/$(PLUGIN_NAME) -f Makefile_oomox_plugin DESTDIR=$(DESTDIR)  APPDIR=$(APPDIR) PREFIX=$(PREFIX) install


install_icons_archdroid:
	$(eval PLUGIN_NAME := "icons_archdroid")
	$(eval CLI_NAME := "oomox-archdroid-icons-cli")
	$(eval PACKAGING_TMP_DIR := $(shell mktemp -d))

	cp -prf \
		packaging/ \
			$(PACKAGING_TMP_DIR)/
	sed -i -e 's|/opt/oomox/|$(APPDIR)/|g' $(PACKAGING_TMP_DIR)/packaging/bin/*
	chmod a+x "$(PACKAGING_TMP_DIR)/packaging/bin/"*
	install -d $(DEST_PREFIX)/bin/
	install -Dp -m 755 "$(PACKAGING_TMP_DIR)/packaging/bin/$(CLI_NAME)" "$(DEST_PREFIX)/bin/"

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


install_icons_gnomecolors:
	$(eval PLUGIN_NAME := "icons_gnomecolors")
	$(eval CLI_NAME := "oomox-gnome-colors-icons-cli")
	$(eval PACKAGING_TMP_DIR := $(shell mktemp -d))

	cp -prf \
		packaging/ \
			$(PACKAGING_TMP_DIR)/
	sed -i -e 's|/opt/oomox/|$(APPDIR)/|g' $(PACKAGING_TMP_DIR)/packaging/bin/*
	chmod a+x "$(PACKAGING_TMP_DIR)/packaging/bin/"*
	install -d $(DEST_PREFIX)/bin/
	install -Dp -m 755 "$(PACKAGING_TMP_DIR)/packaging/bin/$(CLI_NAME)" "$(DEST_PREFIX)/bin/"

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


install_icons_numix:
	$(eval PLUGIN_NAME := "icons_numix")

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


install_icons_papirus:
	$(eval PLUGIN_NAME := "icons_papirus")

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


install_icons_suruplus:
	$(eval PLUGIN_NAME := "icons_suruplus")

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


install_icons_suruplus_aspromauros:
	$(eval PLUGIN_NAME := "icons_suruplus_aspromauros")

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


.PHONY: install
.PHONY: install_gui install_import_random install_theme_arc install_theme_oomox install_theme_materia install_export_oomoxify install_import_images install_plugin_base16 install_icons_archdroid install_icons_gnomecolors install_icons_numix install_icons_papirus install_icons_suruplus install_icons_suruplus_aspromauros install_import_xresources
install: install_gui install_theme_oomox install_theme_materia install_export_oomoxify install_import_images install_plugin_base16 install_icons_archdroid install_icons_gnomecolors install_icons_numix install_icons_papirus install_icons_suruplus install_icons_suruplus_aspromauros install_import_xresources

.PHONY: all
all: install
