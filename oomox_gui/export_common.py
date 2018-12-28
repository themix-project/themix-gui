# -*- coding: utf-8 -*-
import subprocess
import os
import tempfile
from threading import Thread

from gi.repository import Gtk, GLib, Pango

from .export_config import ExportConfig
from .theme_file import save_colorscheme
from .terminal import (
    generate_terminal_colors_for_oomox,
    generate_xrdb_theme_from_oomox,
    generate_xresources
)
from .gtk_helpers import CenterLabel, GObjectABCMeta, g_abstractproperty
from .i18n import _


class ExportDialog(Gtk.Dialog):

    command = None
    timeout = 300

    # widgets:
    box = None
    label = None
    spinner = None
    options_box = None
    scrolled_window = None
    log = None
    error_box = None
    apply_button = None

    def _close_button_callback(self, _widget):
        self.destroy()

    def show_error(self):
        self.box.remove(self.label)
        self.box.remove(self.spinner)

        error_label = CenterLabel(
            label=_("Something went wrong :(")
        )
        error_label.set_alignment(0.5, 0.5)

        error_dismiss_button = Gtk.Button(label=_("_Dismiss"), use_underline=True)
        error_dismiss_button.connect("clicked", self._close_button_callback)

        self.error_box.add(error_label)
        self.error_box.add(error_dismiss_button)
        self.error_box.show_all()
        self.box.add(self.error_box)

    def set_text(self, text):
        self.log.get_buffer().set_text(text)

    def __init__(
            self, transient_for,
            headline=_("Export Theme"),
            width=150,
            height=80
    ):
        Gtk.Dialog.__init__(self, headline, transient_for, 0)
        self.set_default_size(width, height)

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
        adj.connect(
            'changed',
            lambda adj: adj.set_value(adj.get_upper() - adj.get_page_size())
        )

        self.options_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )
        self.options_box.set_margin_bottom(10)

        self.apply_button = Gtk.Button(label=_("_Apply Options and Export"), use_underline=True)
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
        self.set_title(_("Exporting…"))

        def update_ui(text):
            self.set_text(text)

        def ui_done():
            self.destroy()

        def ui_error():
            self.show_error()

        def do_export():
            self.label.set_text(_("Please wait while\nnew colorscheme will be created."))
            self.label.show()
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


class FileBasedExportDialog(ExportDialog):

    theme_name = None
    temp_theme_path = None

    def __init__(self, transient_for, colorscheme, theme_name, **kwargs):
        super().__init__(transient_for=transient_for, **kwargs)
        self.theme_name = 'oomox-' + theme_name.split('/')[-1]
        colorscheme_copy = generate_terminal_colors_for_oomox(colorscheme)
        self.temp_theme_path = save_colorscheme(
            preset_name=theme_name,
            colorscheme=colorscheme_copy,
            path=tempfile.mkstemp()[1]
        )

    def __del__(self):
        os.remove(self.temp_theme_path)


def export_terminal_theme(transient_for, colorscheme):
    dialog = ExportDialog(
        transient_for=transient_for,
        headline=_("Terminal Colorscheme"),
        height=440
    )
    dialog.box.add(dialog.scrolled_window)
    dialog.scrolled_window.show_all()
    dialog.label.set_text(_('Paste this colorscheme to your ~/.Xresources:'))
    try:
        term_colorscheme = generate_xrdb_theme_from_oomox(colorscheme)
        xresources_theme = generate_xresources(term_colorscheme)
    except Exception as exc:
        dialog.set_text(exc)
        dialog.show_error()
    else:
        dialog.set_text(xresources_theme)


OPTION_GTK2_HIDPI = 'gtk2_hidpi'


class CommonGtkThemeExportDialog(FileBasedExportDialog, metaclass=GObjectABCMeta):

    @g_abstractproperty
    def config_name(self):
        pass

    def _create_option_checkbox_callback(self, option_id):
        def callback(widget):
            self.export_config[option_id] = widget.get_active()
        return callback

    def __init__(  # pylint: disable=too-many-arguments
            self, transient_for, colorscheme, theme_name,
            add_options=None, override_options=None,
            **kwargs
    ):
        super().__init__(
            transient_for=transient_for, colorscheme=colorscheme, theme_name=theme_name,
            **kwargs
        )
        self.label.hide()

        export_options = override_options or {
            OPTION_GTK2_HIDPI: {
                'default': False,
                'display_name': _("Generate 2x scaled (_HiDPI) assets for GTK+2"),
            },
        }
        if add_options:
            export_options.update(add_options)
        self.export_config = ExportConfig(
            config_name=self.config_name,
            default_config={
                option_name: option['default']
                for option_name, option in export_options.items()
            }
        )

        export_options_headline = Gtk.Label()
        export_options_headline.set_markup('<b>' + _("Theme Export Options") + '</b>')
        export_options_headline.set_justify(Gtk.Justification.LEFT)
        export_options_headline.set_alignment(0.0, 0.0)
        self.options_box.add(export_options_headline)

        for option_name, option in export_options.items():
            checkbox = \
                Gtk.CheckButton.new_with_mnemonic(
                    option['display_name']
                )
            checkbox.connect(
                "toggled", self._create_option_checkbox_callback(option_name)
            )
            checkbox.set_active(
                self.export_config[option_name]
            )
            self.options_box.add(checkbox)

        self.box.add(self.options_box)
        self.options_box.show_all()
        self.box.add(self.apply_button)
        self.apply_button.show()

    def do_export(self):
        self.export_config.save()
        super().do_export()
