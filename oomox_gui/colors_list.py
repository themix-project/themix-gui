from gi.repository import Gtk

from .theme_model import theme_model
from .palette_cache import PaletteCache
from .helpers import (
    convert_theme_color_to_gdk, convert_gdk_to_theme_color,
    FALLBACK_COLOR
)
from .gtk_helpers import GObjectABCMeta, g_abstractproperty


def check_value_filter(value_filter_data, colorscheme):
    filter_results = []
    for key, values in value_filter_data.items():
        if not isinstance(values, list):
            values = [values, ]
        value_found = False
        for value in values:
            if colorscheme[key] == value:
                value_found = True
                continue
        filter_results.append(value_found)
    all_filters_passed = min(filter_results) is not False
    return all_filters_passed


class OomoxListBoxRow(Gtk.ListBoxRow, metaclass=GObjectABCMeta):

    key = None
    value = None
    changed_signal = None
    callback = None
    value_widget = None
    hbox = None

    @g_abstractproperty
    def set_value(self, value):
        pass

    def __init__(self, display_name, key, callback, value_widget):
        super().__init__()

        self.callback = callback
        self.key = key

        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.add(self.hbox)
        label = Gtk.Label(label=display_name, xalign=0)
        self.hbox.pack_start(label, True, True, 0)

        self.value_widget = value_widget
        self.hbox.pack_start(self.value_widget, False, True, 0)

    def disconnect_changed_signal(self):
        if self.changed_signal:
            self.value_widget.disconnect(self.changed_signal)


class NumericListBoxRow(OomoxListBoxRow):

    def connect_changed_signal(self):
        self.changed_signal = self.value_widget.connect("value-changed", self.on_value_changed)

    def set_value(self, value):
        self.disconnect_changed_signal()
        self.value = value
        self.value_widget.set_value(value)
        self.connect_changed_signal()

    def __init__(  # pylint: disable=too-many-arguments
            self,
            display_name, key,
            callback,
            init_value,
            min_value, max_value,
            step_increment,
            page_increment,
            page_size
    ):

        adjustment = Gtk.Adjustment(
            value=init_value,
            lower=min_value,
            upper=max_value,
            step_increment=step_increment,
            page_increment=page_increment,
            page_size=page_size
        )
        spinbutton = Gtk.SpinButton(
            adjustment=adjustment,
        )
        spinbutton.set_numeric(True)
        spinbutton.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)

        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            value_widget=spinbutton
        )


class FloatListBoxRow(NumericListBoxRow):

    def on_value_changed(self, spinbutton):
        raw_value = spinbutton.get_value()
        self.value = int(raw_value*100)/100  # limit float to 2 digits
        self.callback(self.key, self.value)

    def __init__(self, display_name, key, callback,  # pylint: disable=too-many-arguments
                 min_value=None, max_value=None):
        min_value = min_value or 0.0
        max_value = max_value or 10.0
        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            init_value=0.0,
            min_value=min_value,
            max_value=max_value,
            step_increment=0.01,
            page_increment=1.0,
            page_size=0.0
        )
        self.value_widget.set_digits(2)


class IntListBoxRow(NumericListBoxRow):

    def on_value_changed(self, spinbutton):
        self.value = spinbutton.get_value_as_int()
        self.callback(self.key, self.value)

    def __init__(self, display_name, key, callback,  # pylint: disable=too-many-arguments
                 min_value=None, max_value=None):
        min_value = min_value or 0
        max_value = max_value or 20
        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            init_value=0,
            min_value=min_value,
            max_value=max_value,
            step_increment=1,
            page_increment=10,
            page_size=0
        )


class BoolListBoxRow(OomoxListBoxRow):

    def connect_changed_signal(self):
        self.changed_signal = self.value_widget.connect("notify::active", self.on_switch_activated)

    def set_value(self, value):
        self.disconnect_changed_signal()
        self.value = value
        self.value_widget.set_active(value)
        self.connect_changed_signal()

    def on_switch_activated(self, switch, _gparam):
        self.value = switch.get_active()
        self.callback(self.key, self.value)

    def __init__(self, display_name, key, callback):
        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            value_widget=Gtk.Switch()
        )


class OptionsListBoxRow(OomoxListBoxRow):

    options = None
    vbox = None
    description_label = None
    _description_label_added = False

    def connect_changed_signal(self):
        self.changed_signal = self.value_widget.connect("changed", self.on_dropdown_changed)

    def on_dropdown_changed(self, combobox):
        value_id = combobox.get_active()
        self.value = self.options[value_id]['value']
        self.callback(self.key, self.value)

    def set_value(self, value):
        self.disconnect_changed_signal()
        self.value = value
        for option_id, option in enumerate(self.options):
            if value == option['value']:
                self.value_widget.set_active(option_id)
                if 'description' in option:
                    self.show_description_label()
                    self.description_label.set_text(option['description'])
                break
        self.connect_changed_signal()

    def show_description_label(self):
        if not self._description_label_added:
            self.vbox.add(self.description_label)
            self.description_label.show()
            self._description_label_added = True

    def __init__(self, display_name, key, options, callback):
        self.options = options
        options_store = Gtk.ListStore(str)
        for option in self.options:
            options_store.append([option.get('display_name', option['value'])])
        dropdown = Gtk.ComboBox.new_with_model(options_store)
        renderer_text = Gtk.CellRendererText()
        dropdown.pack_start(renderer_text, True)
        dropdown.add_attribute(renderer_text, "text", 0)

        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            value_widget=dropdown
        )

        self.remove(self.hbox)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.vbox)
        self.vbox.add(self.hbox)

        self.description_label = Gtk.Label(xalign=1)
        self.description_label.set_margin_top(3)
        self.description_label.set_margin_bottom(7)
        self.description_label.set_state_flags(Gtk.StateFlags.INSENSITIVE, False)


class OomoxColorSelectionDialog(Gtk.ColorSelectionDialog):

    gtk_color = None
    transient_for = None

    def _on_cancel(self, _button):
        self.gtk_color = None
        self.destroy()

    def _on_ok(self, _button):
        self.gtk_color = self.props.color_selection.get_current_rgba()
        PaletteCache.add_color(self.gtk_color)
        self.destroy()

    def _on_response(self, widget, result):
        if result == Gtk.ResponseType.DELETE_EVENT:
            self._on_cancel(widget)

    def __init__(self, transient_for, gtk_color):
        self.transient_for = transient_for
        self.gtk_color = gtk_color

        super().__init__(
            title=_("Choose a color..."),
            transient_for=transient_for,
            flags=0
        )
        self.set_transient_for(transient_for)
        self.props.color_selection.set_has_palette(True)

        self.props.color_selection.set_current_rgba(self.gtk_color)

        Gtk.Settings.get_default().props.gtk_color_palette = PaletteCache.get_gtk()

        self.props.cancel_button.connect("clicked", self._on_cancel)
        self.props.ok_button.connect("clicked", self._on_ok)
        self.connect("response", self._on_response)

        self.show_all()


class OomoxColorButton(Gtk.Button):

    gtk_color = None
    callback = None
    transient_for = None
    gtk_color_button = None
    color_image = None

    def set_rgba(self, gtk_color):
        self.gtk_color = gtk_color
        self.gtk_color_button.set_rgba(gtk_color)

    def on_click(self, _widget):
        color_selection_dialog = OomoxColorSelectionDialog(
            self.transient_for, self.gtk_color
        )
        color_selection_dialog.run()
        new_color = color_selection_dialog.gtk_color
        if new_color:
            self.set_rgba(new_color)
            self.callback(new_color)

    def set_value(self, value):
        self.set_rgba(convert_theme_color_to_gdk(value or FALLBACK_COLOR))

    def __init__(self, transient_for, callback):
        self.transient_for = transient_for

        self.callback = callback
        Gtk.Button.__init__(self)
        self.gtk_color_button = Gtk.ColorButton.new()
        self.color_image = self.gtk_color_button.get_child()
        self.set_image(self.color_image)
        self.connect("clicked", self.on_click)


class ColorListBoxRow(OomoxListBoxRow):

    color_button = None
    color_entry = None

    def connect_changed_signal(self):
        self.changed_signal = self.color_entry.connect("changed", self.on_color_input)

    def disconnect_changed_signal(self):
        if self.changed_signal:
            self.color_entry.disconnect(self.changed_signal)

    def on_color_input(self, widget, value=None):
        self.value = value or widget.get_text()
        if self.value == '':
            self.value = None
        if self.value:
            self.color_button.set_rgba(convert_theme_color_to_gdk(self.value))
        self.callback(self.key, self.value)

    def on_color_set(self, gtk_value):
        self.value = convert_gdk_to_theme_color(gtk_value)
        self.color_entry.set_text(self.value)

    def set_value(self, value):
        self.disconnect_changed_signal()
        self.value = value
        if value:
            self.color_entry.set_text(self.value)
            self.color_button.set_rgba(convert_theme_color_to_gdk(value))
        else:
            self.color_entry.set_text(_('<N/A>'))
            self.color_button.set_rgba(convert_theme_color_to_gdk(FALLBACK_COLOR))
        self.connect_changed_signal()

    def __init__(self, display_name, key, callback, transient_for):
        self.color_button = OomoxColorButton(
            transient_for=transient_for,
            callback=self.on_color_set
        )
        self.color_entry = Gtk.Entry(
            text=_('<none>'), width_chars=7, max_length=6
        )
        # unfortunately linked box is causing weird redraw issues
        # in current GTK version, let's leave it for later
        linked_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(
            linked_box.get_style_context(), "linked"
        )
        linked_box.add(self.color_entry)
        linked_box.add(self.color_button)
        super().__init__(
            display_name=display_name,
            key=key,
            callback=callback,
            value_widget=linked_box
        )


class SeparatorListBoxRow(Gtk.ListBoxRow):

    def __init__(self, display_name):
        super().__init__(activatable=False, selectable=False)

        label = Gtk.Label(xalign=0)
        label.set_markup("<b>{}</b>".format(display_name))

        hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        hbox.pack_start(Gtk.Label(), True, True, 2)
        hbox.pack_start(label, True, True, 4)

        self.add(hbox)


class ThemeColorsList(Gtk.Box):

    color_edited_callback = None
    transient_for = None
    theme = None

    listbox = None
    _all_rows = None
    _no_gui_row = None

    def color_edited(self, key, value):
        self.theme[key] = value
        self.color_edited_callback(self.theme)

    def build_theme_model_rows(self):
        self._no_gui_row = SeparatorListBoxRow(_("Can't be edited in GUI"))
        self.listbox.add(self._no_gui_row)
        self._all_rows = {}
        for theme_value in theme_model:
            key = theme_value.get('key') or theme_value['display_name']
            display_name = theme_value.get('display_name', key)
            row = None
            if theme_value['type'] == 'color':
                row = ColorListBoxRow(
                    display_name, key,
                    callback=self.color_edited,
                    transient_for=self.transient_for
                )
            elif theme_value['type'] == 'bool':
                row = BoolListBoxRow(
                    display_name, key, callback=self.color_edited
                )
            elif theme_value['type'] == 'int':
                row = IntListBoxRow(
                    display_name, key, callback=self.color_edited,
                    min_value=theme_value.get('min_value'),
                    max_value=theme_value.get('max_value')
                )
            elif theme_value['type'] == 'float':
                row = FloatListBoxRow(
                    display_name, key, callback=self.color_edited,
                    min_value=theme_value.get('min_value'),
                    max_value=theme_value.get('max_value')
                )
            elif theme_value['type'] == 'separator':
                row = SeparatorListBoxRow(display_name)
            elif theme_value['type'] == 'options':
                callback = None
                if key in [
                        'ICONS_STYLE', 'THEME_STYLE',
                        'TERMINAL_BASE_TEMPLATE', 'TERMINAL_THEME_MODE'
                ]:
                    def _callback(key, value):
                        self.color_edited(key, value)
                        self.open_theme(self.theme)
                    callback = _callback
                else:
                    callback = self.color_edited
                row = OptionsListBoxRow(
                    key=key,
                    display_name=display_name,
                    options=theme_value['options'],
                    callback=callback
                )
            if row:
                self._all_rows[key] = row
                self.listbox.add(row)

    def open_theme(self, theme):
        self.theme = theme
        if "NOGUI" in self.theme:
            self._no_gui_row.show()
        else:
            self._no_gui_row.hide()
        for theme_value in theme_model:
            key = theme_value.get('key') or theme_value['display_name']
            row = self._all_rows.get(key)
            if not row:
                continue
            if "NOGUI" in self.theme:
                row.hide()
                continue
            if theme_value.get('filter'):
                if not theme_value['filter'](theme):
                    row.hide()
                    continue
            if theme_value.get('value_filter'):
                if not check_value_filter(theme_value['value_filter'], theme):
                    row.hide()
                    continue
            if theme_value['type'] in ['color', 'options', 'bool', 'int', 'float']:
                row.set_value(self.theme[key])
            row.show()

    def __init__(self, color_edited_callback, transient_for):
        self.transient_for = transient_for
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.color_edited_callback = color_edited_callback

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.build_theme_model_rows()
        scrolled.add(self.listbox)

        theme_edit_label = Gtk.Label()
        theme_edit_label.set_text(_("Edit:"))
        self.pack_start(theme_edit_label, False, False, 0)
        self.pack_start(scrolled, True, True, 0)
