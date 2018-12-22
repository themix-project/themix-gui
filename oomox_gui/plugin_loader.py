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


ALL_PLUGINS = {}
THEME_PLUGINS = {}
ICONS_PLUGINS = {}
EXPORT_PLUGINS = {}
IMPORT_PLUGINS = {}


def load_plugin(plugin_name, plugin_path):
    plugin_module = get_plugin_module(
        plugin_name,
        os.path.join(plugin_path, "oomox_plugin.py")
    )
    plugin_class = plugin_module.Plugin
    plugin = plugin_class()
    if not issubclass(plugin_class, OomoxPlugin):
        return
    ALL_PLUGINS[plugin_name] = plugin
    if issubclass(plugin_class, OomoxImportPlugin):
        IMPORT_PLUGINS[plugin_name] = plugin
    if issubclass(plugin_class, OomoxThemePlugin):
        THEME_PLUGINS[plugin_name] = plugin
    if issubclass(plugin_class, OomoxIconsPlugin):
        ICONS_PLUGINS[plugin_name] = plugin
    if issubclass(plugin_class, OomoxExportPlugin):
        EXPORT_PLUGINS[plugin_name] = plugin


def init_plugins():
    all_plugin_paths = {}
    for _plugins_dir in (PLUGINS_DIR, USER_PLUGINS_DIR):
        if not os.path.exists(_plugins_dir):
            continue
        for plugin_name in os.listdir(_plugins_dir):
            all_plugin_paths[plugin_name] = os.path.join(_plugins_dir, plugin_name)
    for plugin_name, plugin_path in all_plugin_paths.items():
        try:
            load_plugin(plugin_name, plugin_path)
        except Exception as exc:
            error_dialog = Gtk.MessageDialog(
                text=_('Error loading plugin "{plugin_name}"').format(
                    plugin_name=plugin_name
                ),
                secondary_text=(
                    plugin_path +
                    ":\n" + '\n'.join([str(arg) for arg in exc.args]) +
                    '\n' * 2 +
                    traceback.format_exc()
                ),
                buttons=Gtk.ButtonsType.CLOSE
            )
            error_dialog.run()
            error_dialog.destroy()


init_plugins()


def _print_debug_plugins():
    # @TODO: remove debug code:
    print("MAIN:")
    print()
    print("import plugins:")
    print(IMPORT_PLUGINS)
    print("theme plugins:")
    print(THEME_PLUGINS)
    print("icons plugins:")
    print(ICONS_PLUGINS)
    print("export plugins:")
    print(EXPORT_PLUGINS)
    print()
    print("all plugins:")
    print(ALL_PLUGINS)
    print()
    for plugin_name, plugin in ALL_PLUGINS.items():
        print(
            "{}: {}".format(plugin_name, plugin.display_name)
        )


if __name__ == "__main__":
    _print_debug_plugins()
