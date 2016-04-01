#!/bin/env python3
import os
import gi
gi.require_version('Gtk', '3.0')  # noqa
from gi.repository import Gtk, Gdk

from .helpers import (
    read_colorscheme_from_preset, script_dir
)
from .presets_list import ThemePresetsList
from .colors_list import ThemeColorsList
from .preview import ThemePreview


class MainWindow(Gtk.Window):

    def _init_window(self):
        Gtk.Window.__init__(self, title="Oo-mox GUI")
        self.set_default_size(500, 300)
        self.set_border_width(6)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Oo-mox GUI"
        self.set_titlebar(hb)

        win_style_context = self.get_style_context()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(os.path.join(script_dir, "theme.css"))
        screen = Gdk.Screen.get_default()
        win_style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.box)

    colorscheme = None
    theme_edit = None
    presets_list = None
    preview = None

    def __init__(self):
        self.colorscheme = {}

        self._init_window()

        def preset_select_callback(selected_preset):
            self.colorscheme = read_colorscheme_from_preset(selected_preset)
            self.theme_edit.open_theme(self.colorscheme)
            self.preview.update_preview_colors(self.colorscheme)

        def color_edited_callback(colorscheme):
            self.colorscheme = colorscheme
            self.preview.update_preview_colors(self.colorscheme)

        self.presets_list = ThemePresetsList(
            preset_select_callback=preset_select_callback
        )
        presets_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        presets_list_label = Gtk.Label()
        presets_list_label.set_text("Presets:")
        presets_list_box.pack_start(presets_list_label, False, False, 0)
        presets_list_box.pack_start(self.presets_list, True, True, 0)
        self.box.pack_start(presets_list_box, True, True, 0)

        self.theme_edit = ThemeColorsList(
            color_edited_callback=color_edited_callback
        )
        # preset_select_callback=preset_select_callback)
        theme_edit_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        theme_edit_label = Gtk.Label()
        theme_edit_label.set_text("Edit:")
        theme_edit_box.pack_start(theme_edit_label, False, False, 0)
        theme_edit_box.pack_start(self.theme_edit, True, True, 0)
        self.box.pack_start(theme_edit_box, True, True, 0)

        self.preview = ThemePreview()
        preview_grid = Gtk.Grid()
        preview_label = Gtk.Label()
        preview_label.set_text("Preview:")
        preview_grid.attach(preview_label, 1, 1, 1, 1)
        preview_grid.attach_next_to(self.preview, preview_label,
                                    Gtk.PositionType.BOTTOM, 1, 1)
        self.box.pack_start(preview_grid, True, True, 0)


def main():
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
