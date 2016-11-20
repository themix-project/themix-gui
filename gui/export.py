import subprocess
import os
from threading import Thread
from gi.repository import Gtk, GLib

from .helpers import oomox_root_dir, CenterLabel


DEFAULT_SPOTIFY_PATH = "/usr/share/spotify/Apps"


class ExportDialog(Gtk.Dialog):

    previous_height = None

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

        self.under_log_box.add(label)
        self.under_log_box.add(button)
        self.show_all()

    def set_text(self, text):
        self.log.get_buffer().set_text(text)
        self._text_adjustment_callback()

    def _text_adjustment_callback(self, widget=None, event=None, data=None):
        adj = self.scrolled_window.get_vadjustment()
        adj.set_value(adj.get_upper() - adj.get_page_size())

    def _resize_callback(self, widget, event, data=None):
        window_height = self.get_allocated_height()
        if not self.previous_height:
            self.previous_height = window_height
        if window_height != self.previous_height:
            scroller_height = self.scrolled_window.get_allocated_height()
            scroller_height += window_height - self.previous_height
            self.previous_height = window_height
            self.scrolled_window.set_max_content_height(scroller_height)
            self.scrolled_window.set_min_content_height(scroller_height)
            self._text_adjustment_callback()

    def __init__(self, parent, headline="Exporting..."):
        Gtk.Dialog.__init__(self, headline, parent, 0)
        self.set_default_size(150, 80)

        self.label = CenterLabel(
            "Please wait while\nnew colorscheme will be created"
        )

        self.spinner = Gtk.Spinner()
        self.spinner.start()

        self.log = Gtk.TextView()
        self.log.set_editable(False)
        # self.log.set_cursor_visible(False)
        self.log.set_monospace(True)
        self.log.set_wrap_mode(Gtk.WrapMode.CHAR)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_margin_bottom(5)
        self.scrolled_window.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.log)

        self.under_log_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )

        self.box = self.get_content_area()
        self.box.set_margin_left(5)
        self.box.set_margin_right(5)
        self.box.add(self.label)
        self.box.add(self.spinner)
        self.box.add(self.scrolled_window)
        self.box.add(self.under_log_box)
        self.show_all()

        self.connect('size-allocate', self._resize_callback)


def _export(window, theme_path, export_args):
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
            export_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        for line in iter(proc.stdout.readline, b''):
            captured_log += line.decode("utf-8")
            GLib.idle_add(update_ui, captured_log)
        proc.communicate(timeout=60)
        if proc.returncode == 0:
            GLib.idle_add(ui_done)
        else:
            GLib.idle_add(ui_error)

    spinner = ExportDialog(window)
    thread = Thread(target=do_export)
    thread.daemon = True
    thread.start()


def export_theme(window, theme_path):
    if Gtk.get_minor_version() >= 20:
        make_opts = "gtk320"
    else:
        make_opts = "gtk3"
    return _export(window, theme_path, [
        "bash",
        os.path.join(oomox_root_dir, "change_color.sh"),
        theme_path,
        "--make-opts", make_opts
    ])


def export_gnome_colors_icon_theme(window, theme_path):
    return _export(window, theme_path, [
        "bash",
        os.path.join(oomox_root_dir, "gnome_colors.sh"),
        theme_path,
    ])


def export_archdroid_icon_theme(window, theme_path):
    return _export(window, theme_path, [
        "bash",
        os.path.join(oomox_root_dir, "archdroid.sh"),
        theme_path,
    ])


class SpotifyExportDialog(ExportDialog):

    def do_export(self):
        spotify_path = self.spotify_path_entry.get_text()
        normalize_font = self.font_checkbox.get_active()
        button_height = self.apply_button.get_allocated_height()
        scroller_height = self.scrolled_window.get_allocated_height()
        new_scroller_height = scroller_height + button_height
        self.options_box.destroy()
        self.apply_button.destroy()
        self.scrolled_window.set_min_content_height(new_scroller_height)
        self.scrolled_window.set_max_content_height(new_scroller_height)

        self.spinner.start()
        self.scrolled_window.show()
        export_args = [
            "bash",
            os.path.join(oomox_root_dir, "oomoxify.sh"),
            self.theme_path,
            '--gui',
            '--spotify-apps-path', spotify_path,
        ]
        if normalize_font:
            export_args.append('--font-weight')

        captured_log = ""

        def update_ui(text):
            self.set_text(text)

        def ui_done():
            self.stop()

        def ui_error():
            self.show_error()

        def export_worker():
            nonlocal captured_log
            proc = subprocess.Popen(
                export_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            for line in iter(proc.stdout.readline, b''):
                captured_log += line.decode("utf-8")
                GLib.idle_add(update_ui, captured_log)
            proc.communicate(timeout=60)
            if proc.returncode == 0:
                GLib.idle_add(ui_done)
            else:
                GLib.idle_add(ui_error)

        thread = Thread(target=export_worker)
        thread.daemon = True
        thread.start()

    def stop(self):
        self.spinner.stop()
        self.apply_button.destroy()

        self.label.set_text("Theme applied successfully")

        button = Gtk.Button(label="OK")
        button.connect("clicked", self._close_button_callback)

        self.under_log_box.add(button)
        self.show_all()

        button_height = button.get_allocated_height()
        scroller_height = self.scrolled_window.get_allocated_height()
        new_scroller_height = scroller_height - button_height
        self.scrolled_window.set_min_content_height(new_scroller_height)
        self.scrolled_window.set_max_content_height(new_scroller_height)

    def __init__(self, parent, theme_path):
        ExportDialog.__init__(self, parent, "Spotify options")
        self.theme_path = theme_path

        # self.set_default_size(180, 120)
        self.spinner.stop()
        self.label.set_text("This functionality is still in BETA")

        self.options_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )
        self.options_box.set_margin_bottom(10)

        self.font_checkbox = Gtk.CheckButton(label="Normalize font weight")
        self.options_box.add(self.font_checkbox)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        spotify_path_label = Gtk.Label('Spotify path:')
        self.spotify_path_entry = Gtk.Entry(text=DEFAULT_SPOTIFY_PATH)
        hbox.add(spotify_path_label)
        hbox.add(self.spotify_path_entry)
        self.options_box.add(hbox)

        self.under_log_box.add(self.options_box)

        self.apply_button = Gtk.Button(label="Apply")
        self.apply_button.connect("clicked", lambda x: self.do_export())
        self.under_log_box.add(self.apply_button)

        self.show_all()
        self.scrolled_window.hide()


def export_spotify(window, theme_path):
    return SpotifyExportDialog(window, theme_path)
