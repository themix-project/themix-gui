#!/usr/bin/make -f

DOMAIN = oomox
PODIR = po
SOURCES = $(wildcard oomox_gui/*.py) $(wildcard plugins/*/oomox_plugin.py)
LOCALEDIR = ./locale

XGETTEXT ?= xgettext --package-name=$(DOMAIN) --foreign-user
MSGINIT ?= msginit
MSGMERGE ?= msgmerge
MSGFMT ?= msgfmt
RM ?= rm -f
INSTALL ?= install
MKDIR_P ?= mkdir -p

POTFILE = $(PODIR)/$(DOMAIN).pot
ALL_PO = $(wildcard $(PODIR)/*.po)
ALL_MO = $(ALL_PO:.po=.mo)

all: install

update-pot: $(POTFILE)
update-po: $(ALL_PO)

$(POTFILE): $(SOURCES)
	test -d $(PODIR) || $(MKDIR_P) $(PODIR)
	$(XGETTEXT) -o $@ $^

$(PODIR)/%.po: $(POTFILE)
	if test -f $@; then \
		$(MSGMERGE) -U $@ $(POTFILE); \
	else \
		$(MSGINIT) -o $@ -i $(POTFILE); \
	fi

$(PODIR)/%.mo: $(PODIR)/%.po
	$(MSGFMT) -o $@ $^

install: $(ALL_MO)
	for f in $^; do \
		l="$$(basename "$$f" .mo)"; \
		d="$(LOCALEDIR)/$$l/LC_MESSAGES"; \
		$(MKDIR_P) "$$d" || exit; \
		$(INSTALL) -m 644 "$$f" "$$d/$(DOMAIN).mo"; \
	done

check: $(ALL_PO)
	$(MSGFMT) --check --check-accelerators=_ --statistics $^

clean:
	$(RM) $(POTFILE)
	$(RM) $(PODIR)/*.mo
