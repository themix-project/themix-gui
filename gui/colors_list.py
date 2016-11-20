from gi.repository import Gtk

from .theme_model import theme_model
from .helpers import (
    convert_theme_color_to_gdk, convert_gdk_to_theme_color,
    load_palette, save_palette
)


class FloatListBoxRow(Gtk.ListBoxRow):

    def on_value_changed(self, spinbutton):
        self.value = spinbutton.get_value()
        self.color_set_callback(self.key, self.value)

    def __init__(self, display_name, key, value, color_set_callback):
        super().__init__()

        self.color_set_callback = color_set_callback
        self.key = key
        self.value = value

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.add(hbox)
        label = Gtk.Label(display_name, xalign=0)
        hbox.pack_start(label, True, True, 0)

        adjustment = Gtk.Adjustment(value, 0.0, 4.0, 0.01, 10.0, 0)
        spinbutton = Gtk.SpinButton()
        spinbutton.set_digits(2)
        spinbutton.set_adjustment(adjustment)
        spinbutton.set_numeric(True)
        spinbutton.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        spinbutton.set_value(value)  # idk why it's needed if value is in~
        # ~the adjustment already
        spinbutton.connect("value-changed", self.on_value_changed)
        hbox.pack_start(spinbutton, False, False, 0)


class IntListBoxRow(Gtk.ListBoxRow):

    def on_value_changed(self, spinbutton):
        self.value = spinbutton.get_value_as_int()
        self.color_set_callback(self.key, self.value)

    def __init__(self, display_name, key, value, color_set_callback):
        super().__init__()

        self.color_set_callback = color_set_callback
        self.key = key
        self.value = value

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.add(hbox)
        label = Gtk.Label(display_name, xalign=0)
        hbox.pack_start(label, True, True, 0)

        adjustment = Gtk.Adjustment(value, 0, 20, 1, 10, 0)
        spinbutton = Gtk.SpinButton()
        spinbutton.set_adjustment(adjustment)
        spinbutton.set_numeric(True)
        spinbutton.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        spinbutton.set_value(value)  # idk why it's needed if value is in~
        # ~the adjustment already
        spinbutton.connect("value-changed", self.on_value_changed)
        hbox.pack_start(spinbutton, False, False, 0)


class BoolListBoxRow(Gtk.ListBoxRow):

    def on_switch_activated(self, switch, gparam):
        self.value = switch.get_active()
        self.color_set_callback(self.key, self.value)

    def __init__(self, display_name, key, value, color_set_callback):
        super().__init__()

        self.color_set_callback = color_set_callback
        self.key = key
        self.value = value

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.add(hbox)
        label = Gtk.Label(display_name, xalign=0)
        hbox.pack_start(label, True, True, 0)

        switch = Gtk.Switch()
        switch.connect("notify::active", self.on_switch_activated)
        switch.set_active(value)
        hbox.pack_start(switch, False, True, 0)


class OptionsListBoxRow(Gtk.ListBoxRow):

    def on_dropdown_changed(self, combobox):
        value_id = combobox.get_active()
        self.value = self.options[value_id]['value']
        self.callback(self.key, self.value)

    def __init__(self, display_name, key, value, options, callback):
        super().__init__()

        self.callback = callback
        self.key = key
        self.value = value
        self.options = options

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.add(hbox)
        label = Gtk.Label(display_name, xalign=0)
        hbox.pack_start(label, True, True, 0)

        options_store = Gtk.ListStore(str)
        selected_value_id = 0
        for option_id, option in enumerate(self.options):
            options_store.append([option['display_name']])
            if value == option['value']:
                selected_value_id = option_id
        dropdown = Gtk.ComboBox.new_with_model(options_store)
        dropdown.set_active(selected_value_id)
        renderer_text = Gtk.CellRendererText()
        dropdown.pack_start(renderer_text, True)
        dropdown.add_attribute(renderer_text, "text", 0)
        dropdown.connect("changed", self.on_dropdown_changed)
        hbox.pack_start(dropdown, False, True, 0)


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

        Gtk.ColorSelectionDialog.__init__(self, "Choose a color...", parent, 0)
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
    color_button = None
    color_image = None

    def set_rgba(self, gtk_color):
        self.gtk_color = gtk_color
        self.color_button.set_rgba(gtk_color)

    def on_click(self, widget):
        color_selection_dialog = OomoxColorSelectionDialog(
            self.parent_window, self.gtk_color
        )
        color_selection_dialog.run()
        new_color = color_selection_dialog.gtk_color
        if new_color:
            self.set_rgba(new_color)
            self.callback(new_color)

    def __init__(self, value, parent_window, callback):
        self.parent_window = parent_window
        self.gtk_color = convert_theme_color_to_gdk(value)
        self.callback = callback
        Gtk.Button.__init__(self)
        self.color_button = Gtk.ColorButton.new_with_rgba(
            self.gtk_color
        )
        self.color_image = self.color_button.get_child()
        self.set_image(self.color_image)
        self.connect("clicked", self.on_click)


class ColorListBoxRow(Gtk.ListBoxRow):

    parent_window = None

    def on_color_input(self, widget):
        self.value = widget.get_text()
        self.color_button.set_rgba(convert_theme_color_to_gdk(self.value))
        self.color_set_callback(self.key, self.value)

    def on_color_set(self, gtk_value):
        self.value = convert_gdk_to_theme_color(gtk_value)
        self.color_entry.set_text(self.value)
        self.color_set_callback(self.key, self.value)

    def __init__(self, display_name, key, value, color_set_callback, parent):
        self.parent_window = parent
        super().__init__()

        self.color_set_callback = color_set_callback
        self.key = key
        self.value = value

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.add(hbox)
        label = Gtk.Label(display_name, xalign=0)
        hbox.pack_start(label, True, True, 0)

        # @TODO:
        if False:
            # unfortunately linked box is causing weird redraw issues
            # in current GTK version, let's leave it for later
            linked_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            Gtk.StyleContext.add_class(
                linked_box.get_style_context(), "linked"
            )
            self.color_entry = Gtk.Entry(text=value, width_chars=8)
            self.color_entry.connect("changed", self.on_color_input)
            linked_box.add(self.color_entry)
            self.color_button = OomoxColorButton(
                value,
                parent_window=self.parent_window,
                callback=self.on_color_set
            )
            linked_box.add(self.color_button)
            hbox.pack_start(linked_box, False, True, 0)
        else:
            self.color_entry = Gtk.Entry(text=value, width_chars=8)
            self.color_entry.connect("changed", self.on_color_input)
            hbox.pack_start(self.color_entry, False, True, 0)
            self.color_button = OomoxColorButton(
                value,
                parent_window=self.parent_window,
                callback=self.on_color_set
            )
            hbox.pack_start(self.color_button, False, True, 0)
            # ## ### #### ##### ###### #######


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

    def color_edited(self, key, value):
        self.theme[key] = value
        self.color_edited_callback(self.theme)

    def open_theme(self, theme):
        self.theme = theme
        self.listbox.foreach(lambda x: self.listbox.remove(x))
        if "NOGUI" in self.theme:
            row = Gtk.ListBoxRow()
            row.add(Gtk.Label("Can't be edited in GUI"))
            self.listbox.add(row)
        else:
            for theme_value in theme_model:
                if theme_value.get('filter'):
                    if not theme_value['filter'](theme):
                        continue
                key = theme_value.get('key')
                display_name = theme_value.get('display_name', key)
                row = None
                if theme_value['type'] == 'color':
                    row = ColorListBoxRow(
                        display_name, key, self.theme[key], self.color_edited,
                        parent=self.parent
                    )
                elif theme_value['type'] == 'bool':
                    row = BoolListBoxRow(
                        display_name, key, self.theme[key], self.color_edited
                    )
                elif theme_value['type'] == 'int':
                    row = IntListBoxRow(
                        display_name, key, self.theme[key], self.color_edited
                    )
                elif theme_value['type'] == 'float':
                    row = FloatListBoxRow(
                        display_name, key, self.theme[key], self.color_edited
                    )
                elif theme_value['type'] == 'options':
                    callback = None
                    if key == 'ICONS_STYLE':
                        def _callback(key, value):
                            self.color_edited(key, value)
                            self.open_theme(self.theme)
                        callback = _callback
                    else:
                        callback = self.color_edited
                    row = OptionsListBoxRow(
                        display_name, key, self.theme[key],
                        options=theme_value['options'],
                        callback=callback
                    )
                elif theme_value['type'] == 'separator':
                    row = SeparatorListBoxRow(display_name)
                if row:
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

        scrolled.add(self.listbox)

        theme_edit_label = Gtk.Label()
        theme_edit_label.set_text("Edit:")
        self.pack_start(theme_edit_label, False, False, 0)
        self.pack_start(scrolled, True, True, 0)
