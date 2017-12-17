import subprocess
from threading import Thread

from gi.repository import Gtk, GLib

from ..config import oomoxify_script_path

from .export_config import ExportConfig
from .common import ExportDialog


class SpotifyExportConfig(ExportConfig):
    name = 'spotify'


class SpotifyExportDialog(ExportDialog):

    theme_path = None
    export_config = None

    def do_export(self):
        self.export_config['font_name'] = self.font_name_entry.get_text()
        self.export_config['spotify_path'] = self.spotify_path_entry.get_text()
        self.export_config.save()

        self.options_box.destroy()
        self.apply_button.destroy()

        self.spinner.start()
        self.scrolled_window.show()
        export_args = [
            "bash",
            oomoxify_script_path,
            self.theme_path,
            '--gui',
            '--spotify-apps-path', self.export_config['spotify_path'],
        ]
        if self.export_config['font_options'] == "normalize":
            export_args.append('--font-weight')
        elif self.export_config['font_options'] == "custom":
            export_args.append('--font')
            export_args.append(self.export_config['font_name'])

        def update_ui(text):
            self.set_text(text)

        def ui_done():
            self.stop()

        def ui_error():
            self.show_error()

        def export_worker():
            captured_log = ""
            proc = subprocess.Popen(
                export_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            for line in iter(proc.stdout.readline, b''):
                captured_log += line.decode("utf-8")
                GLib.idle_add(update_ui, captured_log)
            proc.communicate(timeout=120)
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

        self.label.set_text(_("Theme applied successfully"))

        button = Gtk.Button(label=_("_OK"), use_underline=True)
        button.connect("clicked", self._close_button_callback)

        self.under_log_box.add(button)
        self.show_all()

    def on_font_radio_toggled(self, button, value):
        if button.get_active():
            self.export_config['font_options'] = value
            self.font_name_entry.set_sensitive(value == "custom")

    def _init_radios(self):
        self.font_radio_default = \
            Gtk.RadioButton.new_with_mnemonic_from_widget(
                None,
                _("Don't change _default font")
            )
        self.font_radio_default.connect(
            "toggled", self.on_font_radio_toggled, "default"
        )
        self.options_box.add(self.font_radio_default)

        self.font_radio_normalize = \
            Gtk.RadioButton.new_with_mnemonic_from_widget(
                self.font_radio_default,
                _("_Normalize font weight")
            )
        self.font_radio_normalize.connect(
            "toggled", self.on_font_radio_toggled, "normalize"
        )
        self.options_box.add(self.font_radio_normalize)

        self.font_radio_custom = Gtk.RadioButton.new_with_mnemonic_from_widget(
            self.font_radio_default,
            _("Use custom _font:")
        )
        self.font_radio_custom.connect(
            "toggled", self.on_font_radio_toggled, "custom"
        )
        self.options_box.add(self.font_radio_custom)

        self.font_name_entry = Gtk.Entry(text=self.export_config['font_name'])
        self.options_box.add(self.font_name_entry)

        self.font_name_entry.set_sensitive(self.export_config['font_options'] == "custom")
        if self.export_config['font_options'] == 'normalize':
            self.font_radio_normalize.set_active(True)
        if self.export_config['font_options'] == 'custom':
            self.font_radio_custom.set_active(True)

    def __init__(self, parent, theme_path):
        ExportDialog.__init__(self, parent, headline=_("Spotify options"))
        self.theme_path = theme_path
        self.export_config = SpotifyExportConfig({
            "spotify_path": "/usr/share/spotify/Apps",
            "font_name": "sans-serif",
            "font_options": "default",
        })

        # self.set_default_size(180, 120)
        self.spinner.stop()
        self.label.set_text(_("Please choose the font options:"))

        self.options_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )
        self.options_box.set_margin_bottom(10)

        self._init_radios()

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        spotify_path_label = Gtk.Label(label=_('Spotify _path:'),
                                       use_underline=True)
        self.spotify_path_entry = Gtk.Entry(text=self.export_config['spotify_path'])
        spotify_path_label.set_mnemonic_widget(self.spotify_path_entry)
        hbox.add(spotify_path_label)
        hbox.add(self.spotify_path_entry)
        self.options_box.add(hbox)

        self.under_log_box.add(self.options_box)

        self.apply_button = Gtk.Button(label=_("_Apply"), use_underline=True)
        self.apply_button.connect("clicked", lambda x: self.do_export())
        self.under_log_box.add(self.apply_button)

        self.show_all()
        self.scrolled_window.hide()


def export_spotify(window, theme_path):
    return SpotifyExportDialog(window, theme_path)
