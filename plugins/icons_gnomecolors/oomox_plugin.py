import os
from typing import TYPE_CHECKING

from oomox_gui.config import FALLBACK_COLOR
from oomox_gui.export_common import CommonIconThemeExportDialog
from oomox_gui.i18n import translate
from oomox_gui.plugin_api import OomoxIconsPlugin

if TYPE_CHECKING:
    from typing import Final

    from oomox_gui.theme_file import ThemeT


PLUGIN_DIR: "Final" = os.path.dirname(os.path.realpath(__file__))
GNOME_COLORS_ICON_THEME_DIR: "Final" = os.path.join(PLUGIN_DIR, "gnome-colors-icon-theme/")


class GnomeColorsIconsExportDialog(CommonIconThemeExportDialog):

    timeout = 600
    config_name = "icons_gnomecolors"

    def do_export(self) -> None:
        export_path = os.path.expanduser(
            self.option_widgets[self.OPTIONS.DEFAULT_PATH].get_text(),
        )
        self.command = [
            "bash",
            os.path.join(GNOME_COLORS_ICON_THEME_DIR, "change_color.sh"),
            "--output", self.theme_name,
            "--destdir", export_path,
            self.temp_theme_path,
        ]
        super().do_export()


class Plugin(OomoxIconsPlugin):

    name = "gnome_colors"
    display_name = "Gnome-Colors"
    about_text = translate(
        "GNOME-Colors is mostly inspired/based on "
        "Tango, GNOME, Elementary, Tango-Generator "
        "and many other open-source projects.",
    )
    about_links = [
        {
            "name": translate("Homepage"),
            "url": "https://github.com/themix-project/gnome-colors-icon-theme",
        },
    ]

    export_dialog = GnomeColorsIconsExportDialog
    preview_svg_dir = os.path.join(PLUGIN_DIR, "icon_previews/")

    theme_model_icons = [
        {
            "key": "ICONS_LIGHT_FOLDER",
            "type": "color",
            "fallback_key": "SEL_BG",
            "display_name": translate("Light Base (Folders)"),
        },
        {
            "key": "ICONS_LIGHT",
            "fallback_key": "SEL_BG",
            "type": "color",
            "display_name": translate("Light Base"),
        },
        {
            "key": "ICONS_MEDIUM",
            "type": "color",
            "fallback_key": "BTN_BG",
            "display_name": translate("Medium Base"),
        },
        {
            "key": "ICONS_DARK",
            "type": "color",
            "fallback_key": "HDR_BG",
            "display_name": translate("Dark Stroke"),
        },
    ]

    def preview_transform_function(self, svg_template: str, colorscheme: "ThemeT") -> str:
        return svg_template.replace(
            "LightFolderBase", colorscheme["ICONS_LIGHT_FOLDER"] or FALLBACK_COLOR,
        ).replace(
            "LightBase", colorscheme["ICONS_LIGHT"] or FALLBACK_COLOR,
        ).replace(
            "MediumBase", colorscheme["ICONS_MEDIUM"] or FALLBACK_COLOR,
        ).replace(
            "DarkStroke", colorscheme["ICONS_DARK"] or FALLBACK_COLOR,
        )
