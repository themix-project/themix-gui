from gi.repository import Gtk
from .helpers import get_presets


class ThemePresetsList(Gtk.Box):

    presets = None
    current_theme = None
    current_preset_path = None

    update_signal = None
    liststore = None
    treeiter = None
    preset_select_callback = None

    DISPLAY_NAME = 0
    THEME_NAME = 1
    THEME_PATH = 2

    def on_preset_select(self, widget):
        treepath = widget.get_cursor()[0]
        if not treepath:
            return
        list_index = treepath.to_string()
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

    def _find_treepath_by_filepath(
        self, store, target_filepath, treeiter=None
    ):
        if not treeiter:
            treeiter = self.treestore.get_iter_first()
        while treeiter:
            current_filepath = store[treeiter][self.THEME_PATH]
            if current_filepath == target_filepath:
                return store[treeiter].path
            if store.iter_has_child(treeiter):
                childiter = store.iter_children(treeiter)
                child_result = self._find_treepath_by_filepath(
                    store, target_filepath, childiter
                )
                if child_result:
                    return child_result
            treeiter = store.iter_next(treeiter)

    def focus_preset_by_filepath(self, filepath):
        treepath = self._find_treepath_by_filepath(
            self.treestore, filepath
        )
        if treepath:
            treepathcopy = treepath.copy()
            while treepath.up():
                self.treeview.expand_row(treepath, False)
            self.treeview.set_cursor(treepathcopy)

    def load_presets(self):
        if self.update_signal:
            self.treeview.disconnect(self.update_signal)
        self.treestore.clear()
        self.presets = get_presets()
        for preset_dir, preset_list in self.presets.items():
            sorted_preset_list = sorted(preset_list, key=lambda x: x['name'])
            piter = self.treestore.append(
                None,
                (preset_dir,
                 sorted_preset_list[0]['name'],
                 sorted_preset_list[0]['path'])
            )
            for preset in sorted_preset_list[1:]:
                self.treestore.append(
                    piter,
                    (preset['name'], preset['name'], preset['path'])
                )
        self.update_signal = self.treeview.connect(
            "cursor_changed", self.on_preset_select
        )

    def __init__(self, preset_select_callback):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.preset_select_callback = preset_select_callback

        self.treestore = Gtk.TreeStore(str, str, str)
        self.treestore.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.treeview = Gtk.TreeView(model=self.treestore, headers_visible=False)
        self.column = Gtk.TreeViewColumn(
            cell_renderer=Gtk.CellRendererText(), text=0
        )
        self.treeview.append_column(self.column)
        self.load_presets()

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.treeview)

        presets_list_label = Gtk.Label()
        presets_list_label.set_text("Presets:")
        self.pack_start(presets_list_label, False, False, 0)
        self.pack_start(scrolled, True, True, 0)
