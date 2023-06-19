import os
import subprocess
import tempfile
from threading import Thread
from typing import TYPE_CHECKING

from gi.repository import GLib, Gtk, Pango

from .config import DEFAULT_ENCODING, USER_EXPORT_CONFIG_DIR
from .gtk_helpers import CenterLabel, GObjectABCMeta, g_abstractproperty
from .i18n import translate
from .settings import CommonOomoxConfig
from .theme_file import save_colorscheme

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from .theme_file import ThemeT


class ExportConfig(CommonOomoxConfig):

    def __init__(self, config_name: str, default_config: dict[str, "Any"] | None = None) -> None:
        super().__init__(
            config_name=config_name,
            default_config=default_config,
            config_dir=USER_EXPORT_CONFIG_DIR,
            force_reload=True,
        )


class ExportDialog(Gtk.Dialog):

    colorscheme: "ThemeT"
    theme_name: str
    command: str
    timeout = 300

    # widgets:
    box: Gtk.Box
    top_area: Gtk.Box
    label: CenterLabel
    spinner: Gtk.Spinner
    options_box: Gtk.Box
    scrolled_window: Gtk.ScrolledWindow
    log: Gtk.TextView
    error_box: Gtk.Box
    apply_button: Gtk.Button

    def _close_button_callback(self, _widget: Gtk.Button) -> None:
        self.destroy()

    def show_text(self) -> None:
        if not self.scrolled_window.get_visible():
            self.scrolled_window.show_all()

    def show_error(self) -> None:
        self.box.remove(self.label)
        self.box.remove(self.spinner)

        error_label = CenterLabel(
            label=translate("Something went wrong :("),
        )
        error_label.set_alignment(0.5, 0.5)

        error_dismiss_button = Gtk.Button(label=translate("_Dismiss"), use_underline=True)
        error_dismiss_button.connect("clicked", self._close_button_callback)

        self.error_box.add(error_label)
        self.error_box.add(error_dismiss_button)
        self.error_box.show_all()
        self.box.add(self.error_box)

    def set_text(self, text: str) -> None:
        self.log.get_buffer().set_text(text)

    def __init__(
            self,
            transient_for: Gtk.Window,
            colorscheme: "ThemeT",
            theme_name: str,
            headline: str | None = None,
            width: int = 150,
            height: int = 80,
    ) -> None:
        headline = headline or translate("Export Theme")
        self.theme_name = "oomox-" + theme_name.split("/")[-1]

        # @TODO: make sure it doesn't break things:
        self.colorscheme = colorscheme
        # from .terminal import generate_terminal_colors_for_oomox
        # self.colorscheme = generate_terminal_colors_for_oomox(colorscheme)

        Gtk.Dialog.__init__(self, headline, transient_for, 0)  # type: ignore[call-arg]
        self.set_default_size(width, height)
        self.label = CenterLabel()
        self.spinner = Gtk.Spinner()

        # Scrollable log window:
        self.log = Gtk.TextView()
        self.log.set_editable(False)
        # self.log.set_cursor_visible(False)
        self.log.override_font(
            # @TODO: make log size configurable?
            Pango.font_description_from_string("monospace 8"),
        )
        self.log.set_wrap_mode(Gtk.WrapMode.CHAR)
        #
        self.scrolled_window = Gtk.ScrolledWindow(expand=True)  # type: ignore[call-arg]
        self.scrolled_window.set_margin_bottom(5)
        self.scrolled_window.add(self.log)
        #
        adj = self.scrolled_window.get_vadjustment()
        adj.connect(
            "changed",
            lambda adj: adj.set_value(adj.get_upper() - adj.get_page_size()),
        )

        self.options_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5,
        )
        self.options_box.set_margin_top(5)
        self.options_box.set_margin_bottom(15)

        self.apply_button = Gtk.Button(
            label=translate("_Apply Options and Export"), use_underline=True,
        )
        self.apply_button.connect("clicked", lambda _x: self.do_export())

        self.error_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5,
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

    def do_export(self) -> None:
        self.box.remove(self.options_box)
        self.box.remove(self.apply_button)
        self.scrolled_window.set_size_request(-1, 200)
        self.scrolled_window.show_all()
        self.spinner.show()
        self.spinner.start()
        self.set_title(translate("Exporting…"))

        def update_ui(text: str) -> None:
            self.set_text(text)

        def ui_done() -> None:
            self.destroy()

        def ui_error() -> None:
            self.show_error()

        def do_export() -> None:
            self.label.set_text(translate("Please wait while\nnew colorscheme will be created."))
            self.label.show()
            captured_log = ""
            with subprocess.Popen(
                self.command,  # noqa: S603
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            ) as proc:
                for line in iter(
                        proc.stdout.readline,  # type: ignore[union-attr]
                        b"",
                ):
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

    temp_theme_path: str

    def __init__(self, transient_for: Gtk.Window, **kwargs: "Any") -> None:
        super().__init__(transient_for=transient_for, **kwargs)

        self.temp_theme_path = save_colorscheme(
            preset_name=self.theme_name,
            colorscheme=self.colorscheme,
            path=tempfile.mkstemp()[1],
        )

    def __del__(self) -> None:
        if getattr(self, "temp_theme_path", None):
            os.remove(self.temp_theme_path)


class ExportDialogWithOptionsOptions:
    pass


class ExportDialogWithOptions(FileBasedExportDialog, metaclass=GObjectABCMeta):

    OPTIONS: ExportDialogWithOptionsOptions = ExportDialogWithOptionsOptions()

    config_name: str

    @g_abstractproperty  # type: ignore[no-redef]
    def config_name(self) -> None:
        pass

    def _create_option_checkbox_callback(
            self, option_id: str,
    ) -> "Callable[[Gtk.CheckButton], None]":
        def callback(widget: Gtk.CheckButton) -> None:
            self.export_config[option_id] = widget.get_active()
        return callback

    def _create_option_entry_callback(self, option_id: str) -> "Callable[[Gtk.Entry], None]":
        def callback(widget: Gtk.Entry) -> None:
            self.export_config[option_id] = widget.get_text()
        return callback

    def __init__(
            self,
            transient_for: Gtk.Window,
            colorscheme: "ThemeT",
            theme_name: str,
            export_options: "dict[str, Any] | None" = None,
            override_options: dict[str, "Any"] | None = None,
            headline: str | None = None,
            **kwargs: "Any",
    ) -> None:
        self.option_widgets: dict[str, Gtk.Widget] = {}
        export_options = override_options or export_options or {}
        super().__init__(
            transient_for=transient_for, colorscheme=colorscheme, theme_name=theme_name,
            headline=headline or translate("Theme Export Options"),
            **kwargs,
        )
        self.label.hide()

        self.export_config = ExportConfig(
            config_name=self.config_name,
            default_config={
                option_name: option["default"]
                for option_name, option in export_options.items()
            },
        )

        for option_name, option in export_options.items():
            value = self.export_config[option_name]
            value_widget: Gtk.Widget
            if isinstance(value, bool):
                value_widget = \
                    Gtk.CheckButton.new_with_mnemonic(
                        option["display_name"],
                    )
                value_widget.connect(
                    "toggled", self._create_option_checkbox_callback(option_name),
                )
                value_widget.set_active(value)
                self.option_widgets[option_name] = value_widget
            elif isinstance(value, str):
                value_widget = Gtk.HBox()
                label = Gtk.Label(
                    label=option.get("display_name", option_name),
                    use_underline=True,
                )
                entry = Gtk.Entry(text=value)  # type: ignore[call-arg]
                entry.connect(
                    "changed", self._create_option_entry_callback(option_name),
                )
                entry.set_width_chars(min(len(value) + 15, 60))
                label.set_mnemonic_widget(entry)
                value_widget.add(label)
                value_widget.add(entry)
                self.option_widgets[option_name] = entry
            else:
                raise NotImplementedError
            self.options_box.add(value_widget)

        self.box.add(self.options_box)
        self.options_box.show_all()
        self.box.add(self.apply_button)
        self.apply_button.show()

    def do_export(self) -> None:
        self.export_config.save()
        super().do_export()


class DialogWithExportPathOptions(ExportDialogWithOptionsOptions):
    DEFAULT_PATH: str = "default_path"


class DialogWithExportPath(ExportDialogWithOptions):

    OPTIONS: DialogWithExportPathOptions = DialogWithExportPathOptions()

    default_export_dir: str
    config_name: str

    @g_abstractproperty  # type: ignore[no-redef]
    def default_export_dir(self) -> None:
        pass

    @g_abstractproperty  # type: ignore[no-redef]
    def config_name(self) -> None:  # type: ignore[override]
        pass

    def __init__(
            self,
            transient_for: Gtk.Window,
            colorscheme: "ThemeT",
            theme_name: str,
            add_options: dict[str, "Any"] | None = None,
            override_options: dict[str, "Any"] | None = None,
            export_options: dict[str, "Any"] | None = None,
            **kwargs: "Any",
    ) -> None:
        export_options = override_options or export_options or {}
        if not override_options:
            export_options.update({
                self.OPTIONS.DEFAULT_PATH: {
                    "default": self.default_export_dir,
                    "display_name": translate("Export _path: "),
                },
            })
        if add_options:
            export_options.update(add_options)
        super().__init__(
            transient_for=transient_for,
            colorscheme=colorscheme, theme_name=theme_name,
            export_options=export_options,
            **kwargs,
        )
        if (
                (self.OPTIONS.DEFAULT_PATH in self.option_widgets) and
                (self.export_config.get(self.OPTIONS.DEFAULT_PATH))
        ):
            self.option_widgets[self.OPTIONS.DEFAULT_PATH].set_text(  # type: ignore[attr-defined]
                os.path.join(
                    self.export_config[self.OPTIONS.DEFAULT_PATH],
                    self.theme_name,
                ),
            )

    def do_export(self) -> None:
        export_path = os.path.expanduser(
            self.option_widgets[self.OPTIONS.DEFAULT_PATH].get_text(),  # type: ignore[attr-defined]
        )
        new_destination_dir, _theme_name = export_path.rsplit("/", 1)

        super().do_export()

        self.export_config[self.OPTIONS.DEFAULT_PATH] = new_destination_dir
        self.export_config.save()


class CommonGtkThemeExportDialogOptions(DialogWithExportPathOptions):
    GTK2_HIDPI = "gtk2_hidpi"


class CommonGtkThemeExportDialog(DialogWithExportPath):

    OPTIONS: CommonGtkThemeExportDialogOptions = CommonGtkThemeExportDialogOptions()
    default_export_dir: str = os.path.join(os.environ["HOME"], ".themes")
    config_name: str

    @g_abstractproperty  # type: ignore[no-redef]
    def config_name(self) -> None:  # type: ignore[override]
        pass

    def __init__(
            self,
            transient_for: Gtk.Window,
            colorscheme: "ThemeT",
            theme_name: str,
            add_options: dict[str, "Any"] | None = None,
            override_options: dict[str, "Any"] | None = None,
            **kwargs: "Any",
    ) -> None:
        export_options = override_options or {
            self.OPTIONS.GTK2_HIDPI: {
                "default": False,
                "display_name": translate("Generate 2x scaled (_HiDPI) assets for GTK+2"),
            },
        }
        if add_options:
            export_options.update(add_options)
        super().__init__(
            transient_for=transient_for,
            colorscheme=colorscheme, theme_name=theme_name,
            export_options=export_options, override_options=override_options,
            **kwargs,
        )


class CommonIconThemeExportDialog(DialogWithExportPath):

    default_export_dir: str = os.path.join(os.environ["HOME"], ".icons")

    config_name: str

    @g_abstractproperty  # type: ignore[no-redef]
    def config_name(self) -> None:  # type: ignore[override]
        pass

    def __init__(
            self,
            transient_for: Gtk.Window,
            colorscheme: "ThemeT",
            theme_name: str,
            add_options: dict[str, "Any"] | None = None,
            override_options: dict[str, "Any"] | None = None,
            **kwargs: "Any",
    ) -> None:
        if os.environ.get("XDG_CURRENT_DESKTOP", "").lower() in ("kde", "lxqt"):
            self.default_export_dir = os.path.join(
                os.environ.get(
                    "XDG_DATA_HOME",
                    os.path.join(os.environ["HOME"], ".local/share"),
                ),
                "icons",
            )
        export_options = override_options or {}
        if add_options:
            export_options.update(add_options)
        super().__init__(
            transient_for=transient_for,
            colorscheme=colorscheme, theme_name=theme_name,
            export_options=export_options, override_options=override_options,
            **kwargs,
        )
