#!/bin/env python3
import os
import subprocess
from threading import Thread
import gi
gi.require_version('Gtk', '3.0')  # noqa
from gi.repository import Gtk, Gdk, GObject, GLib

from .helpers import (
    read_colorscheme_from_preset, script_dir, theme_dir
)
from .presets_list import ThemePresetsList
from .colors_list import ThemeColorsList
from .preview import ThemePreview
from .dialogs import SpinnerDialog


class MainWindow(Gtk.Window):

    def on_export(self, button):
        spinner = SpinnerDialog(self)

        captured_log = ""

        def update_ui(text):
            spinner.set_text(text)

        def ui_done():
            spinner.destroy()

        def ui_error():
            spinner.show_error()

        def export():
            nonlocal captured_log
            proc = subprocess.Popen(
                [
                    "bash",
                    os.path.join(theme_dir, "change_color.sh"),
                    self.colorscheme_name
                ],
                stdout=subprocess.PIPE
            )
            for line in iter(proc.stdout.readline, b''):
                captured_log += line.decode("utf-8")
                GLib.idle_add(update_ui, captured_log)
            proc.communicate(timeout=60)
            if proc.returncode == 0:
                GLib.idle_add(ui_done)
            else:
                GLib.idle_add(ui_error)

        thread = Thread(target=export)
        thread.daemon = True
        thread.start()
        spinner.run()

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

    colorscheme_name = None
    colorscheme = None
    theme_edit = None
    presets_list = None
    preview = None
    theme_edited = False

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
    GObject.threads_init()
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
