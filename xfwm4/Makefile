
SRCDIR=src
TARGS=close-pressed.xpm close-prelight.xpm close-inactive.xpm close-active.xpm \
  hide-pressed.xpm hide-prelight.xpm hide-inactive.xpm hide-active.xpm \
  menu-pressed.xpm menu-prelight.xpm menu-inactive.xpm menu-active.xpm \
  shade-pressed.xpm shade-prelight.xpm shade-inactive.xpm shade-active.xpm \
  shade-toggled-pressed.xpm shade-toggled-prelight.xpm \
  shade-toggled-inactive.xpm shade-toggled-active.xpm \
  stick-pressed.xpm stick-prelight.xpm stick-inactive.xpm stick-active.xpm \
  stick-toggled-pressed.xpm stick-toggled-prelight.xpm \
  stick-toggled-inactive.xpm stick-toggled-active.xpm \
  maximize-pressed.xpm maximize-prelight.xpm \
  maximize-inactive.xpm maximize-active.xpm \
  maximize-toggled-pressed.xpm maximize-toggled-prelight.xpm \
  maximize-toggled-inactive.xpm maximize-toggled-active.xpm

BASE_MENU=$(SRCDIR)/button-base-menu.xpm
BASE_ACTIVE=$(SRCDIR)/button-base-active.xpm
BASE_INACTIVE=$(SRCDIR)/button-base-inactive.xpm

COL_PRESSED=\#B44335
COL_PRELIGHT=\#D64937
COL_ACTIVE=\#DCDCDC
COL_INACTIVE=\#888



all: $(TARGS)



# Base images for the menu, a 22x16 blank surface in all states. The 16px
# constrains the window icon's size to 16x16.

menu-%.xpm: $(BASE_MENU)
	convert $< $@


# Combined icon images built from 8x8 SVG sources
# The base images are 22x25, width carefully chosen to provide the right 
# spacing and rhythm, and height including an additional top pixel of the
# active/inactive edge colour.


%-inactive.xpm: $(SRCDIR)/%.svg $(BASE_INACTIVE)
	convert $(BASE_INACTIVE) \
	    \( -background none +level-colors "$(COL_INACTIVE)" $< \) \
	    -geometry +7+9 -composite $@

%-pressed.xpm: $(SRCDIR)/%.svg $(BASE_ACTIVE)
	convert $(BASE_ACTIVE) \
	    \( -background none +level-colors "$(COL_PRESSED)" $< \) \
	    -geometry +7+9 -composite $@

%-prelight.xpm: $(SRCDIR)/%.svg $(BASE_ACTIVE)
	convert $(BASE_ACTIVE) \
	    \( -background none +level-colors "$(COL_PRELIGHT)" $< \) \
	    -geometry +7+9 -composite $@

%-active.xpm: $(SRCDIR)/%.svg $(BASE_ACTIVE)
	convert $(BASE_ACTIVE) \
	    \( -background none +level-colors "$(COL_ACTIVE)" $< \) \
	    -geometry +7+9 -composite $@


clean:
	rm -f $(TARGS)
