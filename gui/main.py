#!/bin/env python3
import os
import gi
gi.require_version('Gtk', '3.0')  # noqa
from gi.repository import Gtk, Gdk, GObject, GLib

from .helpers import (
    read_colorscheme_from_preset, script_dir
)
from .presets_list import ThemePresetsList
from .colors_list import ThemeColorsList
from .preview import ThemePreview
from .export import export_theme


class MainWindow(Gtk.Window):

    colorscheme_name = None
    colorscheme = None
    theme_edited = False
    # widgets:
    theme_edit = None
    presets_list = None
    preview = None

    def on_export(self, button):
        return export_theme(window=self, theme_name=self.colorscheme_name)

    def _init_window(self):
        Gtk.Window.__init__(self, title="Oo-mox GUI")
        self.set_default_size(500, 300)
        self.set_border_width(6)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.props.title = "Oo-mox GUI"
        export_button = Gtk.Button(label="Create theme")
        export_button.connect("clicked", self.on_export)
        self.headerbar.pack_end(export_button)
        self.set_titlebar(self.headerbar)

        win_style_context = self.get_style_context()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(os.path.join(script_dir, "theme.css"))
        screen = Gdk.Screen.get_default()
        win_style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.box)

    def __init__(self):
        self.colorscheme = {}

        self._init_window()

        def preset_select_callback(selected_preset):
            self.colorscheme_name = selected_preset
            self.colorscheme = read_colorscheme_from_preset(selected_preset)
            self.theme_edit.open_theme(self.colorscheme)
            self.preview.update_preview_colors(self.colorscheme)
            self.headerbar.props.title = selected_preset
            self.theme_edited = False

        def color_edited_callback(colorscheme):
            self.colorscheme = colorscheme
            self.preview.update_preview_colors(self.colorscheme)
            if not self.theme_edited:
                self.headerbar.props.title = "*" + self.headerbar.props.title
            self.theme_edited = True

        self.presets_list = ThemePresetsList(
            preset_select_callback=preset_select_callback
        )
        self.box.pack_start(self.presets_list, True, True, 0)

        self.theme_edit = ThemeColorsList(
            color_edited_callback=color_edited_callback
        )
        self.box.pack_start(self.theme_edit, True, True, 0)

        self.preview = ThemePreview()
        self.box.pack_start(self.preview, True, True, 0)


def main():
    GObject.threads_init()
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
