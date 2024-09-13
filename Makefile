DESTDIR = ./distrib
PREFIX = /usr
APPDIR = /opt/oomox

DEST_APPDIR = $(DESTDIR)$(APPDIR)
DEST_PLUGIN_DIR = $(DESTDIR)$(APPDIR)/plugins
DEST_PREFIX = $(DESTDIR)$(PREFIX)

SHELL := bash
PYTHON := $(shell which python3)
ifeq (,$(PYTHON))
$(error Can't find `python3`)
endif

# lint:
RUFF := ruff
script_dir := $(shell readlink -e .)
APP_DIR := $(shell readlink -e "$(script_dir)")
TARGET_MODULE := oomox_gui
TARGETS := $(APP_DIR)/oomox_gui/ $(shell ls $(APP_DIR)/plugins/*/oomox_plugin.py) $(shell ls $(APP_DIR)/maintenance_scripts/*.py)
GLOBALS_IGNORES := \
			-e ': Final' \
			-e ' \# nonfinal-ignore' \
			-e ' \# checkglobals-ignore' \
			\
			-e TypeVar \
			-e namedtuple \
			-e Generic \
			-e Sequence \
			\
			-e 'BaseClass' \
			-e 'HexColor' \
			-e 'ColorScheme' \
			\
			-e './maintenance_scripts/find_.*.py.*:.*:' \
			-e '.SRCINFO'

################################################################################

.PHONY: all
all: install

################################################################################

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
		export_config_examples \
			$(DEST_APPDIR)/

	cp -prf \
		packaging/ \
			$(PACKAGING_TMP_DIR)/
	sed -i -e 's|/opt/oomox/|$(APPDIR)/|g' $(PACKAGING_TMP_DIR)/packaging/bin/*
	chmod a+x "$(PACKAGING_TMP_DIR)/packaging/bin/"*

	install -Dp -m 755 "$(PACKAGING_TMP_DIR)/packaging/bin/oomox-gui" -t "$(DEST_PREFIX)/bin/"
	install -Dp -m 755 "$(PACKAGING_TMP_DIR)/packaging/bin/themix-gui" -t "$(DEST_PREFIX)/bin/"
	install -Dp -m 755 "$(PACKAGING_TMP_DIR)/packaging/bin/themix-multi-export" -t "$(DEST_PREFIX)/bin/"

	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox.desktop" -t "$(DEST_PREFIX)/share/applications/"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox.appdata.xml" -t "$(DEST_PREFIX)/share/metainfo/"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox-symbolic.svg" -t "$(DEST_PREFIX)/share/icons/hicolor/symbolic/apps/com.github.themix_project.Oomox-symbolic.svg"
	install -Dp -m 644 "$(PACKAGING_TMP_DIR)/packaging/com.github.themix_project.Oomox.svg" -t "$(DEST_PREFIX)/share/icons/hicolor/scalable/apps/com.github.themix_project.Oomox.svg"

	$(RM) -r $(PACKAGING_TMP_DIR)

	# will update ./po and produce ./locale dir:
	make -C $(DEST_APPDIR) -f po.mk install
	rm $(DEST_APPDIR)/po.mk


install_theme_arc:
	$(eval PLUGIN_NAME := theme_arc)

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


install_theme_oomox:
	$(eval PLUGIN_NAME := theme_oomox)
	make -C plugins/$(PLUGIN_NAME) -f Makefile_oomox_plugin DESTDIR=$(DESTDIR)  APPDIR=$(APPDIR) PREFIX=$(PREFIX) install


install_theme_materia:
	$(eval PLUGIN_NAME := theme_materia)
	$(eval CLI_NAME := oomox-materia-cli)
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
	$(eval PLUGIN_NAME := export_oomoxify)
	make -C plugins/$(PLUGIN_NAME) -f Makefile_oomox_plugin DESTDIR=$(DESTDIR)  APPDIR=$(APPDIR) PREFIX=$(PREFIX) install


install_import_random:
	$(eval PLUGIN_NAME := import_random)

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/


install_import_xresources:
	$(eval PLUGIN_NAME := import_xresources)

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/


install_export_xresources:
	$(eval PLUGIN_NAME := export_xresources)

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/


install_import_images:
	$(eval PLUGIN_NAME := import_from_image)

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/


install_plugin_base16:
	$(eval PLUGIN_NAME := base16)
	make -C plugins/$(PLUGIN_NAME) -f Makefile_oomox_plugin DESTDIR=$(DESTDIR)  APPDIR=$(APPDIR) PREFIX=$(PREFIX) install


install_icons_archdroid:
	$(eval PLUGIN_NAME := icons_archdroid)
	$(eval CLI_NAME := oomox-archdroid-icons-cli)
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
	$(eval PLUGIN_NAME := icons_gnomecolors)
	$(eval CLI_NAME := oomox-gnome-colors-icons-cli)
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
	$(eval PLUGIN_NAME := icons_numix)

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


install_icons_papirus:
	$(eval PLUGIN_NAME := icons_papirus)

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


install_icons_suruplus:
	$(eval PLUGIN_NAME := icons_suruplus)

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


install_icons_suruplus_aspromauros:
	$(eval PLUGIN_NAME := icons_suruplus_aspromauros)

	mkdir -p $(DEST_PLUGIN_DIR)
	cp -prf \
		plugins/$(PLUGIN_NAME) \
			$(DEST_PLUGIN_DIR)/
	$(RM) -r "$(DEST_PLUGIN_DIR)/$(PLUGIN_NAME)"/*/.git*


.PHONY: install
.PHONY: install_gui install_import_random install_theme_arc install_theme_oomox install_theme_materia install_export_oomoxify install_import_images install_plugin_base16 install_icons_archdroid install_icons_gnomecolors install_icons_numix install_icons_papirus install_icons_suruplus install_icons_suruplus_aspromauros install_import_xresources install_export_xresources
install: install_gui install_theme_oomox install_theme_materia install_export_oomoxify install_import_images install_plugin_base16 install_icons_archdroid install_icons_gnomecolors install_icons_numix install_icons_papirus install_icons_suruplus install_icons_suruplus_aspromauros install_import_xresources install_export_xresources

################################################################################

lint_fix:
	$(RUFF) check --fix $(TARGETS)

compile_all:
	export PYTHONWARNINGS='ignore,error:::$(TARGET_MODULE)[.*],error:::pikaur_test[.*]'
	# Running python compile:
	$(PYTHON) -O -m compileall $(TARGETS) \
	| (\
		grep -v -e '^Listing' -e '^Compiling' || true \
	)
	# :: python compile passed ::

python_import:
	# Running python import:
	$(PYTHON) -c "import $(TARGET_MODULE).main"
	# :: python import passed ::

non_final_globals:
	# Checking for non-Final globals:
	result=$$( \
		grep -REn "^[a-zA-Z_]+ = " $(TARGETS) --color=always \
		| grep -Ev \
			\
			-e '=.*\|' \
			-e '=.*(dict|list|Callable)\[' \
			\
			$(GLOBALS_IGNORES) \
		| sort \
	) ; \
	echo -n "$$result" ; \
	exit "$$(test "$$result" = "" && echo 0 || echo 1)"
	# :: non-final globals check passed ::

unreasonable_globals:
	# Checking for unreasonable global vars:
	result=$$( \
		grep -REn "^[a-zA-Z_]+ = [^'\"].*" $(TARGETS) --color=always \
		| grep -Ev \
			\
			-e ' =.*\|' \
			-e ' = [a-zA-Z_]+\[' \
			-e ' = str[^(]' \
			\
			$(GLOBALS_IGNORES) \
		| sort \
	) ; \
	echo -n "$$result" ; \
	exit "$$(test "$$result" = "" && echo 0 || echo 1)"
	# :: global vars check passed ::

ruff:
	# Checking Ruff rules up-to-date:
	diff --color -u \
		<(awk '/select = \[/,/]/' pyproject.toml \
			| sed -e 's|", "|/|g' \
			| head -n -1 \
			| tail -n +2 \
			| tr -d '",\#' \
			| awk '{print $$1;}' \
			| sort) \
		<($(RUFF) linter \
			| awk '{print $$1;}' \
			| sort)
	# Running ruff...
	$(RUFF) check $(TARGETS)
	# :: ruff passed ::

flake8:
	# Running flake8:
	$(PYTHON) -m flake8 $(TARGETS)
	# :: flake8 passed ::

pylint:
	# Running pylint:
	$(PYTHON) -m pylint $(TARGETS) --score no
	# :: pylint passed ::

mypy:
	# Running mypy:
	#$(PYTHON) -m mypy $(TARGETS) --no-error-summary
	$(PYTHON) -m mypy $(TARGET_MODULE) --no-error-summary
	# :: mypy passed ::

vulture:
	# Running vulture:
	$(PYTHON) -m vulture $(TARGETS) \
		--min-confidence=1 \
		--sort-by-size
	# :: vulture passed ::

shellcheck:
	# shellcheck disable=SC2046
	# Running shellcheck:
	( \
		cd $(APP_DIR) || exit ; \
		shellcheck $$(find . \
			-name '*.sh' \
			-not -path './plugins/icons_archdroid/archdroid-icon-theme/*' \
			-not -path './plugins/icons_gnomecolors/gnome-colors-icon-theme/*' \
			-not -path './plugins/icons_papirus/papirus-icon-theme/*' \
			-not -path './plugins/icons_suruplus/suru-plus/*' \
			-not -path './plugins/icons_suruplus_aspromauros/suru-plus-aspromauros/*' \
			-not -path './plugins/base16/*.tmp/*' \
			-not -path './plugins/oomoxify/*' \
			-not -path './plugins/theme_arc/arc-theme/*' \
			-not -path './plugins/theme_materia/materia-theme/*' \
			-not -path './plugins/theme_oomox/gtk-theme/*' \
			-or -path './packaging/bin/*' \
		) \
	)
	# :: shellcheck passed ::

shellcheck_makefile:
	# Running shellcheck on Makefile...
	( \
	    cd $(APP_DIR) || exit ; \
	    $(PYTHON) ./maintenance_scripts/makefile_shellcheck.py \
			--skip lint \
			--skip lint_ubuntu_310 \
		; \
	)
	# :: shellcheck makefile passed ::

validate_pyproject:
	# Validate pyproject file...
	( \
		exit_code=0 ; \
		result=$$(validate-pyproject pyproject.toml 2>&1) || exit_code=$$? ; \
		if [[ $$exit_code -gt 0 ]] ; then \
			echo "$$result" ; \
			exit "$$exit_code" ; \
		fi \
	)
	# :: pyproject validation passed ::

.PHONY: lint compile_all python_import non_final_globals unreasonable_globals ruff flake8 pylint mypy vulture shellcheck shellcheck_makefile validate_pyproject
lint: compile_all python_import non_final_globals unreasonable_globals ruff flake8 pylint mypy vulture shellcheck shellcheck_makefile validate_pyproject
lint_ubuntu_310: compile_all python_import non_final_globals unreasonable_globals flake8 pylint
