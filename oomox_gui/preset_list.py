import os
from collections import namedtuple

from gi.repository import Gtk, Gdk, GLib

from .i18n import _
from .config import USER_COLORS_DIR, COLORS_DIR
from .settings import UI_SETTINGS
from .plugin_api import PLUGIN_PATH_PREFIX
from .plugin_loader import IMPORT_PLUGINS
from .theme_file import get_presets


Section = namedtuple('Section', ['id', 'display_name'])


class Sections:
    PRESETS = Section('presets', _("Presets"))
    PLUGINS = Section('plugins', _("Plugins"))
    USER = Section('user', _("User Presets"))


_SECTION_RESERVED_NAME = '<section>'


class Keys:
    RIGHT_ARROW = 65363
    LEFT_ARROW = 65361
    KEY_F5 = 65474


class ThemePresetList(Gtk.ScrolledWindow):

    _update_signal = None
    treestore = None
    treeview = None
    preset_select_callback = None

    DISPLAY_NAME = 0
    THEME_NAME = 1
    THEME_PATH = 2
    IS_SAVEABLE = 3

    def __init__(self, preset_select_callback):
        super().__init__()
        self.set_size_request(width=UI_SETTINGS.preset_list_minimal_width, height=-1)

        self.preset_select_callback = preset_select_callback

        self.treestore = Gtk.TreeStore(str, str, str, bool)
        self.treeview = Gtk.TreeView(
            model=self.treestore, headers_visible=False
        )
        self.treeview.connect(
            "key-press-event", self._on_keypress
        )
        self.treeview.connect(
            "row-collapsed", self._on_row_collapsed
        )
        self.treeview.connect(
            "row-expanded", self._on_row_expanded
        )
        column = Gtk.TreeViewColumn(
            cell_renderer=Gtk.CellRendererText(), markup=0
        )
        self.treeview.append_column(column)
        self.load_presets()

        self.add(self.treeview)

        GLib.idle_add(
            self.focus_first_available,
            priority=GLib.PRIORITY_HIGH
        )

    ###########################################################################
    # Public interface:
    ###########################################################################

    def get_preset_path(self):
        return self._get_selected_value(self.THEME_PATH)

    def preset_is_saveable(self):
        return self._get_selected_value(self.IS_SAVEABLE)

    def focus_preset_by_filepath(self, filepath):
        treepath = self._find_treepath_by_filepath(
            self.treestore, filepath
        )
        if treepath:
            treepathcopy = treepath.copy()
            while treepath.up():
                self.treeview.expand_row(treepath, False)
            self.treeview.set_cursor(treepathcopy)

    def focus_first_available(self):
        init_iter = self.treestore.get_iter_first()
        while init_iter and not self.treeview.row_expanded(self.treestore.get_path(init_iter)):
            init_iter = self.treestore.iter_next(init_iter)
        init_iter = self.treestore.iter_children(init_iter)
        self.treeview.set_cursor(self.treestore.get_path(init_iter))

    def load_presets(self):
        if self._update_signal:
            self.treeview.disconnect(self._update_signal)

        self.treestore.clear()
        all_presets = get_presets()
        self._load_system_presets(all_presets)
        self._load_plugin_presets(all_presets)
        self._load_user_presets(all_presets)

        self._update_signal = self.treeview.connect(
            "cursor_changed", self._on_preset_select
        )

    def reload_presets(self):
        selected_path = self.get_preset_path()
        self.load_presets()
        self.focus_preset_by_filepath(selected_path)

    ###########################################################################
    # Private methods:
    ###########################################################################

    def _get_current_treepath(self):
        return self.treeview.get_cursor()[0]

    def _get_selected_value(self, value):
        treepath = self._get_current_treepath()
        if not treepath:
            return None
        treeiter = self.treestore.get_iter(treepath)
        return self.treestore.get_value(treeiter, value)

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

    def _add_preset(self, display_name, name, path, saveable, parent=None):  # pylint: disable=too-many-arguments
        return self.treestore.append(
            parent, (display_name, name, path, saveable)
        )

    def _add_section(self, section):
        return self.treestore.append(None, (
            '<b>{}</b>'.format(section.display_name), _SECTION_RESERVED_NAME, section.id, False
        ))

    @staticmethod
    def _format_dirname(preset, preset_dir, plugin=None):
        dir_template = '{}: {}'
        preset_relpath = (
            preset.name[len(preset_dir):]
            if plugin else preset.name
        )
        plugin_name = (plugin.display_name or plugin.name) if plugin else None
        dir_display_name, _slash, item_display_name = preset_relpath.lstrip('/').partition('/')
        if item_display_name:
            dir_display_name = dir_template.format(
                dir_display_name.replace('_', ' '), item_display_name
            )
        if plugin:
            dir_display_name = dir_template.format(plugin_name, dir_display_name)
        return dir_display_name

    @staticmethod
    def _format_childname(preset_relpath):
        dir_template = '{}: {}'
        dir_display_name, _slash, item_display_name = preset_relpath.lstrip('/').partition('/')
        if item_display_name:
            dir_display_name = dir_template.format(
                dir_display_name.replace('_', ' '), item_display_name
            )
        return dir_display_name

    def _add_presets(  # pylint: disable=too-many-arguments
            self, preset_dir, preset_list,
            plugin=None, parent=None
    ):
        sorted_preset_list = sorted(preset_list, key=lambda x: x.name)

        first_preset = sorted_preset_list[0]
        piter = self._add_preset(
            display_name=self._format_dirname(first_preset, preset_dir, plugin),
            name=first_preset.name,
            path=first_preset.path,
            saveable=first_preset.is_saveable,
            parent=parent
        )

        for preset in sorted_preset_list[1:]:
            display_name = self._format_childname((
                preset.name[len(preset_dir):]
                if preset_dir else preset.name
            ))
            self._add_preset(
                display_name=display_name,
                name=preset.name,
                path=preset.path,
                saveable=preset.is_saveable,
                parent=piter
            )

    def _load_system_presets(self, all_presets):
        presets_iter = self._add_section(Sections.PRESETS)
        for preset_dir, preset_list in sorted(all_presets.get(COLORS_DIR, {}).items()):
            if preset_dir.startswith(PLUGIN_PATH_PREFIX):
                continue
            self._add_presets(
                preset_dir=preset_dir, preset_list=preset_list,
                parent=presets_iter
            )
        if UI_SETTINGS.preset_list_sections_expanded.get(Sections.PRESETS.id, True):
            self.treeview.expand_row(self.treestore.get_path(presets_iter), False)

    def _load_plugin_presets(self, all_presets):
        plugins_iter = self._add_section(Sections.PLUGINS)
        for colors_dir, presets in all_presets.items():
            for preset_dir, preset_list in sorted(presets.items()):

                preset_plugin = None
                plugin_theme_dir = None
                for plugin in IMPORT_PLUGINS.values():
                    if plugin.plugin_theme_dir == colors_dir:
                        plugin_theme_dir = plugin.plugin_theme_dir
                    elif plugin.user_theme_dir and (
                            os.path.join(colors_dir, preset_dir).startswith(plugin.user_theme_dir)
                    ):
                        plugin_theme_dir = plugin.user_theme_dir
                    else:
                        continue
                    preset_plugin = plugin
                if not plugin_theme_dir:
                    continue

                self._add_presets(
                    preset_dir=preset_dir, preset_list=preset_list,
                    plugin=preset_plugin, parent=plugins_iter
                )
        if UI_SETTINGS.preset_list_sections_expanded.get(Sections.PLUGINS.id, True):
            self.treeview.expand_row(self.treestore.get_path(plugins_iter), False)

    def _load_user_presets(self, all_presets):
        user_presets_iter = self._add_section(Sections.USER)
        for preset_dir, preset_list in sorted(all_presets.get(USER_COLORS_DIR, {}).items()):
            if preset_dir.startswith(PLUGIN_PATH_PREFIX):
                continue
            self._add_presets(
                preset_dir=preset_dir, preset_list=preset_list,
                parent=user_presets_iter
            )
        if UI_SETTINGS.preset_list_sections_expanded.get(Sections.USER.id, True):
            self.treeview.expand_row(self.treestore.get_path(user_presets_iter), False)

    ###########################################################################
    # Signal handlers:
    ###########################################################################

    def _on_preset_select(self, _widget):
        treepath = self._get_current_treepath()
        if not treepath:
            return
        treeiter = self.treestore.get_iter(treepath)
        current_theme = self.treestore.get_value(treeiter, self.THEME_NAME)
        if current_theme == _SECTION_RESERVED_NAME:
            return
        current_preset_path = self.treestore.get_value(treeiter, self.THEME_PATH)
        self.preset_select_callback(
            current_theme, current_preset_path
        )

    def _on_keypress(self, _widget, event):
        key = event.keyval
        if event.type != Gdk.EventType.KEY_PRESS:
            return
        if key == Keys.KEY_F5:
            self.reload_presets()
        elif key in (Keys.LEFT_ARROW, Keys.RIGHT_ARROW):
            treepath = self._get_current_treepath()
            if not treepath:
                return
            if key == Keys.RIGHT_ARROW:
                self.treeview.expand_row(treepath, False)
            elif key == Keys.LEFT_ARROW:
                self.treeview.collapse_row(treepath)

    def _on_row_expanded(self, _treeview, treeiter, _treepath):
        if self.treestore.get_value(treeiter, self.THEME_NAME) == _SECTION_RESERVED_NAME:
            section_id = self.treestore.get_value(treeiter, self.THEME_PATH)
            UI_SETTINGS.preset_list_sections_expanded[section_id] = True

    def _on_row_collapsed(self, _treeview, treeiter, _treepath):
        if self.treestore.get_value(treeiter, self.THEME_NAME) == _SECTION_RESERVED_NAME:
            section_id = self.treestore.get_value(treeiter, self.THEME_PATH)
            UI_SETTINGS.preset_list_sections_expanded[section_id] = False
