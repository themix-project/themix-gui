INSTALL=cp -rf
CLEAN=rm -rf
THEME="Numix"
LIGHTTHEME="Numix Light"
DARKTHEME="Numix Dark"
LIGHTDIR=../$(LIGHTTHEME)
DARKDIR=../$(DARKTHEME)

all: light dark

light:
	mkdir -p $(LIGHTDIR)
	cp -rf "gtk-2.0" "gtk-3.0" "metacity-1" "unity" "index.theme" $(LIGHTDIR)
	convert -negate $(LIGHTDIR)/unity/close.png $(LIGHTDIR)/unity/close.png
	convert -negate $(LIGHTDIR)/unity/maximize.png $(LIGHTDIR)/unity/maximize.png
	convert -negate $(LIGHTDIR)/unity/minimize.png $(LIGHTDIR)/unity/minimize.png
	convert -negate $(LIGHTDIR)/unity/unmaximize.png $(LIGHTDIR)/unity/unmaximize.png
	convert -negate $(LIGHTDIR)/unity/close_focused_normal.png $(LIGHTDIR)/unity/close_focused_normal.png
	convert -negate $(LIGHTDIR)/unity/maximize_focused_normal.png $(LIGHTDIR)/unity/maximize_focused_normal.png
	convert -negate $(LIGHTDIR)/unity/minimize_focused_normal.png $(LIGHTDIR)/unity/minimize_focused_normal.png
	convert -negate $(LIGHTDIR)/unity/unmaximize_focused_normal.png $(LIGHTDIR)/unity/unmaximize_focused_normal.png
	convert -negate $(LIGHTDIR)/metacity-1/close_focused_normal.png $(LIGHTDIR)/metacity-1/close_focused_normal.png
	convert -negate $(LIGHTDIR)/metacity-1/maximize_focused_normal.png $(LIGHTDIR)/metacity-1/maximize_focused_normal.png
	convert -negate $(LIGHTDIR)/metacity-1/minimize_focused_normal.png $(LIGHTDIR)/metacity-1/minimize_focused_normal.png
	convert -negate $(LIGHTDIR)/metacity-1/unmaximize_focused_normal.png $(LIGHTDIR)/metacity-1/unmaximize_focused_normal.png
	convert -brightness-contrast 30% $(LIGHTDIR)/unity/close.png $(LIGHTDIR)/unity/close.png
	convert -brightness-contrast 30% $(LIGHTDIR)/unity/maximize.png $(LIGHTDIR)/unity/maximize.png
	convert -brightness-contrast 30% $(LIGHTDIR)/unity/minimize.png $(LIGHTDIR)/unity/minimize.png
	convert -brightness-contrast 30% $(LIGHTDIR)/unity/unmaximize.png $(LIGHTDIR)/unity/unmaximize.png
	convert -brightness-contrast 30% $(LIGHTDIR)/unity/close_focused_normal.png $(LIGHTDIR)/unity/close_focused_normal.png
	convert -brightness-contrast 30% $(LIGHTDIR)/unity/maximize_focused_normal.png $(LIGHTDIR)/unity/maximize_focused_normal.png
	convert -brightness-contrast 30% $(LIGHTDIR)/unity/minimize_focused_normal.png $(LIGHTDIR)/unity/minimize_focused_normal.png
	convert -brightness-contrast 30% $(LIGHTDIR)/unity/unmaximize_focused_normal.png $(LIGHTDIR)/unity/unmaximize_focused_normal.png
	convert -brightness-contrast 30% $(LIGHTDIR)/metacity-1/close_focused_normal.png $(LIGHTDIR)/metacity-1/close_focused_normal.png
	convert -brightness-contrast 30% $(LIGHTDIR)/metacity-1/maximize_focused_normal.png $(LIGHTDIR)/metacity-1/maximize_focused_normal.png
	convert -brightness-contrast 30% $(LIGHTDIR)/metacity-1/minimize_focused_normal.png $(LIGHTDIR)/metacity-1/minimize_focused_normal.png
	convert -brightness-contrast 30% $(LIGHTDIR)/metacity-1/unmaximize_focused_normal.png $(LIGHTDIR)/metacity-1/unmaximize_focused_normal.png
	sed -e 's/#2d2d2d/#dedede/g' -e 's/#dcdcdc/#555555/g' -i $(LIGHTDIR)/metacity-1/metacity-theme-1.xml
	sed -e 's/tooltip_bg_color:#2d2d2d/tooltip_bg_color:#dedede/g' -e 's/tooltip_fg_color:#f9f9f9/tooltip_fg_color:#555555/g' -e 's/menubar_bg_color:#2d2d2d/menubar_bg_color:#dedede/g' -e 's/menubar_fg_color:#dcdcdc/menubar_fg_color:#555555/g' -e 's/menu_bg_color:#2d2d2d/menu_bg_color:#f9f9f9/g' -e 's/menu_fg_color:#dcdcdc/menu_fg_color:#555555/g' -e 's/panel_bg_color:#2d2d2d/panel_bg_color:#dedede/g' -e 's/panel_fg_color:#dcdcdc/panel_fg_color:#555555/g' -i $(LIGHTDIR)/gtk-2.0/gtkrc
	sed -e 's/tooltip_bg_color:#2d2d2d/tooltip_bg_color:#dedede/g' -e 's/tooltip_fg_color:#f9f9f9/tooltip_fg_color:#555555/g' -e 's/menubar_bg_color:#2d2d2d/menubar_bg_color:#dedede/g' -e 's/menubar_fg_color:#dcdcdc/menubar_fg_color:#555555/g' -e 's/menu_bg_color:#2d2d2d/menu_bg_color:#f9f9f9/g' -e 's/menu_fg_color:#dcdcdc/menu_fg_color:#555555/g' -e 's/panel_bg_color:#2d2d2d/panel_bg_color:#dedede/g' -e 's/panel_fg_color:#dcdcdc/panel_fg_color:#555555/g' -i $(LIGHTDIR)/gtk-3.0/settings.ini
	sed -e 's/@define-color tooltip_bg_color #2d2d2d/@define-color tooltip_bg_color #dedede/g' -e 's/@define-color tooltip_fg_color #f9f9f9/@define-color tooltip_fg_color #555555/g' -e 's/@define-color menubar_bg_color #2d2d2d/@define-color menubar_bg_color #dedede/g' -e 's/@define-color menubar_fg_color #dcdcdc/@define-color menubar_fg_color #555555/g' -e 's/@define-color menu_bg_color #2d2d2d/@define-color menu_bg_color #f9f9f9/g' -e 's/@define-color menu_fg_color #dcdcdc/@define-color menu_fg_color #555555/g' -e 's/@define-color panel_bg_color #2d2d2d/@define-color panel_bg_color #dedede/g' -e 's/@define-color panel_fg_color #dcdcdc/@define-color panel_fg_color #555555/g' -e 's/@define-color wm_bg #2d2d2d/@define-color wm_bg #dedede/g' -e 's/@define-color wm_title_focused #dcdcdc/@define-color wm_title_focused #555555/g' -e 's/@define-color wm_border_focused #2d2d2d/@define-color wm_border_focused #888888/g' -e 's/@define-color wm_border_unfocused #2d2d2d/@define-color wm_border_unfocused #888888/g' -i $(LIGHTDIR)/gtk-3.0/gtk.css
	sed -e 's/Name=Numix/Name=Numix Light/g' -e 's/GtkTheme=Numix/GtkTheme=Numix Light/g' -e 's/MetacityTheme=Numix/MetacityTheme=Numix Light/g' -i $(LIGHTDIR)/index.theme

dark:
	mkdir -p $(DARKDIR)
	cp -rf "gtk-2.0" "gtk-3.0" "index.theme" $(DARKDIR)
	sed -e 's/toolbar_bg_color:#dedede/toolbar_bg_color:#2d2d2d/g' -e 's/toolbar_fg_color:#555555/toolbar_fg_color:#dcdcdc/g' -i $(DARKDIR)/gtk-2.0/gtkrc
	sed -e 's/toolbar_bg_color:#dedede/toolbar_bg_color:#2d2d2d/g' -e 's/toolbar_fg_color:#555555/toolbar_fg_color:#dcdcdc/g' -i $(DARKDIR)/gtk-3.0/settings.ini
	sed -e 's/@define-color toolbar_bg_color #dedede/@define-color toolbar_bg_color #2d2d2d/g' -e 's/@define-color toolbar_fg_color #555555/@define-color  toolbar_fg_color #dcdcdc/g' -i $(DARKDIR)/gtk-3.0/gtk.css
	sed -e 's/Name=Numix/Name=Numix Dark/g' -e 's/GtkTheme=Numix/GtkTheme=Numix Dark/g' -i $(DARKDIR)/index.theme

clean:
	$(CLEAN) $(LIGHTDIR) $(DARKDIR)

install: all
	mkdir -p $(DESTDIR)/usr/share/themes/$(THEME)/
	mkdir -p $(DESTDIR)/usr/share/themes/$(LIGHTTHEME)/
	mkdir -p $(DESTDIR)/usr/share/themes/$(DARKTHEME)/
	$(INSTALL) gtk-2.0 gtk-3.0 metacity-1 openbox-3 unity xfwm4 index.theme README $(DESTDIR)/usr/share/themes/$(THEME)/
	$(INSTALL) $(LIGHTDIR)/gtk-2.0 $(LIGHTDIR)/gtk-3.0 $(LIGHTDIR)/metacity-1 $(LIGHTDIR)/index.theme $(DESTDIR)/usr/share/themes/$(LIGHTTHEME)/
	$(INSTALL) $(DARKDIR)/gtk-2.0 $(DARKDIR)/gtk-3.0 $(DARKDIR)/index.theme $(DESTDIR)/usr/share/themes/$(DARKTHEME)/

uninstall:
	$(CLEAN) $(DESTDIR)/usr/share/themes/$(THEME)
	$(CLEAN) $(DESTDIR)/usr/share/themes/$(LIGHTTHEME)
	$(CLEAN) $(DESTDIR)/usr/share/themes/$(DARKTHEME)

