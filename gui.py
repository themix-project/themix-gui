import random
import gi


gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk  # noqa


def get_presets():
    result = {"foo": "bar", "baz,": "span"}
    return result


def get_random_gdk_color():
    return Gdk.RGBA(random.random(), random.random(), random.random(), 1)


class ThemePreview(Gtk.Grid):

    BG = 'bg'
    FG = 'fg'

    def override_color(self, widget, value, color, state=Gtk.StateType.NORMAL):
        if value == self.BG:
            return widget.override_background_color(state, color)
        elif value == self.FG:
            return widget.override_color(state, color)

    def update_preview_colors(self):
        bg = get_random_gdk_color()
        fg = get_random_gdk_color()
        txt_bg = get_random_gdk_color()
        txt_fg = get_random_gdk_color()
        sel_bg = get_random_gdk_color()
        sel_fg = get_random_gdk_color()
        btn_bg = get_random_gdk_color()
        btn_fg = get_random_gdk_color()
        menu_bg = get_random_gdk_color()
        menu_fg = get_random_gdk_color()

        self.override_color(self, self.BG, bg)
        self.override_color(self.label, self.FG, fg)
        self.override_color(self.entry, self.FG, txt_fg)
        self.override_color(self.entry, self.BG, txt_bg)
        self.override_color(self.entry, self.FG, sel_fg,
                            state=Gtk.StateFlags.SELECTED)
        self.override_color(self.entry, self.BG, sel_bg,
                            state=Gtk.StateFlags.SELECTED)
        self.override_color(self.button, self.FG, btn_fg)
        self.override_color(self.button, self.BG, btn_bg)
        self.override_color(self.menubar, self.FG, menu_fg)
        self.override_color(self.menubar, self.BG, menu_bg)

    def __init__(self):
        super().__init__(row_spacing=6, column_spacing=6)

        self.menubar = Gtk.MenuBar()

        menuitem = Gtk.MenuItem(label='File')
        # menuitem.set_submenu(self.create_menu(3, True))
        self.menubar.append(menuitem)

        menuitem = Gtk.MenuItem(label='Edit')
        # menuitem.set_submenu(self.create_menu(4, True))
        self.menubar.append(menuitem)

        self.label = Gtk.Label()
        self.label.set_text("This is a label.")
        self.entry = Gtk.Entry()
        self.entry.set_text("Hello World")

        self.button = Gtk.Button(label="Click Here")

        def clicked(_):
            return self.update_preview_colors()
        self.button.connect("clicked", clicked)

        self.attach(self.menubar, 1, 1, 3, 1)
        self.attach(self.label, 2, 2, 1, 1)
        self.attach_next_to(self.entry, self.label,
                            Gtk.PositionType.BOTTOM, 1, 1)
        self.attach_next_to(self.button, self.entry,
                            Gtk.PositionType.BOTTOM, 1, 1)


class ThemePresetsList(Gtk.ScrolledWindow):

    def on_preset_select(self, widget):
        self.list_index = widget.get_cursor()[0].to_string()
        print(self.list_index)
        print(list(
            self.liststore[self.list_index]
        ))

    def text_edited(self, widget, path, text):
        self.liststore[path][1] = text

    def __init__(self):
        super().__init__()
        self.presets = get_presets()

        self.liststore = Gtk.ListStore(str, str)
        for preset_name in self.presets:
            self.liststore.append([preset_name, "http://fedoraproject.org/"])
        treeview = Gtk.TreeView(model=self.liststore)
        treeview.connect("cursor_changed", self.on_preset_select)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Text", renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property("editable", True)
        renderer_editabletext.connect("edited", self.text_edited)
        column_editabletext = Gtk.TreeViewColumn(
            "Editable Text", renderer_editabletext, text=1
        )
        treeview.append_column(column_editabletext)

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
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

    def __init__(self):
        self._init_window()

        self.presets_list = ThemePresetsList()
        presets_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        presets_list_label = Gtk.Label()
        presets_list_label.set_text("Presets:")
        presets_list_box.pack_start(presets_list_label, False, False, 0)
        presets_list_box.pack_start(self.presets_list, True, True, 0)
        self.box.pack_start(presets_list_box, True, True, 0)

        self.theme_edit = ThemePresetsList()
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
