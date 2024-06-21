import os
import traceback
from typing import ClassVar

from gi.repository import Gtk

from .config import PLUGINS_DIR, USER_PLUGINS_DIR
from .helpers import get_plugin_module, log_error
from .i18n import translate
from .plugin_api import (
    OomoxExportPlugin,
    OomoxIconsPlugin,
    OomoxImportPlugin,
    OomoxPlugin,
    OomoxThemePlugin,
)


class PluginLoader:

    _ALL_PLUGINS: ClassVar[dict[str, OomoxPlugin]] = {}
    _THEME_PLUGINS: ClassVar[dict[str, OomoxThemePlugin]] = {}
    _ICONS_PLUGINS: ClassVar[dict[str, OomoxIconsPlugin]] = {}
    _EXPORT_PLUGINS: ClassVar[dict[str, OomoxExportPlugin]] = {}
    _IMPORT_PLUGINS: ClassVar[dict[str, OomoxImportPlugin]] = {}

    _init_done = False

    @classmethod
    def get_all_plugins(cls) -> dict[str, OomoxPlugin]:
        cls.init_plugins()
        return cls._ALL_PLUGINS

    @classmethod
    def get_theme_plugins(cls) -> dict[str, OomoxThemePlugin]:
        cls.init_plugins()
        return cls._THEME_PLUGINS

    @classmethod
    def get_icons_plugins(cls) -> dict[str, OomoxIconsPlugin]:
        cls.init_plugins()
        return cls._ICONS_PLUGINS

    @classmethod
    def get_export_plugins(cls) -> dict[str, OomoxExportPlugin]:
        cls.init_plugins()
        return cls._EXPORT_PLUGINS

    @classmethod
    def get_import_plugins(cls) -> dict[str, OomoxImportPlugin]:
        cls.init_plugins()
        return cls._IMPORT_PLUGINS

    @classmethod
    def load_plugin(cls, plugin_name: str, plugin_path: str) -> None:
        plugin_module = get_plugin_module(
            plugin_name,
            os.path.join(plugin_path, "oomox_plugin.py"),
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
            except Exception as exc:  # noqa: PERF203
                message_header = translate('Error loading plugin "{plugin_name}"').format(
                    plugin_name=plugin_name,
                )
                message_text = (
                    plugin_path +
                    ":\n" + "\n".join([str(arg) for arg in exc.args]) +
                    "\n" * 2 +
                    traceback.format_exc()
                )
                log_error(f"{message_header}\n{message_text}")
                error_dialog = Gtk.MessageDialog(
                    text=message_header,
                    secondary_text=message_text,
                    buttons=Gtk.ButtonsType.CLOSE,
                )
                error_dialog.run()
                error_dialog.destroy()


def _print_debug_plugins() -> None:
    # @TODO: remove debug code:
    plugin_loader = PluginLoader()
    print("MAIN:")
    print()
    print("import plugins:")
    print(plugin_loader.get_import_plugins())
    print("theme plugins:")
    print(plugin_loader.get_theme_plugins())
    print("icons plugins:")
    print(plugin_loader.get_icons_plugins())
    print("export plugins:")
    print(plugin_loader.get_export_plugins())
    print()
    print("all plugins:")
    print(plugin_loader.get_all_plugins())
    print()
    for plugin_name, plugin in plugin_loader.get_all_plugins().items():
        print(
            f"{plugin_name}: {plugin.display_name}",
        )


if __name__ == "__main__":
    _print_debug_plugins()
