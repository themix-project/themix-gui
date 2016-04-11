from gi.repository import Gtk
from .helpers import get_presets


class ThemePresetsList(Gtk.Box):

    def on_preset_select(self, widget):
        list_index = widget.get_cursor()[0].to_string()
        self.current_theme = list(
            self.liststore[list_index]
        )[0]
        self.preset_select_callback(self.current_theme)

    def __init__(self, preset_select_callback):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.preset_select_callback = preset_select_callback
        self.presets = get_presets()

        self.liststore = Gtk.ListStore(str)
        for preset_name in self.presets:
            self.liststore.append((preset_name, ))
        self.liststore.set_sort_column_id(0, Gtk.SortType.ASCENDING)

        treeview = Gtk.TreeView(model=self.liststore, headers_visible=False)
        treeview.connect("cursor_changed", self.on_preset_select)

        column = Gtk.TreeViewColumn(cell_renderer=Gtk.CellRendererText(), text=0)
        treeview.append_column(column)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(treeview)

        presets_list_label = Gtk.Label()
        presets_list_label.set_text("Presets:")
        self.pack_start(presets_list_label, False, False, 0)
        self.pack_start(scrolled, True, True, 0)
