from gi.repository import Gtk
from .helpers import convert_theme_color_to_gdk


class ColorListBoxRow(Gtk.ListBoxRow):

    def on_color_set(self, widget):
        c = widget.get_rgba()
        self.value = "".join([
            str(hex(int(n*255))).lstrip("0x")
            for n in (c.red, c.green, c.blue)
        ])
        self.color_set_callback(self.key, self.value)

    def __init__(self, key, value, color_set_callback):
        super(Gtk.ListBoxRow, self).__init__()

        self.color_set_callback = color_set_callback
        self.key = key
        self.value = value

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.add(hbox)
        label = Gtk.Label(key, xalign=0)
        hbox.pack_start(label, True, True, 0)

        color_button = Gtk.ColorButton.new_with_rgba(
            convert_theme_color_to_gdk(value)
        )
        color_button.connect("color-set", self.on_color_set)
        hbox.pack_start(color_button, False, True, 0)


class ThemeColorsList(Gtk.ScrolledWindow):

    theme = None

    def color_edited(self, key, value):
        self.theme[key] = value
        self.color_edited_callback(self.theme)

    def open_theme(self, theme):
        self.theme = theme
        self.listbox.foreach(lambda x: self.listbox.remove(x))
        for key, value in self.theme.items():
            row = ColorListBoxRow(key, value, self.color_edited)
            self.listbox.add(row)
        self.listbox.show_all()

    def __init__(self, color_edited_callback):
        super().__init__()
        self.color_edited_callback = color_edited_callback
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)

        def sort_func(row_1, row_2, data, notify_destroy):
            return row_1.key.lower() > row_2.key.lower()

        self.listbox.set_sort_func(sort_func, None, False)
        self.add(self.listbox)
