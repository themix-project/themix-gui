import os
from typing import TYPE_CHECKING

from gi.repository import Gtk

from .config import SCRIPT_DIR
from .i18n import translate
from .plugin_loader import PluginLoader

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from .plugin_api import OomoxExportPlugin, OomoxImportPlugin


def show_shortcuts(parent_window: Gtk.Window) -> None:
    path = os.path.join(SCRIPT_DIR, "shortcuts.ui")
    obj_id = "shortcuts"
    builder = Gtk.Builder.new_from_file(path)
    shortcuts_window = builder.get_object(obj_id)
    shortcuts_window.set_transient_for(parent_window)
    shortcuts_window.set_title(translate("Themix-GUI Keyboard Shortcuts"))
    shortcuts_window.set_wmclass("oomox", "Oomox")
    shortcuts_window.set_role("Oomox-Shortcuts")

    data: Sequence[
        tuple[str, Mapping[str, OomoxImportPlugin], Callable[[OomoxImportPlugin], str]] |
        tuple[str, Mapping[str, OomoxExportPlugin], Callable[[OomoxExportPlugin], str]]
    ] = (
        (
            "import_section",
            PluginLoader.get_import_plugins(),
            lambda plugin: (
                (plugin.import_text and
                 plugin.import_text.replace("_", "").replace("…", "")) or
                translate("Import {plugin_name}").format(plugin_name=plugin.display_name)
            ),
        ),
        (
            "export_section",
            PluginLoader.get_export_plugins(),
            lambda plugin: (
                (plugin.export_text and
                 plugin.export_text.replace("_", "").replace("…", "")) or
                translate("Export {plugin_name}").format(plugin_name=plugin.display_name)
            ),
        ),
    )
    for section_id, plugin_list, get_text in data:
        section = builder.get_object(section_id)
        for plugin in plugin_list.values():
            if not plugin.shortcut:
                continue
            shortcut = Gtk.ShortcutsShortcut(  # type: ignore[call-arg]
                title=get_text(plugin),  # type: ignore[arg-type]
                accelerator=plugin.shortcut,
            )
            section.add(shortcut)

    shortcuts_window.show_all()
