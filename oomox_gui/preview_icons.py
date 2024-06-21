from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from gi.repository import Gtk

from .config import DEFAULT_ENCODING
from .gtk_helpers import ScaledImage

if TYPE_CHECKING:
    from .plugin_api import OomoxIconsPlugin
    from .theme_file import ThemeT


class IconsNames(Enum):
    HOME = "user-home"
    DESKTOP = "user-desktop"
    FILE_MANAGER = "system-file-manager"


class IconThemePreview(Gtk.ListBox):

    icons_plugin_name: str | None = None

    icons_templates: dict[str, str]
    icons_imageboxes: dict[str, ScaledImage]

    def __init__(self) -> None:
        self.icons_templates = {}
        self.icons_imageboxes = {}

        super().__init__()
        self.set_margin_left(10)
        self.set_margin_right(10)
        self.set_selection_mode(Gtk.SelectionMode.NONE)

        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.add(hbox)
        for icon in IconsNames:
            icon_imagebox = ScaledImage(width=48)
            hbox.pack_start(icon_imagebox, True, True, 0)
            self.icons_imageboxes[icon.name] = icon_imagebox
        self.add(row)
        self.show_all()

    def update_preview(self, colorscheme: "ThemeT", theme_plugin: "OomoxIconsPlugin") -> None:
        theme_plugin.preview_before_load_callback(self, colorscheme)
        transform_function = theme_plugin.preview_transform_function
        self.load_icon_templates(theme_plugin)
        for icon in IconsNames:
            new_svg_image = transform_function(
                self.icons_templates[icon.name],
                colorscheme,
            ).encode("ascii")
            self.icons_imageboxes[icon.name].set_from_bytes(new_svg_image)

    def load_icon_templates(self, theme_plugin: "OomoxIconsPlugin") -> None:
        if theme_plugin.name == self.icons_plugin_name:
            return
        self.icons_plugin_name = theme_plugin.name
        for icon in IconsNames:
            template_path = f"{icon.value}.svg.template"
            data = Path(
                Path(theme_plugin.preview_svg_dir) / Path(template_path),
            ).read_bytes()
            self.icons_templates[icon.name] = data.decode(DEFAULT_ENCODING)
