import os
import importlib
import sys

from .config import PLUGINS_DIR, USER_PLUGINS_DIR
from .plugin_api import (
    OomoxPlugin,
    OomoxImportPlugin, OomoxThemePlugin, OomoxIconsPlugin, OomoxExportPlugin,
)


def get_plugin_module(name, path):
    if sys.version_info.minor >= 5:
        spec = importlib.util.spec_from_file_location(name, path)  # pylint: disable=no-member
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        loader = importlib.machinery.SourceFileLoader(name, path)
        module = loader.load_module()  # pylint: disable=deprecated-method
    return module


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
    plugin_module = get_plugin_module(
        plugin_name,
        os.path.join(plugin_path, "oomox_plugin.py")
    )
    plugin_class = plugin_module.Plugin
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
