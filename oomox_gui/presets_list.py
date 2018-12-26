import os

from gi.repository import Gtk, Gdk

from .theme_file import (
    is_user_colorscheme, get_presets
)
from .plugin_api import PLUGIN_PATH_PREFIX
from .plugin_loader import IMPORT_PLUGINS
from .config import USER_COLORS_DIR, COLORS_DIR


class Keys:
    RIGHT_ARROW = 65363
    LEFT_ARROW = 65361
    KEY_F5 = 65474


class ThemePresetsList(Gtk.ScrolledWindow):

    colorscheme_path = None

    update_signal = None
    treestore = None
    treeview = None
    preset_select_callback = None

    DISPLAY_NAME = 0
    THEME_NAME = 1
    THEME_PATH = 2

    def on_preset_select(self, widget):
        treepath = widget.get_cursor()[0]
        if not treepath:
            return
        treeiter = self.treestore.get_iter(treepath)
        current_theme = self.treestore.get_value(treeiter, self.THEME_NAME)
        current_preset_path = self.treestore.get_value(treeiter, self.THEME_PATH)
        self.preset_select_callback(
            current_theme, current_preset_path
        )
        self.colorscheme_path = current_preset_path

    def add_preset(self, preset_name, preset_path, display_name=None):
        if not display_name:
            display_name = preset_name
        self.treestore.append(None, (
            display_name, preset_name, preset_path, is_user_colorscheme(preset_path)
        ))

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
        return None

    def focus_preset_by_filepath(self, filepath):
        treepath = self._find_treepath_by_filepath(
            self.treestore, filepath
        )
        if treepath:
            treepathcopy = treepath.copy()
            while treepath.up():
                self.treeview.expand_row(treepath, False)
            self.treeview.set_cursor(treepathcopy)

    def _add_presets(self, colors_dir, preset_dir, preset_list, plugin_name=None):
        sorted_preset_list = sorted(preset_list, key=lambda x: x['name'])

        first_preset = sorted_preset_list[0]
        is_user_theme = not first_preset['default']
        dir_template = "(Plugin) {}: {{}}".format(plugin_name) \
            if plugin_name else "{}"
        dir_display_name = dir_template.format(
            first_preset['path'][len(colors_dir):].lstrip('/')
        )
        piter = self.treestore.append(
            None, (
                dir_display_name,
                first_preset['name'],
                first_preset['path'],
                is_user_theme
            )
        )

        for preset in sorted_preset_list[1:]:
            display_name = (
                preset['name'][len(preset_dir):]
                if preset_dir else preset['name']
            ).lstrip('/')
            self.treestore.append(
                piter, (
                    display_name,
                    preset['name'],
                    preset['path'],
                    is_user_theme
                )
            )

    def load_presets(self):
        if self.update_signal:
            self.treeview.disconnect(self.update_signal)
        self.treestore.clear()
        all_presets = get_presets()

        for preset_dir, preset_list in sorted(all_presets.get(COLORS_DIR, {}).items()):
            if preset_dir.startswith(PLUGIN_PATH_PREFIX):
                continue
            self._add_presets(
                colors_dir=COLORS_DIR, preset_dir=preset_dir, preset_list=preset_list
            )

        for colors_dir, presets in all_presets.items():
            for preset_dir, preset_list in sorted(presets.items()):

                plugin_theme_dir = None
                plugin_display_name = None
                for plugin in IMPORT_PLUGINS.values():
                    if plugin.plugin_theme_dir == colors_dir:
                        plugin_theme_dir = plugin.plugin_theme_dir
                    elif plugin.user_theme_dir and (
                            os.path.join(colors_dir, preset_dir).startswith(plugin.user_theme_dir)
                    ):
                        plugin_theme_dir = plugin.user_theme_dir
                    else:
                        continue
                    plugin_display_name = plugin.display_name or plugin.name
                if not plugin_theme_dir:
                    continue

                self._add_presets(
                    colors_dir=plugin_theme_dir, preset_dir=preset_dir, preset_list=preset_list,
                    plugin_name=plugin_display_name
                )

        for preset_dir, preset_list in sorted(all_presets.get(USER_COLORS_DIR, {}).items()):
            if preset_dir.startswith(PLUGIN_PATH_PREFIX):
                continue
            self._add_presets(
                colors_dir=USER_COLORS_DIR, preset_dir=preset_dir, preset_list=preset_list
            )

        self.update_signal = self.treeview.connect(
            "cursor_changed", self.on_preset_select
        )

    def reload_presets(self):
        self.load_presets()
        self.focus_preset_by_filepath(self.colorscheme_path)

    def get_current_treepath(self):
        return self._find_treepath_by_filepath(
            self.treestore, self.colorscheme_path
        )

    def _on_keypress(self, _widget, event):
        key = event.keyval
        if event.type != Gdk.EventType.KEY_PRESS:
            return
        if key == Keys.KEY_F5:
            self.reload_presets()
        elif key in (Keys.LEFT_ARROW, Keys.RIGHT_ARROW):
            treepath = self.get_current_treepath()
            if not treepath:
                return
            if key == Keys.RIGHT_ARROW:
                self.treeview.expand_row(treepath, False)
            elif key == Keys.LEFT_ARROW:
                self.treeview.collapse_row(treepath)

    def __init__(self, preset_select_callback):
        super().__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.preset_select_callback = preset_select_callback

        self.treestore = Gtk.TreeStore(str, str, str, bool)
        self.treeview = Gtk.TreeView(
            model=self.treestore, headers_visible=False
        )
        self.treeview.connect(
            "key-press-event", self._on_keypress
        )
        column = Gtk.TreeViewColumn(
            cell_renderer=Gtk.CellRendererText(), text=0, sensitive=3
        )
        self.treeview.append_column(column)
        self.load_presets()

        self.add(self.treeview)
