import subprocess
import os
from threading import Thread
from gi.repository import Gtk, GObject, GLib

from .helpers import theme_dir, CenterLabel


class ExportDialog(Gtk.Dialog):

    def _close_button_callback(self, widget):
        self.destroy()

    def show_error(self):
        self.label.destroy()
        self.spinner.destroy()

        label = CenterLabel(
            "Something went wrong :("
        )
        label.set_alignment(0.5, 0.5)

        button = Gtk.Button(label="Dismiss")
        button.connect("clicked", self._close_button_callback)

        self.box.add(label)
        self.box.add(button)
        self.show_all()


    def set_text(self, text):
        self.log.get_buffer().set_text(text)

    def _resize_callback(self, widget, event, data=None):
        adj = self.scrolled_window.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Exporting...", parent, 0)
        self.set_default_size(150, 80)

        self.label = CenterLabel(
            "Please wait while\nnew colorscheme will be created"
        )

        self.spinner = Gtk.Spinner()
        self.spinner.start()

        self.log = Gtk.TextView()
        self.log.set_editable(False)
        #self.log.set_cursor_visible(False)
        self.log.set_monospace(True)
        self.log.set_wrap_mode(Gtk.WrapMode.CHAR)
        self.log.connect('size-allocate', self._resize_callback)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.log)
        self.scrolled_window.set_min_content_height(100)

        self.box = self.get_content_area()
        self.box.add(self.label)
        self.box.add(self.spinner)
        self.box.add(self.scrolled_window)
        self.show_all()


def export_theme(window, theme_path):
    spinner = ExportDialog(window)

    captured_log = ""

    def update_ui(text):
        spinner.set_text(text)

    def ui_done():
        spinner.destroy()

    def ui_error():
        spinner.show_error()

    def do_export():
        nonlocal captured_log
        proc = subprocess.Popen(
            [
                "bash",
                os.path.join(theme_dir, "change_color.sh"),
                theme_path
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

    thread = Thread(target=do_export)
    thread.daemon = True
    thread.start()
    spinner.run()
