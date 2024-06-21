import os
from typing import TYPE_CHECKING

from gi.repository import Gtk

from .config import SCRIPT_DIR
from .i18n import translate
from .plugin_loader import PluginLoader

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from .plugin_api import OomoxPlugin


class PluginInfo(Gtk.ListBoxRow):

    def __init__(self, plugin: "OomoxPlugin") -> None:
        super().__init__()
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.box)

        plugin_name = Gtk.Label()
        plugin_name.set_markup(f"<b>{plugin.display_name or plugin.name}</b>")
        plugin_name.set_halign(Gtk.Align.START)
        self.box.add(plugin_name)

        for attr in ("about_text", "description"):
            value = getattr(plugin, attr, None)
            if value:
                about = Gtk.Label(value)
                about.set_halign(Gtk.Align.START)
                about.set_line_wrap(True)
                self.box.add(about)

        for link_info in plugin.about_links or []:
            link = Gtk.LinkButton.new_with_label(
                link_info["url"],
                link_info["name"],
            )
            link.set_hexpand(False)
            # link.set_halign(Gtk.Align.CENTER)
            link.set_halign(Gtk.Align.START)
            self.box.add(link)


def show_about(parent_window: Gtk.Window) -> None:
    path = os.path.join(SCRIPT_DIR, "about.ui")
    builder = Gtk.Builder.new_from_file(path)

    about_window = builder.get_object("about")
    about_window.set_transient_for(parent_window)
    about_window.set_title("About Themix GUI / Oomox")
    about_window.set_wmclass("oomox", "Oomox")
    about_window.set_role("Oomox-About")
    about_window.show()
    plugins_box = builder.get_object("plugins_box")

    def update_listbox_header(row: Gtk.ListBoxRow, before: bool) -> None:  # noqa: FBT001
        if before and not row.get_header():
            separator = Gtk.Separator(
                orientation=Gtk.Orientation.HORIZONTAL,  # type: ignore[call-arg]
            )
            separator.set_margin_top(4)
            separator.set_margin_bottom(8)
            row.set_header(separator)

    data: Sequence[tuple[str, Mapping[str, OomoxPlugin]]] = (
        (translate("Theme Plugins"), PluginLoader.get_theme_plugins()),
        (translate("Icon Plugins"), PluginLoader.get_icons_plugins()),
        (translate("Import Plugins"), PluginLoader.get_import_plugins()),
        (translate("Export Plugins"), PluginLoader.get_export_plugins()),
    )
    for title, plugin_list in data:
        section_label = Gtk.Label(title)
        section_label.set_margin_top(8)
        section_label.set_margin_bottom(4)
        plugins_box.add(section_label)
        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        listbox.set_header_func(update_listbox_header)
        plugins_box.add(listbox)
        for plugin in plugin_list.values():
            listbox.add(PluginInfo(plugin))

    plugins_box.show_all()
