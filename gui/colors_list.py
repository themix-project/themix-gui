from gi.repository import Gtk
from .helpers import (
    convert_theme_color_to_gdk, THEME_KEYS, convert_gdk_to_theme_color
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

        adjustment = Gtk.Adjustment(value, 0.0, 4.0, 0.02, 10.0, 0)
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


class ColorListBoxRow(Gtk.ListBoxRow):

    def on_color_input(self, widget):
        self.value = widget.get_text()
        self.color_button.set_rgba(convert_theme_color_to_gdk(self.value))
        self.color_set_callback(self.key, self.value)

    def on_color_set(self, widget):
        self.value = convert_gdk_to_theme_color(widget.get_rgba())
        self.color_entry.set_text(self.value)
        self.color_set_callback(self.key, self.value)

    def __init__(self, display_name, key, value, color_set_callback):
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
            self.color_button = Gtk.ColorButton.new_with_rgba(
                convert_theme_color_to_gdk(value)
            )
            linked_box.add(self.color_button)
            self.color_button.connect("color-set", self.on_color_set)
            hbox.pack_start(linked_box, False, True, 0)
        else:
            self.color_entry = Gtk.Entry(text=value, width_chars=7)
            self.color_entry.connect("changed", self.on_color_input)
            hbox.pack_start(self.color_entry, False, True, 0)

            self.color_button = Gtk.ColorButton.new_with_rgba(
                convert_theme_color_to_gdk(value)
            )
            self.color_button.connect("color-set", self.on_color_set)
            hbox.pack_start(self.color_button, False, True, 0)


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
            for key_obj in THEME_KEYS:
                key = key_obj.get('key')
                display_name = key_obj.get('display_name', key)
                row = None
                if key_obj['type'] == 'color':
                    row = ColorListBoxRow(
                        display_name, key, self.theme[key], self.color_edited
                    )
                elif key_obj['type'] == 'bool':
                    row = BoolListBoxRow(
                        display_name, key, self.theme[key], self.color_edited
                    )
                elif key_obj['type'] == 'int':
                    row = IntListBoxRow(
                        display_name, key, self.theme[key], self.color_edited
                    )
                elif key_obj['type'] == 'float':
                    row = FloatListBoxRow(
                        display_name, key, self.theme[key], self.color_edited
                    )
                elif key_obj['type'] == 'separator':
                    row = SeparatorListBoxRow(display_name)
                if row:
                    self.listbox.add(row)
        self.listbox.show_all()

    def __init__(self, color_edited_callback):
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
