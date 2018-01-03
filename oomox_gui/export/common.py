import subprocess
import os
from threading import Thread

from gi.repository import Gtk, GLib, Pango

from ..terminal import generate_xrdb_theme_from_oomox, generate_xresources
from ..gtk_helpers import CenterLabel
from ..config import (
    archdroid_theme_dir, gnome_colors_icon_theme_dir,
)


class ExportDialog(Gtk.Dialog):

    command = None
    timeout = None

    def _close_button_callback(self, widget):
        self.destroy()

    def show_error(self):
        self.box.remove(self.label)
        self.box.remove(self.spinner)

        self.error_label = CenterLabel(
            _("Something went wrong :(")
        )
        self.error_label.set_alignment(0.5, 0.5)

        self.error_dismiss_button = Gtk.Button(label=_("_Dismiss"), use_underline=True)
        self.error_dismiss_button.connect("clicked", self._close_button_callback)

        self.error_box.add(self.error_label)
        self.error_box.add(self.error_dismiss_button)
        self.error_box.show_all()
        self.box.add(self.error_box)

    def set_text(self, text):
        self.log.get_buffer().set_text(text)

    def _adj_changed(self, adj):
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def __init__(
        self, parent,
        headline=_("Exporting..."),
        command=None,
        timeout=120,
        width=150,
        height=80
    ):
        Gtk.Dialog.__init__(self, headline, parent, 0)
        self.set_default_size(width, height)

        self.command = command
        self.timeout = timeout

        self.label = CenterLabel()

        self.spinner = Gtk.Spinner()

        # Scrollable log window:
        self.log = Gtk.TextView()
        self.log.set_editable(False)
        # self.log.set_cursor_visible(False)
        if Gtk.get_minor_version() >= 16:
            self.log.set_monospace(True)
        else:
            self.log.override_font(
                Pango.font_description_from_string("monospace")
            )
        self.log.set_wrap_mode(Gtk.WrapMode.CHAR)
        #
        self.scrolled_window = Gtk.ScrolledWindow(expand=True)
        self.scrolled_window.set_margin_bottom(5)
        self.scrolled_window.add(self.log)
        #
        adj = self.scrolled_window.get_vadjustment()
        adj.connect('changed', self._adj_changed)

        self.options_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )
        self.options_box.set_margin_bottom(10)

        self.apply_button = Gtk.Button(label=_("_Apply"), use_underline=True)
        self.apply_button.connect("clicked", lambda x: self.do_export())

        self.error_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )
        self.error_box.set_margin_bottom(10)

        self.box = self.get_content_area()
        self.box.set_margin_left(5)
        self.box.set_margin_right(5)
        self.box.set_spacing(5)
        self.box.add(self.label)

        self.show_all()

    def do_export(self):
        self.box.remove(self.options_box)
        self.box.remove(self.apply_button)
        self.box.add(self.spinner)
        self.box.add(self.scrolled_window)
        self.scrolled_window.set_size_request(-1, 200)
        self.scrolled_window.show_all()
        self.spinner.show()
        self.spinner.start()

        def update_ui(text):
            self.set_text(text)

        def ui_done():
            self.destroy()

        def ui_error():
            self.show_error()

        def do_export():
            self.label.set_text(_("Please wait while\nnew colorscheme will be created"))
            captured_log = ""
            proc = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            for line in iter(proc.stdout.readline, b''):
                captured_log += line.decode("utf-8")
                GLib.idle_add(update_ui, captured_log)
            proc.communicate(timeout=self.timeout)
            if proc.returncode == 0:
                GLib.idle_add(ui_done)
            else:
                GLib.idle_add(ui_error)

        thread = Thread(target=do_export)
        thread.daemon = True
        thread.start()


def export_gnome_colors_icon_theme(window, theme_path):
    return ExportDialog(window, timeout=600, command=[
        "bash",
        os.path.join(gnome_colors_icon_theme_dir, "change_color.sh"),
        theme_path,
    ]).do_export()


def export_archdroid_icon_theme(window, theme_path):
    return ExportDialog(window, timeout=100, command=[
        "bash",
        os.path.join(archdroid_theme_dir, "change_color.sh"),
        theme_path,
    ]).do_export()


def export_terminal_theme(window, colorscheme):
    dialog = ExportDialog(
        window,
        headline=_("Terminal colorscheme"),
        height=440
    )
    dialog.box.add(dialog.scrolled_window)
    dialog.scrolled_window.show_all()
    dialog.label.set_text(_('Paste this colorscheme to your ~/.Xresources'))
    try:
        term_colorscheme = generate_xrdb_theme_from_oomox(colorscheme)
        xresources_theme = generate_xresources(term_colorscheme)
    except Exception as e:
        dialog.set_text(e)
        dialog.show_error()
    else:
        dialog.set_text(xresources_theme)
