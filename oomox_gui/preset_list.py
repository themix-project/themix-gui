import os
from typing import TYPE_CHECKING, NamedTuple, overload

from gi.repository import Gdk, GLib, Gtk

from .config import COLORS_DIR, USER_COLORS_DIR
from .gtk_helpers import warn_once
from .i18n import translate
from .plugin_api import PLUGIN_PATH_PREFIX
from .plugin_loader import PluginLoader
from .settings import UISettings
from .theme_file import get_presets, group_presets_by_dir

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, Final, Literal

    from .theme_file import PresetFile


class Section(NamedTuple):
    name: str
    display_name: str


class Sections:
    PRESETS = Section("presets", translate("Presets"))
    PLUGINS = Section("plugins", translate("Plugins"))
    USER = Section("user", translate("User Presets"))


_SECTION_RESERVED_NAME: "Final" = "<section>"


class Keys:
    RIGHT_ARROW: "Final" = 65363
    LEFT_ARROW: "Final" = 65361
    KEY_F5: "Final" = 65474


class ThemePresetList(Gtk.ScrolledWindow):

    _update_signal: int | None = None
    treestore: Gtk.TreeStore
    treeview: Gtk.TreeView
    preset_select_callback: "Callable[[str, str], None]"

    DISPLAY_NAME: "Final" = 0
    DISPLAY_NAME_TYPE = str
    THEME_NAME: "Final" = 1
    THEME_NAME_TYPE = str
    THEME_PATH: "Final" = 2
    THEME_PATH_TYPE = str
    IS_SAVEABLE: "Final" = 3
    IS_SAVEABLE_TYPE = bool

    @overload
    def _get_selected_value(self, value: "Literal[0, 1, 2]") -> str:
        ...

    @overload
    def _get_selected_value(self, value: "Literal[3]") -> bool:
        ...

    def _get_selected_value(self, value: int) -> "Any":
        treepath = self._get_current_treepath()
        treeiter = self.treestore.get_iter(treepath)
        return self.treestore.get_value(treeiter, value)

    def __init__(
            self, preset_select_callback: "Callable[[str, str], None]",
    ) -> None:
        super().__init__()
        self.ui_settings = UISettings()
        self.set_size_request(width=self.ui_settings.preset_list_minimal_width, height=-1)

        self.preset_select_callback = preset_select_callback

        self.treestore = Gtk.TreeStore(
            self.DISPLAY_NAME_TYPE,
            self.THEME_NAME_TYPE,
            self.THEME_PATH_TYPE,
            self.IS_SAVEABLE_TYPE,
        )
        self.treeview = Gtk.TreeView(  # type: ignore[call-arg]
            model=self.treestore, headers_visible=False,
        )
        self.treeview.connect(
            "key-press-event", self._on_keypress,
        )
        self.treeview.connect(
            "row-collapsed", self._on_row_collapsed,
        )
        self.treeview.connect(
            "row-expanded", self._on_row_expanded,
        )
        column = Gtk.TreeViewColumn(
            cell_renderer=Gtk.CellRendererText(), markup=self.DISPLAY_NAME,
        )
        self.treeview.append_column(column)
        self.load_presets()

        self.add(self.treeview)

        GLib.idle_add(
            self.focus_first_available,
            priority=GLib.PRIORITY_HIGH,
        )

    ###########################################################################
    # Public interface:
    ###########################################################################

    def get_preset_path(self) -> str:
        return self._get_selected_value(self.THEME_PATH)

    def preset_is_saveable(self) -> bool:
        return self._get_selected_value(self.IS_SAVEABLE)

    def focus_preset_by_filepath(self, filepath: str) -> bool:
        treepath = self._find_treepath_by_filepath(
            self.treestore, filepath,
        )
        if treepath:
            self._focus_preset_by_treepath(treepath)
            return True
        return False

    def focus_first_available(self) -> None:
        init_iter = self.treestore.get_iter_first()
        while (
                init_iter and
                not self.treeview.row_expanded(
                    self.treestore.get_path(init_iter),  # type: ignore[arg-type]
                )
        ):
            init_iter = self.treestore.iter_next(init_iter)
        init_iter = self.treestore.iter_children(init_iter)
        if not init_iter:
            no_themes_found = "No themes found or smth else went wrong"
            raise RuntimeError(no_themes_found)
        self.treeview.set_cursor(self.treestore.get_path(init_iter))

    def load_presets(self) -> None:
        if self._update_signal:
            self.treeview.disconnect(self._update_signal)

        self.treestore.clear()
        all_presets = get_presets()
        self._load_system_presets(all_presets)
        self._load_plugin_presets(all_presets)
        self._load_user_presets(all_presets)

        self._update_signal = self.treeview.connect(
            "cursor_changed", self._on_preset_select,
        )

    def reload_presets(self, focus_on_theme: str | None = None) -> None:
        old_treepath = self._get_current_treepath()
        focus_on_theme = focus_on_theme or self.get_preset_path()
        self.load_presets()
        if not self.focus_preset_by_filepath(focus_on_theme):
            self._focus_preset_by_treepath(old_treepath)

    ###########################################################################
    # Private methods:
    ###########################################################################

    def _focus_preset_by_treepath(self, treepath: Gtk.TreePath) -> None:
        path_found = False
        while not path_found:
            try:
                self.treestore.get_iter(treepath)
                path_found = True
            except ValueError:  # noqa: PERF203
                treepath.prev()
        self.treeview.expand_to_path(treepath)  # type: ignore[arg-type]
        self.treeview.set_cursor(treepath)

    def _get_current_treepath(self) -> Gtk.TreePath:
        treepath: Gtk.TreePath = self.treeview.get_cursor()[0]
        if not treepath:
            no_tree_path = "PresetList: Can't get current TreePath"
            raise RuntimeError(no_tree_path)
        return treepath

    def _find_treepath_by_filepath(
            self, store: Gtk.TreeStore, target_filepath: str,
            treeiter: Gtk.TreeIter | None = None,
    ) -> Gtk.TreePath | None:
        if not treeiter:
            treeiter = self.treestore.get_iter_first()
        while treeiter:
            current_filepath = store[treeiter][self.THEME_PATH]
            if current_filepath == target_filepath:
                return store.get_path(treeiter)
            if store.iter_has_child(treeiter):
                childiter = store.iter_children(treeiter)
                child_result = self._find_treepath_by_filepath(
                    store, target_filepath, childiter,
                )
                if child_result:
                    return child_result
            treeiter = store.iter_next(treeiter)
        return None

    def _add_preset(
        self, display_name: str, name: str, path: str,
        *,
        saveable: bool,
        parent: Gtk.TreeIter | None = None,
    ) -> Gtk.TreeIter:
        return self.treestore.append(
            parent, [display_name, name, path, saveable],
        )

    def _add_directory(
            self, name: str, tree_id: str | None = None,
            parent: Gtk.TreeIter | None = None, template: str = "{}",
    ) -> Gtk.TreeIter:
        tree_id = tree_id or name
        return self.treestore.append(parent, [
            template.format(name), _SECTION_RESERVED_NAME, tree_id, False,
        ])

    def _add_section(
            self, section: Section, parent: Gtk.TreeIter | None = None,
    ) -> Gtk.TreeIter:
        return self._add_directory(
            template="<b>{}</b>", name=section.display_name,
            parent=parent, tree_id=section.name,
        )

    @staticmethod
    def _format_dirname(
            preset: "PresetFile",
            dirname: str,
            plugin_name: str | None = None,
            parent_dir: str | None = None,
    ) -> str:
        dir_template = "{}: {}"
        if parent_dir:
            preset_relpath = preset.path[len("/".join(parent_dir.split("/")[:-1])):]
        else:
            preset_relpath = (
                preset.name[len(dirname):]
                if plugin_name else preset.name
            )
        dir_display_name, _slash, item_display_name = preset_relpath.lstrip("/").partition("/")
        if item_display_name:
            dir_display_name = dir_template.format(
                dir_display_name.replace("_", " "), item_display_name,
            )
        if plugin_name:
            dir_display_name = dir_template.format(plugin_name, dir_display_name)
        return dir_display_name

    @staticmethod
    def _format_childname(preset_relpath: str) -> str:
        dir_template = "{}: {}"
        dir_display_name, _slash, item_display_name = preset_relpath.lstrip("/").partition("/")
        if item_display_name:
            dir_display_name = dir_template.format(
                dir_display_name.replace("_", " "), item_display_name,
            )
        return dir_display_name

    def _add_presets(
            self,
            dirname: str,
            preset_list: "list[PresetFile]",
            plugin_name: str | None = None,
            parent: Gtk.TreeIter | None = None,
            subdir_path: str | None = None,
    ) -> None:
        def preset_sorter(preset: "PresetFile") -> str:
            return preset.name.lower()

        sorted_preset_list = sorted(preset_list, key=preset_sorter)

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
            parent=parent,
        )

        last_subdir = None
        last_subdir_iter = None
        for preset in sorted_preset_list[1:]:
            if len(preset.name.split("/")) > 2:  # noqa: PLR2004
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
                        parent=piter,
                    )
                else:
                    self._add_presets(
                        dirname=dirname, preset_list=[preset],
                        parent=last_subdir_iter,
                        subdir_path=last_subdir,
                    )
            else:
                display_name = self._format_childname(
                    preset.name[len(dirname):]
                    if dirname else preset.name,
                )
                self._add_preset(
                    display_name=display_name,
                    name=preset.name,
                    path=preset.path,
                    saveable=preset.is_saveable,
                    parent=piter,
                )

    def _load_system_presets(self, all_presets: "dict[str, dict[str, list[PresetFile]]]") -> None:
        featured_dirs = ("Featured", )
        presets_iter = self._add_section(Sections.PRESETS)
        sorted_system_presets = sorted(
            all_presets.get(COLORS_DIR, {}).items(),
            key=lambda x: (x[0] not in featured_dirs, x[0].lower()),
        )
        for preset_dir, preset_list in sorted_system_presets:
            if preset_dir.startswith(PLUGIN_PATH_PREFIX):
                continue
            self._add_presets(
                dirname=preset_dir, preset_list=preset_list,
                parent=presets_iter,
            )
        if self.ui_settings.preset_list_sections_expanded.get(Sections.PRESETS.name, True):
            self.treeview.expand_row(self.treestore.get_path(presets_iter), False)

    def _load_plugin_presets(self, all_presets: "dict[str, dict[str, list[PresetFile]]]") -> None:
        plugins_iter = self._add_section(Sections.PLUGINS)
        for colors_dir, presets in all_presets.items():
            for preset_dir, preset_list in sorted(presets.items()):

                preset_plugin = None
                plugin_theme_dir = None
                for plugin in PluginLoader.get_import_plugins().values():
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
                if not preset_plugin:
                    warn_once("Can't load plugin", f"for opening {preset_dir}.")
                    continue
                plugin_name = preset_plugin.display_name or preset_plugin.name
                if plugin_theme_dir == preset_plugin.user_theme_dir:
                    plugin_name = preset_plugin.user_presets_display_name or plugin_name

                grouped_presets = group_presets_by_dir(
                    preset_list, os.path.join(colors_dir, preset_dir),
                )
                if len(grouped_presets) == 1 and not grouped_presets[0][0]:
                    grouped_presets = [
                        (preset.name, [preset])
                        for preset in grouped_presets[0][1]
                    ]

                plugin_presets_iter = self._add_directory(
                    name=plugin_name,
                    parent=plugins_iter,
                )
                for dir_name, group in grouped_presets:
                    self._add_presets(
                        dirname=dir_name,
                        preset_list=group,
                        parent=plugin_presets_iter,
                    )

        if self.ui_settings.preset_list_sections_expanded.get(Sections.PLUGINS.name, True):
            self.treeview.expand_row(self.treestore.get_path(plugins_iter), False)

    def _load_user_presets(self, all_presets: "dict[str, dict[str, list[PresetFile]]]") -> None:
        user_presets_iter = self._add_section(Sections.USER)
        for preset_dir, preset_list in sorted(all_presets.get(USER_COLORS_DIR, {}).items()):
            if preset_dir.startswith(PLUGIN_PATH_PREFIX):
                continue
            self._add_presets(
                dirname=preset_dir, preset_list=preset_list,
                parent=user_presets_iter,
            )
        if self.ui_settings.preset_list_sections_expanded.get(Sections.USER.name, True):
            self.treeview.expand_row(self.treestore.get_path(user_presets_iter), False)

    ###########################################################################
    # Signal handlers:
    ###########################################################################

    def _on_preset_select(self, _widget: Gtk.Widget) -> None:
        treepath = self._get_current_treepath()
        if not treepath:
            return
        treeiter = self.treestore.get_iter(treepath)
        current_theme = self.treestore.get_value(treeiter, self.THEME_NAME)
        if current_theme == _SECTION_RESERVED_NAME:
            return
        current_preset_path = self.treestore.get_value(treeiter, self.THEME_PATH)
        self.preset_select_callback(
            current_theme, current_preset_path,
        )

    def _on_keypress(self, _widget: Gtk.Widget, event: Gdk.EventKey) -> None:
        key = event.keyval
        if event.type != Gdk.EventType.KEY_PRESS:
            return
        if key == Keys.KEY_F5:
            self.reload_presets()
        elif key in {Keys.LEFT_ARROW, Keys.RIGHT_ARROW}:
            treepath = self._get_current_treepath()
            if not treepath:
                return
            if key == Keys.RIGHT_ARROW:
                self.treeview.expand_row(treepath, False)
            elif key == Keys.LEFT_ARROW:
                self.treeview.collapse_row(treepath)  # type: ignore[arg-type]

    def _on_row_expanded(
            self, _treeview: Gtk.TreeView, treeiter: Gtk.TreeIter, _treepath: Gtk.TreePath,
    ) -> None:
        if self.treestore.get_value(treeiter, self.THEME_NAME) == _SECTION_RESERVED_NAME:
            section_id = self.treestore.get_value(treeiter, self.THEME_PATH)
            self.ui_settings.preset_list_sections_expanded[section_id] = True

    def _on_row_collapsed(
            self, _treeview: Gtk.TreeView, treeiter: Gtk.TreeIter, _treepath: Gtk.TreePath,
    ) -> None:
        if self.treestore.get_value(treeiter, self.THEME_NAME) == _SECTION_RESERVED_NAME:
            section_id = self.treestore.get_value(treeiter, self.THEME_PATH)
            self.ui_settings.preset_list_sections_expanded[section_id] = False
