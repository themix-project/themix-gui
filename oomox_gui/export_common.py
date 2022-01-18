# -*- coding: utf-8 -*-
import subprocess
import os
import tempfile
from threading import Thread

from gi.repository import Gtk, GLib, Pango

from .i18n import translate
from .config import USER_EXPORT_CONFIG_DIR, DEFAULT_ENCODING
from .settings import CommonOomoxConfig
from .theme_file import save_colorscheme
from .gtk_helpers import CenterLabel, GObjectABCMeta, g_abstractproperty


from typing import TYPE_CHECKING  # pylint: disable=wrong-import-order
if TYPE_CHECKING:
    from typing import Dict  # noqa


class ExportConfig(CommonOomoxConfig):

    def __init__(self, config_name, default_config=None):
        super().__init__(
            config_name=config_name,
            default_config=default_config,
            config_dir=USER_EXPORT_CONFIG_DIR,
        )


class ExportDialog(Gtk.Dialog):

    colorscheme = None
    theme_name = None
    command = None
    timeout = 300

    # widgets:
    box = None
    top_area = None
    label = None
    spinner = None
    options_box = None
    scrolled_window = None
    log = None
    error_box = None
    apply_button = None

    def _close_button_callback(self, _widget):
        self.destroy()

    def show_text(self):
        if not self.scrolled_window.get_visible():
            self.scrolled_window.show_all()

    def show_error(self):
        self.box.remove(self.label)
        self.box.remove(self.spinner)

        error_label = CenterLabel(
            label=translate("Something went wrong :(")
        )
        error_label.set_alignment(0.5, 0.5)

        error_dismiss_button = Gtk.Button(label=translate("_Dismiss"), use_underline=True)
        error_dismiss_button.connect("clicked", self._close_button_callback)

        self.error_box.add(error_label)
        self.error_box.add(error_dismiss_button)
        self.error_box.show_all()
        self.box.add(self.error_box)

    def set_text(self, text):
        self.log.get_buffer().set_text(text)

    def __init__(
            self, transient_for,
            colorscheme,
            theme_name,
            headline=translate("Export Theme"),
            width=150,
            height=80,
    ):
        self.theme_name = 'oomox-' + theme_name.split('/')[-1]

        # @TODO: make sure it doesn't break things:
        self.colorscheme = colorscheme
        # from .terminal import generate_terminal_colors_for_oomox
        # self.colorscheme = generate_terminal_colors_for_oomox(colorscheme)

        Gtk.Dialog.__init__(self, headline, transient_for, 0)
        self.set_default_size(width, height)
        self.label = CenterLabel()
        self.spinner = Gtk.Spinner()

        # Scrollable log window:
        self.log = Gtk.TextView()
        self.log.set_editable(False)
        # self.log.set_cursor_visible(False)
        self.log.override_font(
            # @TODO: make log size configurable?
            Pango.font_description_from_string("monospace 8")
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
        self.options_box.set_margin_top(5)
        self.options_box.set_margin_bottom(15)

        self.apply_button = Gtk.Button(label=translate("_Apply Options and Export"), use_underline=True)
        self.apply_button.connect("clicked", lambda x: self.do_export())

        self.error_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5
        )
        self.error_box.set_margin_bottom(10)

        self.box = self.get_content_area()
        self.box.set_margin_left(5)
        self.box.set_margin_right(5)
        self.box.set_spacing(5)
        self.top_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.add(self.top_area)
        self.top_area.add(self.label)

        self.show_all()
        self.box.add(self.spinner)
        self.box.add(self.scrolled_window)

    def do_export(self):
        self.box.remove(self.options_box)
        self.box.remove(self.apply_button)
        self.scrolled_window.set_size_request(-1, 200)
        self.scrolled_window.show_all()
        self.spinner.show()
        self.spinner.start()
        self.set_title(translate("Exporting…"))

        def update_ui(text):
            self.set_text(text)

        def ui_done():
            self.destroy()

        def ui_error():
            self.show_error()

        def do_export():
            self.label.set_text(translate("Please wait while\nnew colorscheme will be created."))
            self.label.show()
            captured_log = ""
            with subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            ) as proc:
                for line in iter(proc.stdout.readline, b''):
                    captured_log += line.decode(DEFAULT_ENCODING)
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

    temp_theme_path = None

    def __init__(self, transient_for, **kwargs):
        super().__init__(transient_for=transient_for, **kwargs)

        self.temp_theme_path = save_colorscheme(
            preset_name=self.theme_name,
            colorscheme=self.colorscheme,
            path=tempfile.mkstemp()[1]
        )

    def __del__(self):
        os.remove(self.temp_theme_path)


class ExportDialogWithOptions(FileBasedExportDialog, metaclass=GObjectABCMeta):

    option_widgets = {}  # type: Dict[str, Gtk.Widget]

    @g_abstractproperty
    def config_name(self):
        pass

    def _create_option_checkbox_callback(self, option_id):
        def callback(widget):
            self.export_config[option_id] = widget.get_active()
        return callback

    def _create_option_entry_callback(self, option_id):
        def callback(widget):
            self.export_config[option_id] = widget.get_text()
        return callback

    def __init__(
            self, transient_for, colorscheme, theme_name,
            export_options=None, headline=None,
            **kwargs
    ):
        export_options = export_options or {}
        super().__init__(
            transient_for=transient_for, colorscheme=colorscheme, theme_name=theme_name,
            headline=headline or translate("Theme Export Options"),
            **kwargs
        )
        self.label.hide()

        self.export_config = ExportConfig(
            config_name=self.config_name,
            default_config={
                option_name: option['default']
                for option_name, option in export_options.items()
            }
        )

        for option_name, option in export_options.items():
            value = self.export_config[option_name]
            value_widget = None
            if isinstance(value, bool):
                value_widget = \
                    Gtk.CheckButton.new_with_mnemonic(
                        option['display_name']
                    )
                value_widget.connect(
                    "toggled", self._create_option_checkbox_callback(option_name)
                )
                value_widget.set_active(value)
                self.option_widgets[option_name] = value_widget
            elif isinstance(value, str):
                value_widget = Gtk.HBox()
                label = Gtk.Label(
                    label=option.get('display_name', option_name),
                    use_underline=True
                )
                entry = Gtk.Entry(text=value)
                entry.connect(
                    "changed", self._create_option_entry_callback(option_name)
                )
                entry.set_width_chars(min(len(value) + 15, 60))
                label.set_mnemonic_widget(entry)
                value_widget.add(label)
                value_widget.add(entry)
                self.option_widgets[option_name] = entry
            else:
                raise NotImplementedError()
            self.options_box.add(value_widget)

        self.box.add(self.options_box)
        self.options_box.show_all()
        self.box.add(self.apply_button)
        self.apply_button.show()

    def do_export(self):
        self.export_config.save()
        super().do_export()


OPTION_GTK2_HIDPI = 'gtk2_hidpi'


class CommonGtkThemeExportDialog(ExportDialogWithOptions):

    @g_abstractproperty
    def config_name(self):
        pass

    def __init__(
            self, transient_for, colorscheme, theme_name,
            add_options=None, override_options=None,
            **kwargs
    ):
        export_options = override_options or {
            OPTION_GTK2_HIDPI: {
                'default': False,
                'display_name': translate("Generate 2x scaled (_HiDPI) assets for GTK+2"),
            },
        }
        if add_options:
            export_options.update(add_options)
        super().__init__(
            transient_for=transient_for, colorscheme=colorscheme,
            theme_name=theme_name, export_options=export_options,
            **kwargs
        )
