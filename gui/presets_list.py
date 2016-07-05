from gi.repository import Gtk
from .helpers import get_presets


class ThemePresetsList(Gtk.Box):

    presets = None
    current_theme = None
    current_preset_path = None

    liststore = None
    treeiter = None
    preset_select_callback = None

    DISPLAY_NAME = 0
    THEME_NAME = 1
    THEME_PATH = 2

    def on_preset_select(self, widget):
        list_index = widget.get_cursor()[0].to_string()
        selected_preset = list(
            self.treestore[list_index]
        )
        self.current_theme = selected_preset[self.THEME_NAME]
        self.current_preset_path = selected_preset[self.THEME_PATH]
        self.preset_select_callback(
            self.current_theme, self.current_preset_path
        )
        self.treeiter = self.treestore.get_iter(
            Gtk.TreePath.new_from_string(list_index)
        )

    def add_preset(self, preset_name, preset_path, display_name=None):
        if not display_name:
            display_name = preset_name
        self.treestore.append(None, (display_name, preset_name, preset_path))

    def focus_previous(self):
        treepath = self.treeview.get_cursor()[0]
        treepath.prev()
        self.treeview.set_cursor(treepath)

    def update_current_preset_display_name(self, new_name):
        self.treestore[self.treeiter][self.DISPLAY_NAME] = new_name

    def update_current_preset_name(self, new_name):
        self.treestore[self.treeiter][self.THEME_NAME] = new_name

    def update_current_preset_path(self, new_path):
        self.treestore[self.treeiter][self.THEME_PATH] = new_path

    def __init__(self, preset_select_callback):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.preset_select_callback = preset_select_callback
        self.presets = get_presets()

        self.treestore = Gtk.TreeStore(str, str, str)
        for preset_dir, preset_list in self.presets.items():
            sorted_preset_list = sorted(preset_list, key=lambda x: x['name'])
            piter = self.treestore.append(
                None,
                (preset_dir, sorted_preset_list[0]['name'], sorted_preset_list[0]['path'])
            )
            for preset in sorted_preset_list[1:]:
                self.treestore.append(
                    piter,
                    (preset['name'], preset['name'], preset['path'])
                )
        self.treestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)

        self.treeview = Gtk.TreeView(model=self.treestore, headers_visible=False)
        self.treeview.connect("cursor_changed", self.on_preset_select)

        column = Gtk.TreeViewColumn(
            cell_renderer=Gtk.CellRendererText(), text=0
        )
        self.treeview.append_column(column)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.treeview)

        presets_list_label = Gtk.Label()
        presets_list_label.set_text("Presets:")
        self.pack_start(presets_list_label, False, False, 0)
        self.pack_start(scrolled, True, True, 0)
