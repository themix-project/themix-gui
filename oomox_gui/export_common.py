import os
import subprocess
import tempfile
from threading import Thread
from typing import (
    TYPE_CHECKING,
    Generic,
    TypeVar,
)

from gi.repository import (
    GLib,
    Gtk,
    Pango,
)

from .config import DEFAULT_ENCODING, USER_EXPORT_CONFIG_DIR
from .gtk_helpers import (
    CenterLabel,
    g_abstractproperty,
    nongobject_check_class_for_gobject_metas,
)
from .helpers import SuppressWarningsFilter
from .i18n import translate
from .settings import CommonOomoxConfig
from .theme_file import save_colorscheme

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

    from .plugin_api import OomoxPlugin
    from .theme_file import ThemeT


class ExportConfig(CommonOomoxConfig):

    def __init__(
            self,
            config_name: str,
            default_config: dict[str, "Any"] | None = None,
            override_config: dict[str, "Any"] | None = None,
    ) -> None:
        super().__init__(
            config_name=config_name,
            default_config=default_config,
            override_config=override_config,
            config_dir=USER_EXPORT_CONFIG_DIR,
            force_reload=True,
        )


PossibleBaseClass = type[Gtk.Box | Gtk.Dialog]


class ExportDialogT(Gtk.Dialog):
    base_class: type[Gtk.Dialog]


class ExportBoxT(Gtk.Box):
    base_class: type[Gtk.Box]


ExportBaseClassT = TypeVar("ExportBaseClassT", ExportDialogT, ExportBoxT)

# # ExportWrapperBase = GObject.Object
ExportWrapperBase = Generic  # checkglobals-ignore


class ExportWrapper(Generic[ExportBaseClassT]):
    """
    Base class with ability to choose its parent class at the runtime.
    e.g. in case of Export functionality - to choose whatever it will be
    inside Gtk.Dialog or Gtk.Box.
    """

    base_class: PossibleBaseClass

    def __new__(  # type: ignore[misc]
            cls,
            *_args: "Any",
            base_class: PossibleBaseClass = Gtk.Dialog,
            **_kwargs: "Any",
    ) -> ExportBaseClassT:
        new_mro = []
        for base in cls.__mro__:
            if base is ExportWrapperBase:
                break
            new_mro.append(base)
        new_mro += list(base_class.__mro__)
        new_class: type[ExportBaseClassT]
        with SuppressWarningsFilter(
                warning_class=RuntimeWarning,
                message="Interface type gobject.GInterface has no Python implementation support",
        ):
            new_class = type(cls.__name__, tuple(new_mro), dict(cls.__dict__))
        nongobject_check_class_for_gobject_metas(new_class)
        result: ExportBaseClassT = super(  # type: ignore[arg-type]  # pylint: disable=bad-super-call,no-value-for-parameter  # noqa: E501,RUF100
            base_class, new_class,
        ).__new__(new_class)
        result.base_class = base_class  # type: ignore[assignment]
        return result

    def __init__(  # type: ignore[misc]
            self: ExportBaseClassT,
            title: str,
            transient_for: Gtk.Window,
            flags: int,
            *_args: "Any",
            **_kwargs: "Any",
    ) -> None:
        if self.base_class is Gtk.Dialog:
            self.base_class.__init__(self, title, transient_for, flags)  # type: ignore[call-arg,arg-type]
        elif self.base_class is Gtk.Box:
            self.base_class.__init__(
                self,
                orientation=Gtk.Orientation.VERTICAL,
                # spacing=5,
            )
        else:
            raise NotImplementedError

    def get_content_area(self: ExportBaseClassT) -> ExportBoxT | Gtk.Box:  # type: ignore[misc]
        if self.base_class is Gtk.Dialog:
            return super().get_content_area()  # type: ignore[misc]  # pylint: disable=no-member
        if self.base_class is Gtk.Box:
            return self  # type: ignore[return-value]
        raise NotImplementedError

    def set_default_size(self: ExportBaseClassT, width: int, height: int) -> None:  # type: ignore[misc]
        if self.base_class is Gtk.Dialog:
            super().set_default_size(width, height)  # type: ignore[misc]  # pylint: disable=no-member

    def set_title(self: ExportBaseClassT, title: str) -> None:  # type: ignore[misc]
        if self.base_class is Gtk.Dialog:
            super().set_title(title)  # type: ignore[misc]  # pylint: disable=no-member

    def dialog_done(self: ExportBaseClassT) -> None:  # type: ignore[misc]
        # pylint: disable=no-member
        if self.base_class is Gtk.Dialog:
            self.destroy()
        elif self.base_class is Gtk.Box:
            for child in self.get_children():
                self.remove(child)
            message = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
                spacing=4,
            )
            message.add(
                Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.BUTTON),
            )
            message.add(
                Gtk.Label(translate("Done!")),
            )
            message_align = Gtk.Box(
                orientation=Gtk.Orientation.HORIZONTAL,
            )
            message_align.set_center_widget(message)
            self.add(message_align)
            self.show_all()
        else:
            raise NotImplementedError


class ExportDialog(ExportWrapper):  # type: ignore[type-arg]

    colorscheme: "ThemeT"
    theme_name: str
    plugin: "OomoxPlugin"
    command: str  # deprecated from plugin API 1.1
    timeout = 300
    done: bool = False

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

    def _dismiss_button_callback(self, _widget: Gtk.Button) -> None:
        self.dialog_done()

    def show_text(self) -> None:
        if not self.scrolled_window.get_visible():
            self.box.add(self.scrolled_window)
            self.scrolled_window.show_all()

    def show_error(self) -> None:
        self.box.remove(self.label)
        self.box.remove(self.spinner)

        error_label = CenterLabel(
            label=translate("Something went wrong :("),
        )
        error_label.set_alignment(0.5, 0.5)

        error_dismiss_button = Gtk.Button(label=translate("_Dismiss"), use_underline=True)
        error_dismiss_button.connect("clicked", self._dismiss_button_callback)

        self.error_box.add(error_label)
        self.error_box.add(error_dismiss_button)
        self.error_box.show_all()
        self.box.add(self.error_box)

    def set_text(self, text: str) -> None:
        self.log.get_buffer().set_text(text)

    def __init__(  # pylint: disable=too-many-arguments
            self,
            transient_for: Gtk.Window,
            colorscheme: "ThemeT",
            theme_name: str,
            plugin: "OomoxPlugin",
            headline: str | None = None,
            width: int = 150,
            height: int = 80,
            base_class: type[ExportBaseClassT] = Gtk.Dialog,  # type: ignore[assignment]
            callback: "Callable[[], None] | None" = None,
            **_kwargs: "Any",
    ) -> None:
        headline = headline or translate("Export Theme")
        self.theme_name = "oomox-" + theme_name.split("/")[-1]

        # @TODO: make sure it doesn't break things:
        self.colorscheme = colorscheme
        self.callback = callback
        self.plugin = plugin
        # from .terminal import generate_terminal_colors_for_oomox
        # self.colorscheme = generate_terminal_colors_for_oomox(colorscheme)

        super().__init__(
            title=headline, transient_for=transient_for, flags=0, base_class=base_class,
        )
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

        self.show_all()  # type: ignore[attr-defined]  # pylint: disable=no-member
        self.box.add(self.spinner)

    def dialog_done(self) -> None:
        super().dialog_done()
        if self.callback:
            self.callback()

    def do_export(self) -> None:
        self.box.remove(self.options_box)
        self.box.remove(self.apply_button)
        self.show_text()
        self.scrolled_window.set_size_request(-1, 200)
        self.scrolled_window.show_all()
        self.spinner.show()
        self.spinner.start()
        self.set_title(translate("Exporting…"))

        def update_ui(text: str) -> None:
            self.set_text(text)

        def ui_done() -> None:
            self.done = True
            self.dialog_done()

        def ui_error() -> None:
            self.show_error()

        def do_export_thread() -> None:
            if self.done:
                print("Export already done")
                return
            self.label.set_text(translate("Please wait while\nnew colorscheme will be created."))
            self.label.show()
            captured_log = ""
            with subprocess.Popen(  # noqa: S603
                self.command,
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

        thread = Thread(target=do_export_thread)
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


# class ExportDialogWithOptions(FileBasedExportDialog, metaclass=GObjectABCMeta):
class ExportDialogWithOptions(FileBasedExportDialog):

    OPTIONS: ExportDialogWithOptionsOptions = ExportDialogWithOptionsOptions()

    config_name: str
    export_config: ExportConfig

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

    def load_state_from_config(self) -> None:
        for option_name, option in self.export_options.items():
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

    def __init__(
            self,
            transient_for: Gtk.Window,
            colorscheme: "ThemeT",
            theme_name: str,
            export_options: "dict[str, Any] | None" = None,
            override_options: dict[str, "Any"] | None = None,
            override_config: dict[str, "Any"] | None = None,
            headline: str | None = None,
            **kwargs: "Any",
    ) -> None:
        self.option_widgets: dict[str, Gtk.Widget] = {}
        self.export_options = override_options or export_options or {}
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
                for option_name, option in self.export_options.items()
            },
            override_config=override_config,
        )

        self.load_state_from_config()

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
            new_export_path = self.export_config[self.OPTIONS.DEFAULT_PATH].replace(
                "<THEME_NAME>",
                self.theme_name,
            )
            if self.theme_name not in new_export_path:
                new_export_path = os.path.join(
                    new_export_path,
                    self.theme_name,
                )
            self.option_widgets[self.OPTIONS.DEFAULT_PATH].set_text(  # type: ignore[attr-defined]
                new_export_path,
            )

    def remove_preset_name_from_path_config(self) -> None:
        export_path = os.path.expanduser(
            self.option_widgets[self.OPTIONS.DEFAULT_PATH].get_text(),  # type: ignore[attr-defined]
        )
        # new_destination_dir, _theme_name = export_path.rstrip("/").rsplit("/", 1)
        self.export_config[self.OPTIONS.DEFAULT_PATH] = export_path.replace(
            self.theme_name,
            "<THEME_NAME>",
        )
        self.export_config.save()

    def do_export(self) -> None:
        self.remove_preset_name_from_path_config()
        super().do_export()


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
        if os.environ.get("XDG_CURRENT_DESKTOP", "").lower() in {"kde", "lxqt"}:
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
