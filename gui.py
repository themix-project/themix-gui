#!/bin/env python3
import os
import random
import gi


gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk  # noqa


script_dir = os.path.dirname(os.path.realpath(__file__))
colors_dir = os.path.join(script_dir, "colors/")


def ls_r(path):
    return [
        os.path.join(files[0], file)
        for files in os.walk(path)
        for file in files[2]
    ]


def get_presets():
    result = {
        "".join(path.rsplit(colors_dir)): path
        for path in ls_r(colors_dir)
    }
    return result


def get_random_gdk_color():
    return Gdk.RGBA(random.random(), random.random(), random.random(), 1)


def hex_str_to_float(s):
    return int("0x{}".format(s), 16)/255


def convert_theme_color_to_gdk(theme_color):
    r = hex_str_to_float(theme_color[:2])
    g = hex_str_to_float(theme_color[2:4])
    b = hex_str_to_float(theme_color[4:])
    return Gdk.RGBA(r, g, b, 1)


def read_colorscheme_from_preset(preset_name):
    colorscheme = {}
    with open(os.path.join(colors_dir, preset_name)) as f:
        for line in f.readlines():
            parsed_line = line.strip().split('=')
            # migration workaround:
            if parsed_line[0] != "NAME":
                colorscheme[parsed_line[0]] = parsed_line[1]
    # migration workaround #2:
    for key, value in colorscheme.items():
        if value.startswith("$"):
            colorscheme[key] = colorscheme[value.lstrip("$")]
    return colorscheme


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
            key: convert_theme_color_to_gdk(value)
            for key, value in colorscheme.items()
        }
        self.override_color(self, self.BG, converted["BG"])
        self.override_color(self.label, self.FG, converted["FG"])
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

        self.menubar = Gtk.MenuBar()

        self.menuitem1 = Gtk.MenuItem(label='File')
        # menuitem.set_submenu(self.create_menu(3, True))
        self.menubar.append(self.menuitem1)

        self.menuitem2 = Gtk.MenuItem(label='Edit')
        # menuitem.set_submenu(self.create_menu(4, True))
        self.menubar.append(self.menuitem2)

        self.label = Gtk.Label()
        self.label.set_text("This is a label.")
        self.entry = Gtk.Entry()
        self.entry.set_text("Hello World")

        self.button = Gtk.Button(label="Click Here")

        self.attach(self.menubar, 1, 1, 3, 1)
        self.attach(self.label, 2, 2, 1, 1)
        self.attach_next_to(self.entry, self.label,
                            Gtk.PositionType.BOTTOM, 1, 1)
        self.attach_next_to(self.button, self.entry,
                            Gtk.PositionType.BOTTOM, 1, 1)
        # hack to have margin inside children box instead of the parent one:
        self.attach_next_to(Gtk.Label(), self.button,
                            Gtk.PositionType.BOTTOM, 1, 1)


class ThemePresetsList(Gtk.ScrolledWindow):

    def on_preset_select(self, widget):
        list_index = widget.get_cursor()[0].to_string()
        self.current_theme = list(
            self.liststore[list_index]
        )[0]
        self.preset_select_callback(self.current_theme)

    def __init__(self, preset_select_callback):
        super().__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.preset_select_callback = preset_select_callback
        self.presets = get_presets()

        self.liststore = Gtk.ListStore(str)
        for preset_name in self.presets:
            self.liststore.append((preset_name, ))

        treeview = Gtk.TreeView(model=self.liststore, headers_visible=False)
        treeview.connect("cursor_changed", self.on_preset_select)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn(cell_renderer=renderer_text, text=0)
        treeview.append_column(column_text)

        self.add(treeview)


class ThemeColorsList(Gtk.ScrolledWindow):

    theme = None

    def color_edited(self, widget, path, text):
        print((path, text))
        self.liststore[path][1] = text

    def open_theme(self, theme):
        self.liststore.clear()
        self.theme = theme
        for key, value in self.theme.items():
            self.liststore.append((key, value))

    def __init__(self):
        super().__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.liststore = Gtk.ListStore(str, str)

        treeview = Gtk.TreeView(model=self.liststore, headers_visible=False)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn(cell_renderer=renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property("editable", True)
        renderer_editabletext.connect("edited", self.color_edited)
        column_editabletext = Gtk.TreeViewColumn(
            "Editable Text", renderer_editabletext, text=1
        )
        treeview.append_column(column_editabletext)

        self.add(treeview)


class MainWindow(Gtk.Window):

    def _init_window(self):
        Gtk.Window.__init__(self, title="Oo-mox GUI")
        self.set_default_size(500, 300)
        self.set_border_width(6)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Oo-mox GUI"
        self.set_titlebar(hb)

        win_style_context = self.get_style_context()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path("./gui.css")
        screen = Gdk.Screen.get_default()
        win_style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.box)

    colorscheme = None
    theme_edit = None
    presets_list = None
    preview = None

    def __init__(self):
        self.colorscheme = {}

        self._init_window()

        def preset_select_callback(selected_preset):
            self.colorscheme = read_colorscheme_from_preset(selected_preset)
            self.theme_edit.open_theme(self.colorscheme)
            self.preview.update_preview_colors(self.colorscheme)

        self.presets_list = ThemePresetsList(
            preset_select_callback=preset_select_callback)
        presets_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        presets_list_label = Gtk.Label()
        presets_list_label.set_text("Presets:")
        presets_list_box.pack_start(presets_list_label, False, False, 0)
        presets_list_box.pack_start(self.presets_list, True, True, 0)
        self.box.pack_start(presets_list_box, True, True, 0)

        self.theme_edit = ThemeColorsList()
        # preset_select_callback=preset_select_callback)
        theme_edit_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        theme_edit_label = Gtk.Label()
        theme_edit_label.set_text("Edit:")
        theme_edit_box.pack_start(theme_edit_label, False, False, 0)
        theme_edit_box.pack_start(self.theme_edit, True, True, 0)
        self.box.pack_start(theme_edit_box, True, True, 0)

        self.preview = ThemePreview()
        preview_grid = Gtk.Grid()
        preview_label = Gtk.Label()
        preview_label.set_text("Preview:")
        preview_grid.attach(preview_label, 1, 1, 1, 1)
        preview_grid.attach_next_to(self.preview, preview_label,
                                    Gtk.PositionType.BOTTOM, 1, 1)
        self.box.pack_start(preview_grid, True, True, 0)


if __name__ == "__main__":
    win = MainWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()
