import os

from gi.repository import Gtk

from .config import SCRIPT_DIR
from .plugin_loader import PluginLoader


def show_shortcuts(parent_window):
    path = os.path.join(SCRIPT_DIR, 'shortcuts.ui')
    obj_id = "shortcuts"
    builder = Gtk.Builder.new_from_file(path)
    shortcuts_window = builder.get_object(obj_id)
    shortcuts_window.set_transient_for(parent_window)
    shortcuts_window.set_title("Oomox Keyboard Shortcuts")
    shortcuts_window.set_wmclass("oomox", "Oomox")
    shortcuts_window.set_role("Oomox-Shortcuts")

    for section_id, plugin_list, get_text in (
            (
                    "import_section",
                    PluginLoader.get_import_plugins(),
                    lambda plugin: (
                        plugin.import_text and
                        plugin.import_text.replace('_', '').replace('…', '') or
                        f"Import {plugin.display_name}"
                    ),
            ),
            (
                    "export_section",
                    PluginLoader.get_export_plugins(),
                    lambda plugin: (
                        plugin.export_text and
                        plugin.export_text.replace('_', '').replace('…', '') or
                        f"Export {plugin.display_name}"
                    ),
            ),
    ):
        section = builder.get_object(section_id)
        for plugin in plugin_list.values():
            if not plugin.shortcut:
                continue
            shortcut = Gtk.ShortcutsShortcut(
                title=get_text(plugin),
                accelerator=plugin.shortcut
            )
            section.add(shortcut)

    shortcuts_window.show_all()
