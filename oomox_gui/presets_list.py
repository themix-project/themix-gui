import os

from gi.repository import Gtk, Gdk, Pango

from .i18n import _
from .theme_file import get_presets
from .plugin_api import PLUGIN_PATH_PREFIX
from .plugin_loader import IMPORT_PLUGINS
from .config import USER_COLORS_DIR, COLORS_DIR


class Keys:
    RIGHT_ARROW = 65363
    LEFT_ARROW = 65361
    KEY_F5 = 65474


class Settings:
    presets_list_system_expanded = True
    presets_list_plugins_expanded = True
    presets_list_user_expanded = True


SETTINGS = Settings()
PRESET_LIST_MIN_SIZE = 250

_SECTION_RESERVED_NAME = '<section>'


class ThemePresetsList(Gtk.ScrolledWindow):

    update_signal = None
    treestore = None
    treeview = None
    preset_select_callback = None

    DISPLAY_NAME = 0
    THEME_NAME = 1
    THEME_PATH = 2
    IS_SAVEABLE = 3

    def get_current_treepath(self):
        return self.treeview.get_cursor()[0]

    def get_selected_value(self, value):
        treepath = self.get_current_treepath()
        if not treepath:
            return None
        treeiter = self.treestore.get_iter(treepath)
        return self.treestore.get_value(treeiter, value)

    def get_colorscheme_path(self):
        return self.get_selected_value(self.THEME_PATH)

    def preset_is_saveable(self):
        return self.get_selected_value(self.IS_SAVEABLE)

    def on_preset_select(self, _widget):
        treepath = self.get_current_treepath()
        if not treepath:
            return
        treeiter = self.treestore.get_iter(treepath)
        current_theme = self.treestore.get_value(treeiter, self.THEME_NAME)
        if current_theme == _SECTION_RESERVED_NAME:
            if self.treestore.iter_has_child(treeiter):
                treeiter = self.treestore.iter_children(treeiter)
            else:
                treeiter = self.treestore.iter_next(treeiter)
            self.treeview.set_cursor(self.treestore.get_path(treeiter))
            return
        current_preset_path = self.treestore.get_value(treeiter, self.THEME_PATH)
        self.preset_select_callback(
            current_theme, current_preset_path
        )

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

    def _add_preset(self, display_name, name, path, saveable, parent=None):  # pylint: disable=too-many-arguments
        return self.treestore.append(
            parent, (display_name, name, path, saveable, Pango.Weight.NORMAL)
        )

    def _add_section(self, name):
        return self.treestore.append(
            None, (name, _SECTION_RESERVED_NAME, "", False, Pango.Weight.BOLD)
        )

    def _add_presets(  # pylint: disable=too-many-arguments
            self, colors_dir, preset_dir, preset_list,
            plugin_name=None, parent=None
    ):
        sorted_preset_list = sorted(preset_list, key=lambda x: x['name'])

        first_preset = sorted_preset_list[0]
        dir_template = "{}: {{}}".format(plugin_name) \
            if plugin_name else "{}"
        dir_display_name = dir_template.format(
            first_preset['path'][len(colors_dir):].lstrip('/')
        )
        piter = self._add_preset(
            display_name=dir_display_name,
            name=first_preset['name'],
            path=first_preset['path'],
            saveable=first_preset['is_saveable'],
            parent=parent
        )

        for preset in sorted_preset_list[1:]:
            display_name = (
                preset['name'][len(preset_dir):]
                if preset_dir else preset['name']
            ).lstrip('/')
            self._add_preset(
                display_name=display_name,
                name=preset['name'],
                path=preset['path'],
                saveable=preset['is_saveable'],
                parent=piter
            )

    def _load_system_presets(self, all_presets):
        presets_iter = self._add_section(_("Presets"))
        for preset_dir, preset_list in sorted(all_presets.get(COLORS_DIR, {}).items()):
            if preset_dir.startswith(PLUGIN_PATH_PREFIX):
                continue
            self._add_presets(
                colors_dir=COLORS_DIR, preset_dir=preset_dir, preset_list=preset_list,
                parent=presets_iter
            )
        if SETTINGS.presets_list_system_expanded:
            self.treeview.expand_row(self.treestore.get_path(presets_iter), False)

    def _load_plugin_presets(self, all_presets):
        plugins_iter = self._add_section(_("Plugins"))
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
                    plugin_name=plugin_display_name, parent=plugins_iter
                )
        if SETTINGS.presets_list_plugins_expanded:
            self.treeview.expand_row(self.treestore.get_path(plugins_iter), False)

    def _load_user_presets(self, all_presets):
        user_presets_iter = self._add_section(_("User Presets"))
        for preset_dir, preset_list in sorted(all_presets.get(USER_COLORS_DIR, {}).items()):
            if preset_dir.startswith(PLUGIN_PATH_PREFIX):
                continue
            self._add_presets(
                colors_dir=USER_COLORS_DIR, preset_dir=preset_dir, preset_list=preset_list,
                parent=user_presets_iter
            )
        if SETTINGS.presets_list_user_expanded:
            self.treeview.expand_row(self.treestore.get_path(user_presets_iter), False)

    def load_presets(self):
        if self.update_signal:
            self.treeview.disconnect(self.update_signal)
        self.treestore.clear()
        all_presets = get_presets()

        self._load_system_presets(all_presets)
        self._load_plugin_presets(all_presets)
        self._load_user_presets(all_presets)

        self.update_signal = self.treeview.connect(
            "cursor_changed", self.on_preset_select
        )

    def reload_presets(self):
        selected_path = self.get_colorscheme_path()
        self.load_presets()
        self.focus_preset_by_filepath(selected_path)

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
        self.set_size_request(width=PRESET_LIST_MIN_SIZE, height=-1)

        self.preset_select_callback = preset_select_callback

        self.treestore = Gtk.TreeStore(str, str, str, bool, int)
        self.treeview = Gtk.TreeView(
            model=self.treestore, headers_visible=False
        )
        self.treeview.connect(
            "key-press-event", self._on_keypress
        )
        column = Gtk.TreeViewColumn(
            cell_renderer=Gtk.CellRendererText(), text=0, sensitive=3, weight=4
        )
        self.treeview.append_column(column)
        self.load_presets()

        self.add(self.treeview)
