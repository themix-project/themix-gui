from typing import TYPE_CHECKING

from gi.repository import GLib, Gtk

from .color import (
    convert_gdk_to_theme_color,
    convert_theme_color_to_gdk,
)
from .config import FALLBACK_COLOR
from .gtk_helpers import GObjectABCMeta, ScaledImage, g_abstractproperty
from .i18n import translate
from .palette_cache import PaletteCache
from .theme_model import get_theme_model, get_theme_options_by_key

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import Any, Final

    from gi.repository import Gdk

    from .theme_file import ThemeT, ThemeValueT
    from .theme_model import Option


SECTION_MARGIN: "Final" = 20
LIST_ITEM_MARGIN: "Final" = 10


def check_value_filter(
        value_filter_data: "dict[str, list[ThemeValueT] | ThemeValueT]",
        colorscheme: "ThemeT",
) -> bool:
    filter_results = []
    for key, _values in value_filter_data.items():
        values = [_values] if not isinstance(_values, list) else _values
        value_found = False
        for value in values:
            if colorscheme.get(key) == value:
                value_found = True
                continue
        filter_results.append(value_found)
    return min(filter_results) is not False


class OomoxListBoxRow(Gtk.ListBoxRow, metaclass=GObjectABCMeta):

    key: str
    value: "ThemeValueT | None" = None
    value_widget: Gtk.Widget

    changed_signal: int | None = None
    hbox: Gtk.Box
    vbox: Gtk.Box
    description_label: Gtk.Label | None = None
    _description_label_added: bool = False

    # callback: "Callable[[str, Any], None]"
    if TYPE_CHECKING:
        @staticmethod
        def callback(key: str, value: "ThemeValueT") -> None:  # pylint: disable=method-hidden
            # mypy 🙄
            pass

    @g_abstractproperty
    def set_value(self, value: "Any") -> None:
        pass

    def __init__(
            self,
            display_name: str,
            key: str,
            callback: "Callable[[str, ThemeValueT], None]",
            value_widget: Gtk.Widget,
            colors_list: "ThemeColorsList",
    ) -> None:
        super().__init__(activatable=False)  # type: ignore[call-arg]

        self.callback = callback  # type: ignore[assignment]
        self.colors_list = colors_list
        self.key = key

        self.hbox = Gtk.Box(  # type: ignore[call-arg]
            orientation=Gtk.Orientation.HORIZONTAL, spacing=50, margin=LIST_ITEM_MARGIN,
        )
        label = Gtk.Label(label=display_name, xalign=0)  # type: ignore[call-arg]
        self.hbox.pack_start(label, True, True, 0)

        self.value_widget = value_widget
        self.hbox.pack_start(self.value_widget, False, True, 0)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.vbox)
        self.vbox.add(self.hbox)

    def disconnect_changed_signal(self) -> None:
        if self.changed_signal:
            self.value_widget.disconnect(self.changed_signal)

    def set_description(self, description_text: str | None = None) -> None:
        label_not_added = "Description label is set as added but it's not."
        if description_text:
            if not self._description_label_added:
                self.description_label = Gtk.Label(xalign=1)  # type: ignore[call-arg]
                self.description_label.set_line_wrap(True)
                self.description_label.set_margin_top(3)
                self.description_label.set_margin_bottom(7)
                self.description_label.set_state_flags(Gtk.StateFlags.INSENSITIVE, False)
                self.vbox.add(self.description_label)
                self.description_label.show()
                self._description_label_added = True
            if not self.description_label:
                raise RuntimeError(label_not_added)
            self.description_label.set_text(description_text)
        elif self._description_label_added:
            if not self.description_label:
                raise RuntimeError(label_not_added)
            self.vbox.remove(self.description_label)
            self._description_label_added = False


class NumericListBoxRow(OomoxListBoxRow):

    value: float
    value_widget: Gtk.SpinButton

    @g_abstractproperty
    def on_value_changed(self, widget: Gtk.SpinButton) -> None:
        pass

    def connect_changed_signal(self) -> None:
        self.changed_signal = self.value_widget.connect(
            "value-changed",
            self.on_value_changed,
        )

    def set_value(self, value: float) -> None:  # type: ignore[override]
        self.disconnect_changed_signal()
        self.value = value
        self.value_widget.set_value(value)
        self.connect_changed_signal()

    def __init__(  # pylint: disable=too-many-arguments
            self,
            display_name: str,
            key: str,
            callback: "Callable[[str, ThemeValueT], None]",
            colors_list: "ThemeColorsList",
            init_value: float,
            min_value: float,
            max_value: float,
            step_increment: float,
            page_increment: float,
            page_size: float,
    ) -> None:

        adjustment = Gtk.Adjustment(
            value=init_value,
            lower=min_value,
            upper=max_value,
            step_increment=step_increment,
            page_increment=page_increment,
            page_size=page_size,
        )
        spinbutton = Gtk.SpinButton(  # type: ignore[call-arg]
            adjustment=adjustment,
        )
        spinbutton.set_numeric(True)
        spinbutton.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)

        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            value_widget=spinbutton,
            colors_list=colors_list,
        )


class FloatListBoxRow(NumericListBoxRow):

    def on_value_changed(self, widget: Gtk.SpinButton) -> None:  # type: ignore[override]
        raw_value = widget.get_value()
        self.value = int(raw_value * 100) / 100  # limit float to 2 digits
        GLib.idle_add(self.callback, self.key, self.value)

    def __init__(
            self,
            display_name: str,
            key: str,
            callback: "Callable[[str, ThemeValueT], None]",
            colors_list: "ThemeColorsList",
            min_value: float | None = None,
            max_value: float | None = None,
    ) -> None:
        min_value = min_value or 0.0
        max_value = max_value or 10.0
        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            colors_list=colors_list,
            init_value=0.0,
            min_value=min_value,
            max_value=max_value,
            step_increment=0.01,
            page_increment=1.0,
            page_size=0.0,
        )
        self.value_widget.set_digits(2)  # type: ignore[arg-type]


class IntListBoxRow(NumericListBoxRow):

    def on_value_changed(self, widget: Gtk.SpinButton) -> None:  # type: ignore[override]
        self.value = widget.get_value_as_int()
        GLib.idle_add(self.callback, self.key, self.value)

    def __init__(
            self,
            display_name: str,
            key: str,
            callback: "Callable[[str, ThemeValueT], None]",
            colors_list: "ThemeColorsList",
            min_value: int | None = None,
            max_value: int | None = None,
    ) -> None:
        min_value = min_value or 0
        max_value = max_value or 20
        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            colors_list=colors_list,
            init_value=0,
            min_value=min_value,
            max_value=max_value,
            step_increment=1,
            page_increment=10,
            page_size=0,
        )


class BoolListBoxRow(OomoxListBoxRow):

    value_widget: Gtk.Switch

    def connect_changed_signal(self) -> None:
        self.changed_signal = self.value_widget.connect("notify::active", self.on_switch_activated)

    def set_value(self, value: bool) -> None:  # type: ignore[override]
        self.disconnect_changed_signal()
        self.value = value
        self.value_widget.set_active(value)
        self.connect_changed_signal()

    def on_switch_activated(self, switch: Gtk.Switch, _gparam: "Any") -> None:
        self.value = switch.get_active()
        GLib.idle_add(self.callback, self.key, self.value)

    def __init__(
            self,
            display_name: str,
            key: str,
            callback: "Callable[[str, ThemeValueT], None]",
            colors_list: "ThemeColorsList",
    ) -> None:
        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            colors_list=colors_list,
            value_widget=Gtk.Switch(),
        )


class OptionsListBoxRow(OomoxListBoxRow):

    options: "list[Option]"
    value_widget: Gtk.ComboBox

    def connect_changed_signal(self) -> None:
        self.changed_signal = self.value_widget.connect("changed", self.on_dropdown_changed)

    def on_dropdown_changed(self, combobox: Gtk.ComboBox) -> None:
        value_id = combobox.get_active()
        self.value = self.options[value_id]["value"]
        GLib.idle_add(self.callback, self.key, self.value)

    def set_value(self, value: str) -> None:  # type: ignore[override]
        self.disconnect_changed_signal()
        self.value = value
        for option_idx, option in enumerate(self.options):
            if value == option["value"]:
                self.value_widget.set_active(option_idx)
                if "description" in option:
                    self.set_description(option["description"])
                break
        self.connect_changed_signal()

    def __init__(
            self,
            display_name: str,
            key: str,
            options: "list[Option]",
            callback: "Callable[[str, ThemeValueT], None]",
            colors_list: "ThemeColorsList",
    ) -> None:
        self.options = options
        options_store = Gtk.ListStore(str)
        for option in self.options:
            options_store.append([option.get("display_name", option["value"])])
        dropdown = Gtk.ComboBox.new_with_model(options_store)
        renderer_text = Gtk.CellRendererText()
        dropdown.pack_start(renderer_text, True)
        dropdown.add_attribute(renderer_text, "text", 0)

        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            colors_list=colors_list,
            value_widget=dropdown,
        )


class OomoxColorSelectionDialog(Gtk.ColorSelectionDialog):

    gtk_color = None
    transient_for = None

    def _on_cancel(self, _button: Gtk.Button) -> None:
        self.gtk_color = None
        self.destroy()

    def _on_ok(self, _button: Gtk.Button) -> None:
        self.gtk_color = self.props.color_selection.get_current_rgba()  # type: ignore[attr-defined]
        PaletteCache.add_color(self.gtk_color)
        self.destroy()

    def _on_response(self, button: Gtk.Button, result: Gtk.ResponseType) -> None:
        if result == Gtk.ResponseType.DELETE_EVENT:
            self._on_cancel(button)

    def __init__(self, transient_for: Gtk.Window, gtk_color: "Gdk.RGBA") -> None:
        self.transient_for = transient_for
        self.gtk_color = gtk_color

        super().__init__(
            title=translate("Choose a Color…"),
            transient_for=transient_for,
            flags=0,
        )
        self.set_transient_for(transient_for)
        self.props.color_selection.set_has_palette(True)  # type: ignore[attr-defined]

        self.props.color_selection.set_current_rgba(self.gtk_color)  # type: ignore[attr-defined]

        settings = Gtk.Settings.get_default()
        if not settings:
            cant_load_palette_settings = "Can't load Gtk Palette settings"
            raise RuntimeError(cant_load_palette_settings)
        settings.props.gtk_color_palette = PaletteCache.get_gtk()  # type: ignore[attr-defined]

        self.props.cancel_button.connect("clicked", self._on_cancel)  # type: ignore[attr-defined]
        self.props.ok_button.connect("clicked", self._on_ok)  # type: ignore[attr-defined]
        self.connect("response", self._on_response)

        self.show_all()


class OomoxColorButton(Gtk.Button):

    gtk_color: "Gdk.RGBA"
    callback: "Callable[[Gdk.RGBA], None]"
    transient_for: Gtk.Window
    gtk_color_button: Gtk.ColorButton
    color_image: Gtk.Widget

    def set_rgba(self, gtk_color: "Gdk.RGBA") -> None:
        self.gtk_color = gtk_color
        self.gtk_color_button.set_rgba(gtk_color)

    def on_click(self, _widget: Gtk.Widget) -> None:
        color_selection_dialog = OomoxColorSelectionDialog(
            self.transient_for, self.gtk_color,
        )
        color_selection_dialog.run()
        new_color = color_selection_dialog.gtk_color
        if new_color:
            self.set_rgba(new_color)
            self.callback(new_color)

    def set_value(self, value: str) -> None:
        self.set_rgba(convert_theme_color_to_gdk(value or FALLBACK_COLOR))

    def __init__(
            self, transient_for: Gtk.Window, callback: "Callable[[Gdk.RGBA], None]",
    ) -> None:
        self.transient_for = transient_for

        self.callback = callback
        Gtk.Button.__init__(self)
        self.gtk_color_button = Gtk.ColorButton.new()
        self.color_image = self.gtk_color_button.get_child()
        self.set_image(self.color_image)
        self.connect("clicked", self.on_click)


class ColorDropdown(Gtk.MenuButton):

    colorbox: "ColorListBoxRow"
    drop_down: Gtk.Menu | None = None

    def build_dropdown_menu(self) -> Gtk.Menu:
        self.drop_down = Gtk.Menu()
        menu_items: "list[tuple[Gtk.MenuItem, Callable[[Gtk.MenuItem], None]]]" = []
        menu_items.append((
            Gtk.MenuItem(label=translate("Replace all instances")), self.replace_all_instances,
        ))

        for item in menu_items:
            self.drop_down.append(item[0])
            item[0].connect("activate", item[1])

        self.drop_down.show_all()
        return self.drop_down

    def replace_all_instances(self, _menu_item: "Any") -> None:

        color_selection_dialog = OomoxColorSelectionDialog(
            self.transient_for, self.colorbox.color_button.gtk_color,
        )
        color_selection_dialog.run()
        new_color = color_selection_dialog.gtk_color
        if new_color:
            new_color_string = convert_gdk_to_theme_color(new_color)
            old_color = self.colorbox.color_button.gtk_color
            old_color_string = convert_gdk_to_theme_color(old_color)
            self.colorbox.colors_list.replace_all(old_color_string, new_color_string)

    def __init__(self, transient_for: Gtk.Window, colorbox: "ColorListBoxRow") -> None:
        super().__init__()
        self.transient_for = transient_for
        self.colorbox = colorbox
        self.set_popup(self.build_dropdown_menu())


class ColorListBoxRow(OomoxListBoxRow):

    color_button: OomoxColorButton
    color_entry: Gtk.Entry
    menu_button: ColorDropdown

    def connect_changed_signal(self) -> None:
        self.changed_signal = self.color_entry.connect("changed", self.on_color_input)

    def disconnect_changed_signal(self) -> None:
        if self.changed_signal:
            self.color_entry.disconnect(self.changed_signal)

    def on_color_input(self, widget: Gtk.Entry, value: str | None = None) -> None:
        self.value = value or widget.get_text()
        if not self.value:
            self.value = None
        if self.value:
            self.color_button.set_rgba(convert_theme_color_to_gdk(self.value))
        GLib.idle_add(self.callback, self.key, self.value)

    def on_color_set(self, gtk_value: "Gdk.RGBA") -> None:
        self.value = convert_gdk_to_theme_color(gtk_value)
        self.color_entry.set_text(self.value)

    def set_value(self, value: str) -> None:  # type: ignore[override]
        self.disconnect_changed_signal()
        self.value = value
        if value:
            self.color_entry.set_text(self.value)
            self.color_button.set_rgba(convert_theme_color_to_gdk(value))
        else:
            self.color_entry.set_text(translate("<N/A>"))
            self.color_button.set_rgba(convert_theme_color_to_gdk(FALLBACK_COLOR))
        self.connect_changed_signal()

    def __init__(
            self,
            display_name: str,
            key: str,
            callback: "Callable[[str, ThemeValueT], None]",
            transient_for: Gtk.Window,
            colors_list: "ThemeColorsList",
    ) -> None:
        self.color_button = OomoxColorButton(
            transient_for=transient_for,
            callback=self.on_color_set,
        )
        self.color_entry = Gtk.Entry(  # type: ignore[call-arg]
            text=translate("<none>"), width_chars=6, max_length=6,
        )
        self.menu_button = ColorDropdown(transient_for, self)
        self.color_entry.get_style_context().add_class(Gtk.STYLE_CLASS_MONOSPACE)
        linked_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(
            linked_box.get_style_context(), "linked",
        )
        linked_box.add(self.color_entry)
        linked_box.add(self.color_button)
        linked_box.add(self.menu_button)
        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            colors_list=colors_list,
            value_widget=linked_box,
        )


class ImagePathListBoxRow(OomoxListBoxRow):

    value_widget: ScaledImage

    def set_value(self, value: str) -> None:  # type: ignore[override]
        with open(value, "rb") as image_file:
            img_bytes = image_file.read()
            self.value_widget.set_from_bytes(img_bytes)

    def __init__(
            self,
            display_name: str,
            key: str,
            callback: "Callable[[str, ThemeValueT], None]",
            colors_list: "ThemeColorsList",
    ) -> None:

        image = ScaledImage(width=120)

        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            colors_list=colors_list,
            value_widget=image,
        )


class SectionHeader(Gtk.Box):

    def set_markup(self, markup: str) -> None:
        self.label.set_markup(f"<b>{markup}</b>")

    def __init__(self, display_name: str | None = None) -> None:
        # super().__init__(activatable=False, selectable=False)
        super().__init__()

        self.label = Gtk.Label(xalign=0)  # type: ignore[call-arg]
        if display_name:
            self.set_markup(display_name)

        # hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # hbox.pack_start(Gtk.Label(), True, True, 2)
        # hbox.pack_start(self.label, True, True, 4)

        # self.add(hbox)

        self.add(self.label)


class SectionListBox(Gtk.Box):

    def __init__(self) -> None:
        super().__init__(  # type: ignore[call-arg]
            orientation=Gtk.Orientation.VERTICAL,
            margin=SECTION_MARGIN,
        )
        # self.set_margin_bottom(SECTION_MARGIN//2)
        self.set_margin_top(SECTION_MARGIN // 2)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)

        def update_listbox_header(row: Gtk.ListBoxRow, before: bool) -> None:
            if before and not row.get_header():
                row.set_header(
                    Gtk.Separator(  # type: ignore[call-arg]
                        orientation=Gtk.Orientation.HORIZONTAL,
                    ),
                )

        self.listbox.set_header_func(update_listbox_header)

        # self.titlebox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.titlebox = Gtk.Stack()
        self.titlebox.set_margin_bottom(LIST_ITEM_MARGIN)
        super().add(self.titlebox)
        # super().add(self.listbox)
        frame = Gtk.Frame()
        frame.add(self.listbox)
        super().add(frame)

    def add(self, widget: Gtk.Widget) -> None:  # pylint: disable=arguments-differ
        self.listbox.add(widget)

    def add_title(self, *args: "Any", **kwargs: "Any") -> None:
        self.titlebox.add(*args, **kwargs)


class ThemeColorsList(Gtk.ScrolledWindow):

    color_edited_callback: "Callable[[ThemeT], None]"
    theme_reload_callback: "Callable[[], ThemeT]"
    transient_for: Gtk.Window
    theme: "ThemeT"

    mainbox: Gtk.Box
    listbox = None
    _all_rows: dict[str, dict[int, OomoxListBoxRow | SectionHeader]]
    _error_messages_row: SectionHeader

    def color_edited(self, key: str, value: "ThemeValueT") -> None:
        self.theme[key] = value
        self.color_edited_callback(self.theme)

    def build_theme_model_rows(self) -> None:  # pylint: disable=too-many-branches
        self._error_messages_row = SectionHeader()
        self.mainbox.add(self._error_messages_row)
        self._all_rows = {}
        self._all_section_boxes = {}
        for section_id, section in get_theme_model().items():
            self._all_section_boxes[section_id] = section_box = SectionListBox()
            for option_idx, theme_value in enumerate(section):
                key: str = theme_value.get(  # type: ignore[assignment]
                    "key", theme_value.get("display_name"),
                )
                if (not key) and (theme_value.get("type") != "separator"):
                    print(
                        f"build_theme_model_rows: WARNING:"
                        f" theme value {theme_value} doesn't have a `key`",
                    )
                    continue
                display_name: str = theme_value.get("display_name", key)
                if not display_name:
                    no_display_name = (
                        f"build_theme_model_rows: ERROR:"
                        f" theme value {theme_value} doesn't have a `display_name`",
                    )
                    raise RuntimeError(no_display_name)
                row: OomoxListBoxRow | SectionHeader | None = None

                callbacks = [self.color_edited]
                if theme_value.get("reload_theme"):
                    def _callback(key: str, value: "ThemeValueT") -> None:
                        for theme_option in get_theme_options_by_key(key):
                            theme_option["fallback_value"] = value
                        self.theme = self.theme_reload_callback()
                    callbacks = [_callback]
                elif theme_value.get("reload_options") or key in [
                        "ICONS_STYLE", "THEME_STYLE",
                        "TERMINAL_BASE_TEMPLATE", "TERMINAL_THEME_MODE",
                        "TERMINAL_THEME_AUTO_BGFG", "TERMINAL_FG", "TERMINAL_BG",
                ]:
                    def _callback(  # pylint:disable=unused-argument
                            key: str,  # noqa: ARG001
                            value: "ThemeValueT",  # noqa: ARG001
                    ) -> None:
                        self.open_theme(self.theme)
                    callbacks += [_callback]

                def create_callback(
                        _callbacks: "Sequence[Callable[[str, ThemeValueT], None]]",
                ) -> "Callable[[str, ThemeValueT], None]":
                    def _callback(key2: str, value: "ThemeValueT") -> None:
                        for each in _callbacks:
                            each(key2, value)

                    return _callback

                callback = create_callback(callbacks)
                standard_kwargs = {"colors_list": self, "callback": callback}

                if theme_value["type"] == "color":
                    row = ColorListBoxRow(
                        display_name, key,
                        transient_for=self.transient_for,
                        **standard_kwargs,  # type: ignore[arg-type]
                    )
                elif theme_value["type"] == "bool":
                    row = BoolListBoxRow(
                        display_name, key,
                        **standard_kwargs,  # type: ignore[arg-type]
                    )
                elif theme_value["type"] == "int":
                    row = IntListBoxRow(
                        display_name, key,
                        min_value=theme_value.get("min_value"),
                        max_value=theme_value.get("max_value"),
                        **standard_kwargs,  # type: ignore[arg-type]
                    )
                elif theme_value["type"] == "float":
                    row = FloatListBoxRow(
                        display_name, key,
                        min_value=theme_value.get("min_value"),
                        max_value=theme_value.get("max_value"),
                        **standard_kwargs,  # type: ignore[arg-type]
                    )
                elif theme_value["type"] == "separator":
                    row = SectionHeader(display_name)
                elif theme_value["type"] == "image_path":
                    row = ImagePathListBoxRow(
                        display_name, key,
                        **standard_kwargs,  # type: ignore[arg-type]
                    )
                elif theme_value["type"] == "options":
                    row = OptionsListBoxRow(
                        key=key,
                        display_name=display_name,
                        options=theme_value["options"],
                        **standard_kwargs,  # type: ignore[arg-type]
                    )
                if row:
                    self._all_rows.setdefault(section_id, {})[option_idx] = row
                    if isinstance(row, SectionHeader):
                        section_box.add_title(row)
                    else:
                        section_box.add(row)

            self.mainbox.add(section_box)

    def open_theme(  # pylint: disable=too-many-branches,too-many-locals
            self, theme: "ThemeT",
    ) -> None:
        self.theme = theme
        error_messages = []
        if "NOGUI" in theme:
            error_messages.append(translate("Can't Be Edited in GUI"))

        for section_id, section in get_theme_model().items():
            rows_displayed_in_section = 0
            for option_idx, theme_value in enumerate(section):
                key: str = theme_value.get(  # type: ignore[assignment]
                    "key", theme_value.get("display_name"),
                )
                if (not key) and (theme_value.get("type") != "separator"):
                    print(
                        f"open_theme: WARNING:"
                        f" theme value {theme_value} doesn't have a `key`",
                    )
                    continue
                display_name: str = theme_value.get("display_name", key)
                if not display_name:
                    no_display_name = (
                        f"build_theme_model_rows: ERROR:"
                        f" theme value {theme_value} doesn't have a `display_name`",
                    )
                    raise RuntimeError(no_display_name)
                if isinstance(theme.get(key or display_name), Exception):
                    error_messages.append(str(theme[key or display_name]))
                    continue
                row: OomoxListBoxRow | SectionHeader | None = \
                    self._all_rows.get(section_id, {}).get(option_idx)

                if not row:
                    continue
                if "NOGUI" in theme:
                    row.hide()
                    continue
                if (filter_func := theme_value.get("filter")) and not filter_func(theme):
                    row.hide()
                    continue
                value_filter: "dict[str, ThemeValueT | list[ThemeValueT]] | None"
                if (
                        (value_filter := theme_value.get("value_filter"))
                        and not check_value_filter(value_filter, theme)
                ):
                    row.hide()
                    continue
                if theme_value["type"] in (
                        "color", "options", "bool", "int", "float", "image_path",
                ):
                    if not isinstance(row, OomoxListBoxRow):
                        wrong_row_type = (
                            f"Row is of type {theme_value['type']}"
                            f" is not OomoxListBoxRow",
                        )
                        raise TypeError(wrong_row_type)
                    row.set_value(theme[key])  # type: ignore[call-arg]
                row.show()
                rows_displayed_in_section += 1

            section_box = self._all_section_boxes[section_id]
            if rows_displayed_in_section == 0:
                section_box.hide()
            else:
                section_box.show()
        if error_messages:
            self._error_messages_row.set_markup("\n".join(error_messages))
            self._error_messages_row.show()
        else:
            self._error_messages_row.hide()

    def hide_all_rows(self) -> None:
        self._error_messages_row.hide()
        for section_id in get_theme_model():  # pylint: disable=not-an-iterable
            self._all_section_boxes[section_id].hide()

    def replace_all(self, old_value: str, new_value: str) -> None:
        for section_rows in self._all_rows.values():
            for row in section_rows.values():
                if (
                        isinstance(row, OomoxListBoxRow) and
                        row.value == old_value
                ):
                    row.set_value(new_value)  # type: ignore[call-arg]
                    row.callback(row.key, row.value)

    def __init__(
            self,
            color_edited_callback: "Callable[[ThemeT], None]",
            theme_reload_callback: "Callable[[], ThemeT]",
            transient_for: Gtk.Window,
    ) -> None:
        self.transient_for = transient_for
        super().__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.color_edited_callback = color_edited_callback
        self.theme_reload_callback = theme_reload_callback

        self.mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.build_theme_model_rows()
        self.add(self.mainbox)
