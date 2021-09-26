# pylint: disable=invalid-name
import os
import traceback

from gi.repository import Gtk

from .i18n import _
from .config import PLUGINS_DIR, USER_PLUGINS_DIR
from .plugin_api import (
    OomoxPlugin,
    OomoxImportPlugin, OomoxThemePlugin, OomoxIconsPlugin, OomoxExportPlugin,
)
from .helpers import get_plugin_module


from typing import TYPE_CHECKING  # pylint: disable=wrong-import-order
if TYPE_CHECKING:
    # pylint: disable=ungrouped-imports
    from typing import Dict  # noqa


class PluginLoader:

    _ALL_PLUGINS: "Dict[str, OomoxPlugin]" = {}
    _THEME_PLUGINS: "Dict[str, OomoxPlugin]" = {}
    _ICONS_PLUGINS: "Dict[str, OomoxPlugin]" = {}
    _EXPORT_PLUGINS: "Dict[str, OomoxPlugin]" = {}
    _IMPORT_PLUGINS: "Dict[str, OomoxPlugin]" = {}

    _init_done = False

    @classmethod
    @property
    def ALL_PLUGINS(cls):
        cls.init_plugins()
        return cls._ALL_PLUGINS

    @classmethod
    @property
    def THEME_PLUGINS(cls):
        cls.init_plugins()
        return cls._THEME_PLUGINS

    @classmethod
    @property
    def ICONS_PLUGINS(cls):
        cls.init_plugins()
        return cls._ICONS_PLUGINS

    @classmethod
    @property
    def EXPORT_PLUGINS(cls):
        cls.init_plugins()
        return cls._EXPORT_PLUGINS

    @classmethod
    @property
    def IMPORT_PLUGINS(cls):
        cls.init_plugins()
        return cls._IMPORT_PLUGINS

    @classmethod
    def load_plugin(cls, plugin_name: str, plugin_path: str) -> None:
        plugin_module = get_plugin_module(
            plugin_name,
            os.path.join(plugin_path, "oomox_plugin.py")
        )
        plugin_class = plugin_module.Plugin
        plugin = plugin_class()
        if not issubclass(plugin_class, OomoxPlugin):
            return
        cls._ALL_PLUGINS[plugin_name] = plugin
        if issubclass(plugin_class, OomoxImportPlugin):
            cls._IMPORT_PLUGINS[plugin_name] = plugin
        if issubclass(plugin_class, OomoxThemePlugin):
            cls._THEME_PLUGINS[plugin_name] = plugin
        if issubclass(plugin_class, OomoxIconsPlugin):
            cls._ICONS_PLUGINS[plugin_name] = plugin
        if issubclass(plugin_class, OomoxExportPlugin):
            cls._EXPORT_PLUGINS[plugin_name] = plugin

    @classmethod
    def init_plugins(cls) -> None:
        if cls._init_done:
            return
        cls._init_done = True
        all_plugin_paths = {}
        for _plugins_dir in (PLUGINS_DIR, USER_PLUGINS_DIR):
            if not os.path.exists(_plugins_dir):
                continue
            for plugin_name in os.listdir(_plugins_dir):
                all_plugin_paths[plugin_name] = os.path.join(_plugins_dir, plugin_name)
        for plugin_name, plugin_path in all_plugin_paths.items():
            try:
                cls.load_plugin(plugin_name, plugin_path)
            except Exception as exc:
                error_dialog = Gtk.MessageDialog()
                error_dialog.text = _('Error loading plugin "{plugin_name}"').format(
                    plugin_name=plugin_name
                )
                error_dialog.secondary_text = (
                    plugin_path +
                    ":\n" + '\n'.join([str(arg) for arg in exc.args]) +
                    '\n' * 2 +
                    traceback.format_exc()
                )
                error_dialog.buttons = Gtk.ButtonsType.CLOSE
                error_dialog.run()
                error_dialog.destroy()


def _print_debug_plugins():
    # @TODO: remove debug code:
    plugin_loader = PluginLoader()
    print("MAIN:")
    print()
    print("import plugins:")
    print(plugin_loader.IMPORT_PLUGINS)
    print("theme plugins:")
    print(plugin_loader.THEME_PLUGINS)
    print("icons plugins:")
    print(plugin_loader.ICONS_PLUGINS)
    print("export plugins:")
    print(plugin_loader.EXPORT_PLUGINS)
    print()
    print("all plugins:")
    print(plugin_loader.ALL_PLUGINS)
    print()
    for plugin_name, plugin in plugin_loader.ALL_PLUGINS.items():
        print(
            f"{plugin_name}: {plugin.display_name}"
        )


if __name__ == "__main__":
    _print_debug_plugins()
