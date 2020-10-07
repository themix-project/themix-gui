import os
from collections import namedtuple

from gi.repository import Gtk, Gdk, GLib

from .i18n import _
from .config import USER_COLORS_DIR, COLORS_DIR
from .settings import UI_SETTINGS
from .plugin_api import PLUGIN_PATH_PREFIX
from .plugin_loader import IMPORT_PLUGINS
from .theme_file import get_presets, group_presets_by_dir


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
            cell_renderer=Gtk.CellRendererText(), markup=self.DISPLAY_NAME
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
            self._focus_preset_by_treepath(treepath)
            return True
        return False

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

    def reload_presets(self, focus_on_theme=None):
        old_treepath = self._get_current_treepath()
        focus_on_theme = focus_on_theme or self.get_preset_path()
        self.load_presets()
        if not self.focus_preset_by_filepath(focus_on_theme):
            self._focus_preset_by_treepath(old_treepath)

    ###########################################################################
    # Private methods:
    ###########################################################################

    def _focus_preset_by_treepath(self, treepath):
        path_found = False
        while not path_found:
            try:
                self.treestore.get_iter(treepath)
                path_found = True
            except ValueError:
                treepath.prev()
        self.treeview.expand_to_path(treepath)
        self.treeview.set_cursor(treepath)

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

    def _add_directory(self, name, tree_id=None, parent=None, template='{}'):
        tree_id = tree_id or name
        return self.treestore.append(parent, (
            template.format(name), _SECTION_RESERVED_NAME, tree_id, False
        ))

    def _add_section(self, section, parent=None):
        return self._add_directory(
            template='<b>{}</b>', name=section.display_name,
            parent=parent, tree_id=section.id,
        )

    @staticmethod
    def _format_dirname(preset, dirname, plugin_name=None, parent_dir=None):
        dir_template = '{}: {}'
        if parent_dir:
            preset_relpath = preset.path[len('/'.join(parent_dir.split('/')[:-1])):]
        else:
            preset_relpath = (
                preset.name[len(dirname):]
                if plugin_name else preset.name
            )
        dir_display_name, _slash, item_display_name = preset_relpath.lstrip('/').partition('/')
        if item_display_name:
            dir_display_name = dir_template.format(
                dir_display_name.replace('_', ' '), item_display_name
            )
        if plugin_name:
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
            self, dirname, preset_list,
            plugin_name=None, parent=None, subdir_path=None
    ):
        sorted_preset_list = sorted(preset_list, key=lambda x: x.name.lower())

        first_preset = sorted_preset_list[0]
        piter = self._add_preset(
            display_name=self._format_dirname(
                first_preset, dirname,
                plugin_name=plugin_name,
                parent_dir=subdir_path,
            ),
            name=first_preset.name,
            path=first_preset.path,
            saveable=first_preset.is_saveable,
            parent=parent
        )

        last_subdir = None
        last_subdir_iter = None
        for preset in sorted_preset_list[1:]:
            if len(preset.name.split('/')) > 2:
                preset_subdir = os.path.dirname(preset.path)
                if preset_subdir != last_subdir:
                    last_subdir = preset_subdir
                    last_subdir_iter = self._add_preset(
                        display_name=self._format_dirname(
                            preset, dirname,
                            plugin_name=plugin_name,
                            parent_dir=last_subdir,
                        ),
                        name=preset.name,
                        path=preset.path,
                        saveable=preset.is_saveable,
                        parent=piter
                    )
                else:
                    self._add_presets(
                        dirname=dirname, preset_list=[preset],
                        parent=last_subdir_iter,
                        subdir_path=last_subdir
                    )
            else:
                display_name = self._format_childname((
                    preset.name[len(dirname):]
                    if dirname else preset.name
                ))
                self._add_preset(
                    display_name=display_name,
                    name=preset.name,
                    path=preset.path,
                    saveable=preset.is_saveable,
                    parent=piter
                )

    def _load_system_presets(self, all_presets):
        featured_dirs = ('Featured', )
        presets_iter = self._add_section(Sections.PRESETS)
        sorted_system_presets = sorted(
            all_presets.get(COLORS_DIR, {}).items(),
            key=lambda x: (x[0] not in featured_dirs, x[0].lower())
        )
        for preset_dir, preset_list in sorted_system_presets:
            if preset_dir.startswith(PLUGIN_PATH_PREFIX):
                continue
            self._add_presets(
                dirname=preset_dir, preset_list=preset_list,
                parent=presets_iter
            )
        if UI_SETTINGS.preset_list_sections_expanded.get(Sections.PRESETS.id, True):
            self.treeview.expand_row(self.treestore.get_path(presets_iter), False)

    def _load_plugin_presets(self, all_presets):  # pylint: disable=too-many-locals
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
                plugin_name = preset_plugin.display_name or preset_plugin.name
                if plugin_theme_dir == preset_plugin.user_theme_dir:
                    plugin_name = preset_plugin.user_presets_display_name or plugin_name

                grouped_presets = group_presets_by_dir(
                    preset_list, os.path.join(colors_dir, preset_dir)
                )
                if len(grouped_presets) == 1 and grouped_presets[0][0] == '':
                    grouped_presets = [
                        (preset.name, [preset, ])
                        for preset in grouped_presets[0][1]
                    ]

                plugin_presets_iter = self._add_directory(
                    name=plugin_name,
                    parent=plugins_iter
                )
                for dir_name, group in grouped_presets:
                    self._add_presets(
                        dirname=dir_name,
                        preset_list=group,
                        parent=plugin_presets_iter
                    )

        if UI_SETTINGS.preset_list_sections_expanded.get(Sections.PLUGINS.id, True):
            self.treeview.expand_row(self.treestore.get_path(plugins_iter), False)

    def _load_user_presets(self, all_presets):
        user_presets_iter = self._add_section(Sections.USER)
        for preset_dir, preset_list in sorted(all_presets.get(USER_COLORS_DIR, {}).items()):
            if preset_dir.startswith(PLUGIN_PATH_PREFIX):
                continue
            self._add_presets(
                dirname=preset_dir, preset_list=preset_list,
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
