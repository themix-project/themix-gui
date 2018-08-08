DESTDIR = ./distrib
PREFIX = /opt/oomox

DISABLE_PLUGIN_MATERIA = 0
DISABLE_PLUGIN_SPOTIFY = 0
DISABLE_PLUGIN_ARC = 0


.PHONY: install
install:
	$(eval APP_DIR := $(DESTDIR)$(PREFIX))
	$(eval PACKAGING_TMP_DIR := $(shell mktemp -d))

	mkdir -p $(APP_DIR)
	cp -prf \
		CREDITS \
		LICENSE \
		README.md \
		colors \
		gui.sh \
		oomox_gui \
		plugins \
		po \
		po.mk \
		terminal_templates \
			$(APP_DIR)/

	$(RM) -r "$(APP_DIR)/plugins/oomoxify/".git*
	$(RM) -r "$(APP_DIR)/plugins"/*/*/.git*
	$(RM) -r "$(APP_DIR)/plugins/theme_oomox/gtk-theme/".editorconfig
	$(RM) -r "$(APP_DIR)/plugins/theme_oomox/gtk-theme/".*.yml
	$(RM) -r "$(APP_DIR)/plugins/theme_oomox/gtk-theme/"{D,d}ocker*
	$(RM) -r "$(APP_DIR)/plugins/theme_oomox/gtk-theme/"maintenance*
	$(RM) -r "$(APP_DIR)/plugins/theme_oomox/gtk-theme/"screenshot*
	$(RM) -r "$(APP_DIR)/plugins/theme_oomox/gtk-theme/"test*

ifeq ($(DISABLE_PLUGIN_MATERIA), 1)
	$(RM) -r $(APP_DIR)/plugins/theme_materia/
endif
ifeq ($(DISABLE_PLUGIN_SPOTIFY), 1)
	$(RM) -r $(APP_DIR)/plugins/oomoxify/
endif
ifeq ($(DISABLE_PLUGIN_ARC), 1)
	$(RM) -r $(APP_DIR)/plugins/theme_arc/
endif

	cp -prf \
		packaging/ \
			$(PACKAGING_TMP_DIR)/
	sed -i -e 's|/opt/oomox/|$(PREFIX)/|g' $(PACKAGING_TMP_DIR)/packaging/bin/*

	install -Dp -m 755 --target-directory="$(DESTDIR)/usr/bin/" "$(PACKAGING_TMP_DIR)/packaging/bin/"*

	install -d $(DESTDIR)/usr/share/applications/
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox.desktop" "$(DESTDIR)/usr/share/applications/"

	install -d $(DESTDIR)/usr/share/appdata/
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox.appdata.xml" "$(DESTDIR)/usr/share/appdata/"

	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-symbolic.svg" "$(DESTDIR)/usr/share/icons/hicolor/symbolic/apps/com.github.themix_project.Oomox-symbolic.svg"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-16.png" "$(DESTDIR)/usr/share/icons/hicolor/16x16/apps/com.github.themix_project.Oomox.png"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-24.png" "$(DESTDIR)/usr/share/icons/hicolor/24x24/apps/com.github.themix_project.Oomox.png"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-32.png" "$(DESTDIR)/usr/share/icons/hicolor/32x32/apps/com.github.themix_project.Oomox.png"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-48.png"  "$(DESTDIR)/usr/share/icons/hicolor/48x48/apps/com.github.themix_project.Oomox.png"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-512.png" "$(DESTDIR)/usr/share/icons/hicolor/512x512/apps/com.github.themix_project.Oomox.png"

	$(RM) -r $(PACKAGING_TMP_DIR)

	cd $(APP_DIR)
	# will update ./po and produce ./locale dir:
	make -f po.mk install
	rm $(APP_DIR)/po.mk

all: install
