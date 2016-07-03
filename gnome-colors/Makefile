PROJECT := gnome-colors-src
DOCS := AUTHORS ChangeLog COPYING README
SIZES := 16x16 22x22 24x24 32x32
THEME_FILES := $(filter-out %~,$(wildcard themes/*))
LINKS_FILE := links
DIST_EXTRA := Makefile Palette.svg

gnome-colors_DIST_COMMON := yes
$(PROJECT)_DIST_COMMON := yes

BRANDING := \
	places/gnome-main-menu \
	places/gnome-starthere \
	places/mandrake \
	places/mandriva \
	places/novell-button \
	places/start-here

############################### Global variables ###############################

VERSION := $(shell head -n 1 ChangeLog | cut -d ' ' -f 1)

ifeq ($(THEME_FILES),)
ALL_THEMES := $(filter-out src,$(shell find * -maxdepth 1 ! -wholename '*/.*' -type f -name index.theme -printf "%h "))
THEMES := $(filter-out gnome-colors-common,$(ALL_THEMES))
THEME_BUILD_FILES = $(shell find $(1) ! -wholename '*/.*' -type f)
THEME_BUILD_LINKS = $(shell find $(1) ! -wholename '*/.*' -type l)
else
THEMES := $(notdir $(THEME_FILES))
ALL_THEMES := $(THEMES) gnome-colors-common
config = $(shell grep "^$(2)=" themes/$(1) | sed "s/^$(2)=//")
FIXED := $(shell find src/*x* ! -wholename '*/.*' -type f -name '*.svg')
SCALABLE := $(shell find src/scalable ! -wholename '*/.*' -type f -name '*.svg')
ICON_FILES := $(shell find src ! -wholename '*/.*' -type f -name '*.icon')
ONESIZE_FILES := $(patsubst src/scalable/%,%,$(SCALABLE))
LINK_LIST := $(shell sed "s/ /-->/" $(LINKS_FILE))
LINK_FILES := $(foreach link,$(LINK_LIST),$(lastword $(subst -->, ,$(link))))
THEME_BUILD_FILES = $(1)/index.theme \
	$(patsubst src/%,$(1)/%,$(SCALABLE)) \
	$(addprefix $(1)/,$(FIXED:src/%.svg=%.png)) \
	$(addprefix $(1)/24x24/,$(ONESIZE_FILES:%.svg=%.png)) \
	$(patsubst src/%,$(1)/%,$(ICON_FILES))
THEME_BUILD_LINKS = $(addprefix $(1)/scalable/,$(LINK_FILES:%.png=%.svg)) \
	$(foreach size,$(SIZES),$(addprefix $(1)/$(size)/,$(LINK_FILES)))
endif

THEME_BUILD = $(THEME_BUILD_FILES) $(THEME_BUILD_LINKS)
BUILD_FILES := $(foreach theme,$(THEMES),$(call THEME_BUILD_FILES,$(theme)))
BUILD_LINKS := $(foreach theme,$(THEMES),$(call THEME_BUILD_LINKS,$(theme)))
BUILD := $(BUILD_FILES) $(BUILD_LINKS)
COMMON_FILES := $(shell find gnome-colors-common ! -wholename '*/.*' -type f 2> /dev/null)
COMMON_LINKS := $(shell find gnome-colors-common ! -wholename '*/.*' -type l 2> /dev/null)
COMMON := $(COMMON_FILES) $(COMMON_LINKS)

################################### Building ###################################

# all should be the first target
all:

help::
	@echo "make targets:"

ifneq ($(THEME_FILES),)

COLORS = $(call config,$(1),Alternatives)

all: $(BUILD)

define color_template
$(1)_$(2)1 := $$(call config,$(1),$(2)_LightFolderBase)
$(1)_$(2)2 := $$(call config,$(1),$(2)_LightBase)
$(1)_$(2)3 := $$(call config,$(1),$(2)_MediumBase)
$(1)_$(2)4 := $$(call config,$(1),$(2)_DarkStroke)
$(1)_$(2)_sed := s/\#8fb3d9/$$($(1)_$(2)1)/g;s/\#729fcf/$$($(1)_$(2)2)/g;s/\#3465a4/$$($(1)_$(2)3)/g;s/\#204a87/$$($(1)_$(2)4)/g
$(1)_$(2)_FIXED := $(patsubst %.svg,%.png,$(foreach size,$(filter-out 24x24,$(SIZES)),$(addprefix $(size)/,$(call config,$(1),$(2)_Files))))
$(1)_$(2)_SCALABLE := $(patsubst %.png,%.svg,$(addprefix scalable/,$(call config,$(1),$(2)_Files)))
$(1)_$(2)_FILES := $$($(1)_$(2)_FIXED) $$($(1)_$(2)_SCALABLE)
$(1)_ALTERNATIVES += $$($(1)_$(2)_FILES)
endef

$(foreach theme,$(THEMES),$(foreach color,$(call COLORS,$(theme)),$(eval $(call color_template,$(theme),$(color)))))

define theme_template
$(1)_default1 := $$(call config,$(1),LightFolderBase)
$(1)_default2 := $$(call config,$(1),LightBase)
$(1)_default3 := $$(call config,$(1),MediumBase)
$(1)_default4 := $$(call config,$(1),DarkStroke)
$(1)_default_sed := s/\#8fb3d9/$$($(1)_default1)/g;s/\#729fcf/$$($(1)_default2)/g;s/\#3465a4/$$($(1)_default3)/g;s/\#204a87/$$($(1)_default4)/g

$(1): $(call THEME_BUILD,$(1))

$(1)/index.theme: src/index.theme themes/$(1)
	@if test ! -d $(1); then mkdir -p $(1); echo "mkdir -p $(1)"; fi
	sed "s/@NAME@/$(call config,$(1),Name)/" $$< > $$@
endef

$(foreach theme,$(THEMES),$(eval $(call theme_template,$(theme))))

define png_template
$(1)/$(2).png: src/$(2).svg themes/$(1)
	@if test ! -d $$(dir $$@); then mkdir -p $$(dir $$@); echo "mkdir -p $$(dir $$@)"; fi
	sed "$$($(1)_$(3)_sed)" $$< | inkscape --without-gui -f /dev/stdin -e "$$(CURDIR)/$$@" || true
endef

define svg_template
$(1)/$(2): src/$(2) themes/$(1)
	@if test ! -d $$(dir $$@); then mkdir -p $$(dir $$@); echo "mkdir -p $$(dir $$@)"; fi
	sed "$$($(1)_$(3)_sed)" $$< > $$@
endef

$(foreach theme,$(THEMES),$(foreach color,$(call COLORS,$(theme)), \
	$(foreach file,$(patsubst %.png,%,$($(theme)_$(color)_FIXED)),$(eval $(call png_template,$(theme),$(file),$(color)))) \
	$(foreach file,$($(theme)_$(color)_SCALABLE),$(eval $(call svg_template,$(theme),$(file),$(color)))) \
))

define 24_template
$(1)/24x24/$(2): $(1)/22x22/$(2)
	@if test ! -d $$(dir $$@); then mkdir -p $$(dir $$@); echo "mkdir -p $$(dir $$@)"; fi
	convert -bordercolor Transparent -border 1x1 $$< $$@ || true
endef

define link_template
$(1)/$(3):
	@if test ! -d $$(dir $$@); then mkdir -p $$(dir $$@); echo "mkdir -p $$(dir $$@)"; fi
	ln -sf $(2) $$@
endef

define icon_template
$(2): $(1)
	@if test ! -d $$(dir $$@); then mkdir -p $$(dir $$@); echo "mkdir -p $$(dir $$@)"; fi
	cp $$< $$@
endef

first = $(firstword $(subst -->, ,$(1)))
last = $(lastword $(subst -->, ,$(1)))

$(foreach theme,$(THEMES), \
	$(foreach file,$(filter-out $(patsubst %.png,%,$($(theme)_ALTERNATIVES)),$(patsubst src/%.svg,%,$(FIXED))),$(eval $(call png_template,$(theme),$(file),default))) \
	$(foreach file,$(filter-out $($(theme)_ALTERNATIVES),$(patsubst src/%,%,$(SCALABLE))),$(eval $(call svg_template,$(theme),$(file),default))) \
	$(foreach file,$(ONESIZE_FILES:%.svg=%.png),$(eval $(call 24_template,$(theme),$(file)))) \
	$(foreach link,$(LINK_LIST),$(foreach size,$(SIZES),$(eval $(call link_template \
		,$(theme)/$(size),$(call first,$(link)),$(call last,$(link)))))) \
	$(foreach link,$(LINK_LIST),$(eval $(call link_template \
		,$(theme)/scalable,$(patsubst %.png,%.svg,$(call first,$(link))),$(patsubst %.png,%.svg,$(call last,$(link)))))) \
	$(foreach icon,$(ICON_FILES),$(eval $(call icon_template,$(icon),$(patsubst src/%,$(theme)/%,$(icon))))) \
)

help::
	@echo "    all                      Build all files for all themes (default target)."
	@echo "    THEME                    Build all files for THEME."

else

help::
	@echo "    all                      Does nothing (default target)."

endif

#################################### Cleanup ###################################

clean:
	rm -f *.tar *.tar.bz2 *.tar.gz
ifneq ($(THEME_FILES),)
	rm -rf $(THEMES)
endif

help::
	@echo "    clean                    Deletes all files created by this makefile."

.PHONY: clean

################################# Miscellaneous ################################

BROKEN_LINKS = $(shell find * ! -wholename '*/.*' -type l ! -exec test -r {} \; -printf "%p ")

check:
	@for link in $(BROKEN_LINKS); do echo "Found broken link $$link"; done
	@test -z "$(BROKEN_LINKS)"

fixperms:
	find * ! -wholename '*/.*' -a -type f -a ! -perm 644 -exec chmod 644 {} \; -printf "chmod 644 %p\n"

themes:
	@echo "Available themes:"
	@for theme in $(sort $(ALL_THEMES)); do echo $$theme; done

help::
	@echo "    check                    Performs self tests."
	@echo "    fixperms                 Fixes permissions of icon files."
	@echo "    help                     Displays this help."
	@echo "    themes                   Lists all available themes."

.PHONY: check fixperms help themes

################################# Distribution #################################

ifneq ($(THEME_FILES),)

DISTRIBUTIONS := $(PROJECT) \
	$(sort $(foreach theme,$(THEMES),$(call config,$(theme),Distribution)))
$(PROJECT)_DIST := \
	$(shell find src ! -wholename '*/.*' -type f) \
	$(THEME_FILES) \
	$(LINKS_FILE)

COMMON_LINKS1 := $(filter gnome-colors-common/16x16% gnome-colors-common/22x22%,$(COMMON_LINKS))
COMMON_LINKS2 := $(filter-out $(COMMON_LINKS1),$(COMMON_LINKS))

define dist_template
# The tar command must be split, otherwise you get this error:
# make: execvp: /bin/sh: Argument list too long
$(1)-$(VERSION).tar: $$(DOCS) $$(DIST_EXTRA) $$($(1)_DIST)
	$$(MAKE) fixperms
	tar -cf $$@ $$(filter-out $$(COMMON),$$^)
ifeq ($($(1)_DIST_COMMON),yes)
	tar -rf $$@ $$(COMMON_FILES)
	tar -rf $$@ $$(COMMON_LINKS1)
	tar -rf $$@ $$(COMMON_LINKS2)

$(1)-$(VERSION).tar: $$(COMMON)
endif

$(1)-$(VERSION).tar.bz2: $(1)-$(VERSION).tar
	bzip2 -cz9 $$< > $$@

$(1)-$(VERSION).tar.gz: $(1)-$(VERSION).tar
	gzip -cn9 $$< > $$@
endef

define dist_theme_template
$(call config,$(1),Distribution)-$(VERSION).tar: $(call THEME_BUILD,$(1))
endef

$(foreach dist,$(DISTRIBUTIONS),$(eval $(call dist_template,$(dist))))
$(foreach theme,$(THEMES),$(eval $(call dist_theme_template,$(theme))))

dist: gz

dist-src: $(PROJECT)-$(VERSION).tar.gz

bz2: $(addsuffix -$(VERSION).tar.bz2,$(DISTRIBUTIONS))

gz: $(addsuffix -$(VERSION).tar.gz,$(DISTRIBUTIONS))

help::
	@echo "    dist                     Creates distribution tar files."
	@echo "    dist-src                 Creates a source distribution tar file."
	@echo "    bz2                      Create distribution .tar.bz2 files."
	@echo "    gz                       Create distribution .tar.gz files."

endif

################################# Installation #################################

USER := ~/.icons
SYSTEM := $(DESTDIR)/usr/share/icons
BRANDING_FILES := $(patsubst %,gnome-colors-common/scalable/%.svg,$(BRANDING)) \
	$(foreach size,$(SIZES),$(patsubst %,gnome-colors-common/$(size)/%.png,$(BRANDING)))
UNBRANDED_COMMON := $(filter-out $(BRANDING_FILES),$(COMMON))

define install_template
$(SYSTEM)/$(1): $(1)
	install -D -m 644 $$< $$@

$(USER)/$(1): $(1)
	install -D -m 644 $$< $$@
endef

define install_links_template
$(SYSTEM)/$(1): $(1)
	cp -d $$< $$@

$(USER)/$(1): $(1)
	cp -d $$< $$@
endef

$(foreach file,$(BUILD_FILES) $(COMMON_FILES),$(eval $(call install_template,$(file))))
$(foreach file,$(BUILD_LINKS) $(COMMON_LINKS),$(eval $(call install_links_template,$(file))))

define theme_install_template
install-$(1): $$(addprefix $$(SYSTEM)/,$(call THEME_BUILD,$(1)))

user-install-$(1): $$(addprefix $$(USER)/,$(call THEME_BUILD,$(1)))

ifneq ($(COMMON),)
install-$(1): install-unbranded-gnome-colors-common
user-install-$(1): user-install-unbranded-gnome-colors-common
endif
endef

define theme_uninstall_template
uninstall-$(1):
	rm -rf $$(SYSTEM)/$(1)

user-uninstall-$(1):
	rm -rf $$(USER)/$(1)

.PHONY: uninstall-$(1) user-uninstall-$(1)
endef

$(foreach theme,$(THEMES),$(eval $(call theme_install_template,$(theme))))
$(foreach theme,$(ALL_THEMES),$(eval $(call theme_uninstall_template,$(theme))))

install-gnome-colors-common: $(addprefix $(SYSTEM)/,$(COMMON))

user-install-gnome-colors-common: $(addprefix $(USER)/,$(COMMON))

install-unbranded-gnome-colors-common: $(addprefix $(SYSTEM)/,$(UNBRANDED_COMMON))

user-install-unbranded-gnome-colors-common: $(addprefix $(USER)/,$(UNBRANDED_COMMON))

install: $(addprefix install-,$(ALL_THEMES))

user-install: $(addprefix user-install-,$(ALL_THEMES))

install-unbranded: $(addprefix install-,$(THEMES)) install-unbranded-gnome-colors-common

user-install-unbranded: $(addprefix user-install-,$(THEMES)) user-install-unbranded-gnome-colors-common

uninstall:
	rm -rf $(addprefix $(SYSTEM)/,$(ALL_THEMES))

user-uninstall:
	rm -rf $(addprefix $(USER)/,$(ALL_THEMES))

help::
	@echo "    install                  Installs all themes system-wide."
	@echo "    install-unbranded        Installs all themes unbranded system-wide."
	@echo "    uninstall                Removes all themes from the system."
	@echo "    user-install             Installs all themes into the user directory."
	@echo "    user-install-unbranded   Installs all themes unbranded for the user."
	@echo "    user-uninstall           Removes all themes from the user directory."
	@echo "    install-THEME            Installs THEME system-wide."
	@echo "    uninstall-THEME          Removes THEME from the system."
	@echo "    user-install-THEME       Installs THEME into the user directory."
	@echo "    user-uninstall-THEME     Removes THEME from the user directory."

.PHONY:  uninstall user-uninstall
