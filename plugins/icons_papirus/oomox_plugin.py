import os
from typing import TYPE_CHECKING

from oomox_gui.color import mix_theme_colors
from oomox_gui.config import FALLBACK_COLOR
from oomox_gui.export_common import CommonIconThemeExportDialog
from oomox_gui.i18n import translate
from oomox_gui.plugin_api import OomoxIconsPlugin

if TYPE_CHECKING:
    from typing import Final

    from oomox_gui.theme_file import ThemeT


PLUGIN_DIR: "Final" = os.path.dirname(os.path.realpath(__file__))


class PapirusIconsExportDialog(CommonIconThemeExportDialog):

    timeout = 100
    config_name = "icons_papirus"

    def do_export(self) -> None:
        export_path = os.path.expanduser(
            self.option_widgets[self.OPTIONS.DEFAULT_PATH].get_text(),
        )
        self.command = [
            "bash",
            os.path.join(PLUGIN_DIR, "change_color.sh"),
            "--output", self.theme_name,
            "--destdir", export_path,
            self.temp_theme_path,
        ]
        super().do_export()


class Plugin(OomoxIconsPlugin):
    name = "papirus_icons"
    display_name = "Papirus"
    about_text = translate(
        "Papirus is a free and open source SVG icon theme for Linux, "
        "based on Paper Icon Set with a lot of new icons and a few extras, "
        "like Hardcode-Tray support, KDE colorscheme support, "
        "Folder Color support, and others.",
    )
    about_links = [
        {
            "name": translate("Homepage"),
            "url": "https://github.com/PapirusDevelopmentTeam/papirus-icon-theme",
        },
    ]

    export_dialog = PapirusIconsExportDialog
    preview_svg_dir = os.path.join(PLUGIN_DIR, "icon_previews/")

    theme_model_icons = [
        {
            "key": "ICONS_LIGHT_FOLDER",
            "type": "color",
            "fallback_key": "SEL_BG",
            "display_name": translate("Light Base (Folders)"),
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
        {
            "key": "ICONS_SYMBOLIC_ACTION",
            "type": "color",
            "fallback_function": lambda colors: mix_theme_colors(
                colors["MENU_FG"], colors["BTN_FG"],
                0.66,
            ),
            "display_name": translate("Actions Icons"),
        },
        {
            "key": "ICONS_SYMBOLIC_PANEL",
            "type": "color",
            "fallback_key": "FG",
            "display_name": translate("Panel Icons"),
        },
    ]

    def preview_transform_function(self, svg_template: str, colorscheme: "ThemeT") -> str:
        return svg_template.replace(
            "%LIGHT%", colorscheme["ICONS_LIGHT_FOLDER"] or FALLBACK_COLOR,
        ).replace(
            "%MEDIUM%", colorscheme["ICONS_MEDIUM"] or FALLBACK_COLOR,
        ).replace(
            "%DARK%", colorscheme["ICONS_DARK"] or FALLBACK_COLOR,
        ).replace(
            "%SYMBOLIC_ACTION%", colorscheme["ICONS_SYMBOLIC_ACTION"] or FALLBACK_COLOR,
        ).replace(
            "%SYMBOLIC_PANEL%", colorscheme["ICONS_SYMBOLIC_PANEL"] or FALLBACK_COLOR,
        )
