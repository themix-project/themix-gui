from .helpers import convert_theme_color_to_gdk, THEME_KEYS
from gi.repository import Gtk


class ThemePreview(Gtk.Grid):

    BG = 'bg'
    FG = 'fg'

    def override_color(self, widget, value, color, state=Gtk.StateType.NORMAL):
        if value == self.BG:
            return widget.override_background_color(state, color)
        elif value == self.FG:
            return widget.override_color(state, color)

    def update_preview_colors(self, colorscheme):
        converted = {
            key: convert_theme_color_to_gdk(colorscheme[key])
            for key in THEME_KEYS
        }
        self.override_color(self.bg, self.BG, converted["BG"])
        self.override_color(self.label, self.FG, converted["FG"])
        self.override_color(self.sel_label, self.FG, converted["SEL_FG"])
        self.override_color(self.sel_label, self.BG, converted["SEL_BG"])
        self.override_color(self.entry, self.FG, converted["TXT_FG"])
        self.override_color(self.entry, self.BG, converted["TXT_BG"])
        self.override_color(self.entry, self.FG, converted["SEL_FG"],
                            state=Gtk.StateFlags.SELECTED)
        self.override_color(self.entry, self.BG, converted["SEL_BG"],
                            state=Gtk.StateFlags.SELECTED)
        self.override_color(self.button, self.FG, converted["BTN_FG"])
        self.override_color(self.button, self.BG, converted["BTN_BG"])
        self.override_color(self.menuitem1, self.FG, converted["MENU_FG"])
        self.override_color(self.menuitem2, self.FG, converted["MENU_FG"])
        self.override_color(self.menubar, self.BG, converted["MENU_BG"])

    def __init__(self):
        super().__init__(row_spacing=6, column_spacing=6)

        preview_label = Gtk.Label("Preview:")
        self.bg = Gtk.Grid(row_spacing=6, column_spacing=6)
        self.attach(preview_label, 1, 1, 3, 1)
        self.attach_next_to(self.bg, preview_label,
                            Gtk.PositionType.BOTTOM, 1, 1)

        self.menubar = Gtk.MenuBar()

        self.menuitem1 = Gtk.MenuItem(label='File')
        # menuitem.set_submenu(self.create_menu(3, True))
        self.menubar.append(self.menuitem1)

        self.menuitem2 = Gtk.MenuItem(label='Edit')
        # menuitem.set_submenu(self.create_menu(4, True))
        self.menubar.append(self.menuitem2)

        self.label = Gtk.Label("This is a label.")
        self.sel_label = Gtk.Label("Selected item.")
        self.entry = Gtk.Entry(text="Text entry.")

        self.button = Gtk.Button(label="Click-click")

        self.bg.attach(self.menubar, 1, 1, 3, 1)
        self.bg.attach(self.label, 2, 2, 1, 1)
        self.bg.attach_next_to(self.sel_label, self.label,
                               Gtk.PositionType.BOTTOM, 1, 1)
        self.bg.attach_next_to(self.entry, self.sel_label,
                               Gtk.PositionType.BOTTOM, 1, 1)
        self.bg.attach_next_to(self.button, self.entry,
                               Gtk.PositionType.BOTTOM, 1, 1)
        # hack to have margin inside children box instead of the parent one:
        self.bg.attach_next_to(Gtk.Label(), self.button,
                               Gtk.PositionType.BOTTOM, 1, 1)
