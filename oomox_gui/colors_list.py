from gi.repository import Gtk

from .theme_model import theme_model
from .helpers import (
    convert_theme_color_to_gdk, convert_gdk_to_theme_color,
    load_palette, save_palette, FALLBACK_COLOR
)


class FloatListBoxRow(Gtk.ListBoxRow):

    changed_signal = None

    def connect_changed_signal(self):
        self.changed_signal = self.spinbutton.connect("value-changed", self.on_value_changed)

    def disconnect_changed_signal(self):
        if self.changed_signal:
            self.spinbutton.disconnect(self.changed_signal)

    def set_value(self, value):
        self.disconnect_changed_signal()
        self.value = value
        self.spinbutton.set_value(value)
        self.connect_changed_signal()

    def on_value_changed(self, spinbutton):
        self.value = spinbutton.get_value()
        self.color_set_callback(self.key, self.value)

    def __init__(self, display_name, key, callback, value=None):
        super().__init__()

        self.color_set_callback = callback
        self.key = key

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.add(hbox)
        label = Gtk.Label(display_name, xalign=0)
        hbox.pack_start(label, True, True, 0)

        adjustment = Gtk.Adjustment(value or 0, 0.0, 4.0, 0.01, 10.0, 0)
        spinbutton = Gtk.SpinButton()
        spinbutton.set_digits(2)
        spinbutton.set_adjustment(adjustment)
        spinbutton.set_numeric(True)
        spinbutton.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.spinbutton = spinbutton
        hbox.pack_start(spinbutton, False, False, 0)

        if value:
            self.set_value(value)


class IntListBoxRow(Gtk.ListBoxRow):

    changed_signal = None

    def connect_changed_signal(self):
        self.changed_signal = self.spinbutton.connect("value-changed", self.on_value_changed)

    def disconnect_changed_signal(self):
        if self.changed_signal:
            self.spinbutton.disconnect(self.changed_signal)

    def set_value(self, value):
        self.disconnect_changed_signal()
        self.value = value
        self.spinbutton.set_value(value)
        self.connect_changed_signal()

    def on_value_changed(self, spinbutton):
        self.value = spinbutton.get_value_as_int()
        self.color_set_callback(self.key, self.value)

    def __init__(self, display_name, key, callback, value=None):
        super().__init__()

        self.color_set_callback = callback
        self.key = key

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.add(hbox)
        label = Gtk.Label(display_name, xalign=0)
        hbox.pack_start(label, True, True, 0)

        adjustment = Gtk.Adjustment(value or 0, 0, 20, 1, 10, 0)
        spinbutton = Gtk.SpinButton()
        spinbutton.set_adjustment(adjustment)
        spinbutton.set_numeric(True)
        spinbutton.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.spinbutton = spinbutton
        hbox.pack_start(spinbutton, False, False, 0)

        if value:
            self.set_value(value)


class BoolListBoxRow(Gtk.ListBoxRow):

    changed_signal = None

    def connect_changed_signal(self):
        self.changed_signal = self.switch.connect("notify::active", self.on_switch_activated)

    def disconnect_changed_signal(self):
        if self.changed_signal:
            self.switch.disconnect(self.changed_signal)

    def set_value(self, value):
        self.disconnect_changed_signal()
        self.value = value
        self.switch.set_active(value)
        self.connect_changed_signal()

    def on_switch_activated(self, switch, gparam):
        self.value = switch.get_active()
        self.color_set_callback(self.key, self.value)

    def __init__(self, display_name, key, callback, value=None):
        super().__init__()

        self.color_set_callback = callback
        self.key = key

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.add(hbox)
        label = Gtk.Label(display_name, xalign=0)
        hbox.pack_start(label, True, True, 0)

        self.switch = Gtk.Switch()
        hbox.pack_start(self.switch, False, True, 0)

        if value is not None:
            self.set_value(value)


class OptionsListBoxRow(Gtk.ListBoxRow):

    dropdown = None
    changed_signal = None

    def connect_changed_signal(self):
        self.changed_signal = self.dropdown.connect("changed", self.on_dropdown_changed)

    def disconnect_changed_signal(self):
        if self.changed_signal:
            self.dropdown.disconnect(self.changed_signal)

    def on_dropdown_changed(self, combobox):
        value_id = combobox.get_active()
        self.value = self.options[value_id]['value']
        self.callback(self.key, self.value)

    def set_value(self, value):
        self.disconnect_changed_signal()
        self.value = value
        for option_id, option in enumerate(self.options):
            if value == option['value']:
                self.dropdown.set_active(option_id)
        self.connect_changed_signal()

    def __init__(self, display_name, key, options, callback, value=None):
        super().__init__()

        self.callback = callback
        self.key = key
        self.options = options

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.add(hbox)
        label = Gtk.Label(display_name, xalign=0)
        hbox.pack_start(label, True, True, 0)

        options_store = Gtk.ListStore(str)
        for option_id, option in enumerate(self.options):
            options_store.append([option.get('display_name', option['value'])])
        dropdown = Gtk.ComboBox.new_with_model(options_store)
        renderer_text = Gtk.CellRendererText()
        dropdown.pack_start(renderer_text, True)
        dropdown.add_attribute(renderer_text, "text", 0)
        self.dropdown = dropdown
        hbox.pack_start(dropdown, False, True, 0)

        if value:
            self.set_value(value)


palette_cache = None


class OomoxColorSelectionDialog(Gtk.ColorSelectionDialog):

    parent_window = None
    gtk_color = None

    def on_cancel(self, button):
        self.gtk_color = None
        self.destroy()

    def on_ok(self, button):
        global palette_cache
        self.gtk_color = self.props.color_selection.get_current_rgba()
        gtk_color_converted = self.gtk_color.to_color().to_string()
        palette_cache_list = [
            string for string in palette_cache.split(':')
            if string != ''
        ]
        if gtk_color_converted not in palette_cache_list:
            palette_cache_list = (
                [gtk_color_converted] + palette_cache_list
            )[:20]
            palette_cache = ':'.join(palette_cache_list)
            save_palette(palette_cache_list)
        self.destroy()

    def on_response(self, widget, result):
        if result == -4:
            return self.on_cancel(widget)

    def __init__(self, parent, gtk_color):
        global palette_cache
        self.gtk_color = gtk_color
        self.parent_window = parent

        Gtk.ColorSelectionDialog.__init__(self, _("Choose a color..."),
                                          parent, 0)
        self.set_transient_for(parent)
        self.props.color_selection.set_has_palette(True)

        self.props.color_selection.set_current_rgba(self.gtk_color)
        if not palette_cache:
            palette_cache = ':'.join(load_palette())

        Gtk.Settings.get_default().props.gtk_color_palette = palette_cache

        self.props.cancel_button.connect("clicked", self.on_cancel)
        self.props.ok_button.connect("clicked", self.on_ok)
        self.connect("response", self.on_response)

        self.show_all()


class OomoxColorButton(Gtk.Button):

    gtk_color = None
    callback = None
    parent_window = None
    gtk_color_button = None
    color_image = None

    def set_rgba(self, gtk_color):
        self.gtk_color = gtk_color
        self.gtk_color_button.set_rgba(gtk_color)

    def on_click(self, widget):
        color_selection_dialog = OomoxColorSelectionDialog(
            self.parent_window, self.gtk_color
        )
        color_selection_dialog.run()
        new_color = color_selection_dialog.gtk_color
        if new_color:
            self.set_rgba(new_color)
            self.callback(new_color)

    def set_value(self, value):
        self.set_rgba(convert_theme_color_to_gdk(value or FALLBACK_COLOR))

    def __init__(self, parent_window, callback, value=None):
        self.parent_window = parent_window

        self.callback = callback
        Gtk.Button.__init__(self)
        self.gtk_color_button = Gtk.ColorButton.new()
        self.color_image = self.gtk_color_button.get_child()
        self.set_image(self.color_image)
        self.connect("clicked", self.on_click)
        if value:
            self.set_value(value)


class ColorListBoxRow(Gtk.ListBoxRow):

    parent_window = None
    changed_signal = None

    def connect_changed_signal(self):
        self.changed_signal = self.color_entry.connect("changed", self.on_color_input)

    def disconnect_changed_signal(self):
        if self.changed_signal:
            self.color_entry.disconnect(self.changed_signal)

    def on_color_input(self, widget, skip_callback=False):
        self.value = widget.get_text()
        if self.value == '':
            self.value = None
        if self.value:
            self.color_button.set_rgba(convert_theme_color_to_gdk(self.value))
        if not skip_callback:
            self.callback(self.key, self.value)

    def on_color_set(self, gtk_value):
        self.value = convert_gdk_to_theme_color(gtk_value)
        self.color_entry.set_text(self.value)

    def set_value(self, value):
        self.disconnect_changed_signal()
        self.value = value
        self.color_entry.set_text(self.value)
        self.on_color_input(self.color_entry, skip_callback=True)
        self.connect_changed_signal()

    def __init__(self, display_name, key, callback, parent, value=None):
        self.parent_window = parent
        super().__init__()

        self.callback = callback
        self.key = key

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.add(hbox)
        label = Gtk.Label(display_name, xalign=0)
        hbox.pack_start(label, True, True, 0)

        self.color_button = OomoxColorButton(
            parent_window=self.parent_window,
            callback=self.on_color_set
        )
        # @TODO:
        if True:
            self.color_entry = Gtk.Entry(
                text=value or _('<none>'), width_chars=7, max_length=6
            )
            # unfortunately linked box is causing weird redraw issues
            # in current GTK version, let's leave it for later
            linked_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            Gtk.StyleContext.add_class(
                linked_box.get_style_context(), "linked"
            )
            linked_box.add(self.color_entry)
            linked_box.add(self.color_button)
            hbox.pack_start(linked_box, False, True, 0)
        else:
            self.color_entry = Gtk.Entry(
                text=value or _('<none>'), width_chars=8, max_length=6
            )
            hbox.pack_start(self.color_entry, False, True, 0)
            hbox.pack_start(self.color_button, False, True, 0)
            # ## ### #### ##### ###### #######
        if value:
            self.set_value(value)


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

    theme = None
    parent = None

    _all_rows = None
    _no_gui_row = None

    def color_edited(self, key, value):
        self.theme[key] = value
        self.color_edited_callback(self.theme)

    def build_theme_model_rows(self):
        self._no_gui_row = Gtk.ListBoxRow()
        self._no_gui_row.add(Gtk.Label(_("Can't be edited in GUI")))
        self._all_rows = {}
        for theme_value in theme_model:
            key = theme_value.get('key') or theme_value['display_name']
            display_name = theme_value.get('display_name', key)
            row = None
            if theme_value['type'] == 'color':
                row = ColorListBoxRow(
                    display_name, key,
                    callback=self.color_edited,
                    parent=self.parent
                )
            elif theme_value['type'] == 'bool':
                row = BoolListBoxRow(
                    display_name, key, callback=self.color_edited
                )
            elif theme_value['type'] == 'int':
                row = IntListBoxRow(
                    display_name, key, callback=self.color_edited
                )
            elif theme_value['type'] == 'float':
                row = FloatListBoxRow(
                    display_name, key, callback=self.color_edited
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
                    display_name, key,
                    options=theme_value['options'],
                    callback=callback
                )
            if row:
                self._all_rows[key] = row

    def open_theme(self, theme):
        self.theme = theme
        for child in self.listbox.get_children():
            # @TODO: refactor: populate listbox on init(done); and only
            # show/hide listbox items when opening the theme
            self.listbox.remove(child)
        if "NOGUI" in self.theme:
            self.listbox.add(self._no_gui_row)
        else:
            for theme_value in theme_model:
                if theme_value.get('filter'):
                    if not theme_value['filter'](theme):
                        continue
                key = theme_value.get('key') or theme_value['display_name']
                row = self._all_rows.get(key)
                if not row:
                    continue
                if theme_value['type'] in ['color', 'options', 'bool', 'int', 'float']:
                    row.set_value(self.theme[key])
                self.listbox.add(row)
        self.listbox.show_all()

    def __init__(self, color_edited_callback, parent):
        self.parent = parent
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
