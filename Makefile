DESTDIR = ./distrib
PREFIX = /usr
APPDIR = /opt/oomox

DISABLE_PLUGIN_MATERIA = 0
DISABLE_PLUGIN_ARC = 0
DISABLE_PLUGIN_SPOTIFY = 0
DISABLE_PLUGIN_IMPORT_IMAGE = 0


.PHONY: install
install:
	$(eval DEST_APPDIR := $(DESTDIR)$(APPDIR))
	$(eval DEST_PREFIX := $(DESTDIR)$(PREFIX))
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
		plugins \
		po \
		po.mk \
		terminal_templates \
			$(DEST_APPDIR)/

	$(RM) -r "$(DEST_APPDIR)/plugins/oomoxify/".git*
	$(RM) -r "$(DEST_APPDIR)/plugins"/*/*/.git*
	$(RM) -r "$(DEST_APPDIR)/plugins/theme_oomox/gtk-theme/".editorconfig
	$(RM) -r "$(DEST_APPDIR)/plugins/theme_oomox/gtk-theme/".*.yml
	$(RM) -r "$(DEST_APPDIR)/plugins/theme_oomox/gtk-theme/"{D,d}ocker*
	$(RM) -r "$(DEST_APPDIR)/plugins/theme_oomox/gtk-theme/"maintenance*
	$(RM) -r "$(DEST_APPDIR)/plugins/theme_oomox/gtk-theme/"screenshot*
	$(RM) -r "$(DEST_APPDIR)/plugins/theme_oomox/gtk-theme/"test*

	cp -prf \
		packaging/ \
			$(PACKAGING_TMP_DIR)/

ifeq ($(DISABLE_PLUGIN_MATERIA), 1)
	$(RM) -r $(DEST_APPDIR)/plugins/theme_materia/
	$(RM) $(PACKAGING_TMP_DIR)/packaging/bin/oomox-materia-cli
endif
ifeq ($(DISABLE_PLUGIN_ARC), 1)
	$(RM) -r $(DEST_APPDIR)/plugins/theme_arc/
endif
ifeq ($(DISABLE_PLUGIN_SPOTIFY), 1)
	$(RM) -r $(DEST_APPDIR)/plugins/oomoxify/
	$(RM) $(PACKAGING_TMP_DIR)/packaging/bin/oomoxify-cli
endif
ifeq ($(DISABLE_PLUGIN_IMPORT_IMAGE), 1)
	$(RM) -r $(DEST_APPDIR)/plugins/import_pil/
endif

	sed -i -e 's|/opt/oomox/|$(APPDIR)/|g' $(PACKAGING_TMP_DIR)/packaging/bin/*

	chmod a+x "$(PACKAGING_TMP_DIR)/packaging/bin/"*
	install -Dp -m 755 --target-directory="$(DEST_PREFIX)/bin/" "$(PACKAGING_TMP_DIR)/packaging/bin/"*

	install -d $(DEST_PREFIX)/share/applications/
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox.desktop" "$(DEST_PREFIX)/share/applications/"

	install -d $(DEST_PREFIX)/share/appdata/
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox.appdata.xml" "$(DEST_PREFIX)/share/appdata/"

	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-symbolic.svg" "$(DEST_PREFIX)/share/icons/hicolor/symbolic/apps/com.github.themix_project.Oomox-symbolic.svg"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-16.png" "$(DEST_PREFIX)/share/icons/hicolor/16x16/apps/com.github.themix_project.Oomox.png"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-24.png" "$(DEST_PREFIX)/share/icons/hicolor/24x24/apps/com.github.themix_project.Oomox.png"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-32.png" "$(DEST_PREFIX)/share/icons/hicolor/32x32/apps/com.github.themix_project.Oomox.png"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-48.png"  "$(DEST_PREFIX)/share/icons/hicolor/48x48/apps/com.github.themix_project.Oomox.png"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-512.png" "$(DEST_PREFIX)/share/icons/hicolor/512x512/apps/com.github.themix_project.Oomox.png"

	$(RM) -r $(PACKAGING_TMP_DIR)

	cd $(DEST_APPDIR)
	# will update ./po and produce ./locale dir:
	make -f po.mk install
	rm $(DEST_APPDIR)/po.mk

all: install
