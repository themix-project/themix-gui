import os
import importlib.util

from .config import PLUGINS_DIR, USER_PLUGINS_DIR
from .plugin_api import (
    OomoxPlugin,
    OomoxImportPlugin, OomoxThemePlugin, OomoxIconsPlugin, OomoxExportPlugin,
)


all_plugin_paths = {}  # pylint: disable=invalid-name
for _plugins_dir in (PLUGINS_DIR, USER_PLUGINS_DIR):
    if not os.path.exists(_plugins_dir):
        continue
    for plugin_name in os.listdir(_plugins_dir):
        all_plugin_paths[plugin_name] = os.path.join(_plugins_dir, plugin_name)

all_plugins = {}  # pylint: disable=invalid-name
import_plugins = {}  # pylint: disable=invalid-name
theme_plugins = {}  # pylint: disable=invalid-name
icons_plugins = {}  # pylint: disable=invalid-name
export_plugins = {}  # pylint: disable=invalid-name
for plugin_name, plugin_path in all_plugin_paths.items():
    spec = importlib.util.spec_from_file_location(
        plugin_name,
        os.path.join(plugin_path, "oomox_plugin.py")
    )
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    plugin_class = foo.Plugin
    plugin = plugin_class()
    if not issubclass(plugin_class, OomoxPlugin):
        continue
    all_plugins[plugin_name] = plugin
    if issubclass(plugin_class, OomoxImportPlugin):
        import_plugins[plugin_name] = plugin
    if issubclass(plugin_class, OomoxThemePlugin):
        theme_plugins[plugin_name] = plugin
    if issubclass(plugin_class, OomoxIconsPlugin):
        icons_plugins[plugin_name] = plugin
    if issubclass(plugin_class, OomoxExportPlugin):
        export_plugins[plugin_name] = plugin


if __name__ == "__main__":
    # @TODO: remove debug code:
    print("MAIN:")
    print("paths:")
    print(all_plugin_paths)
    print()
    print("import plugins:")
    print(import_plugins)
    print("theme plugins:")
    print(theme_plugins)
    print("icons plugins:")
    print(icons_plugins)
    print("export plugins:")
    print(export_plugins)
    print()
    print("all plugins:")
    print(all_plugins)
    print()
    for plugin_name, plugin in all_plugins.items():
        print(
            "{}: {}".format(plugin_name, plugin.display_name)
        )
