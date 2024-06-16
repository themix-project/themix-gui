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
ARCHDROID_THEME_DIR: "Final" = os.path.join(PLUGIN_DIR, "archdroid-icon-theme/")


class ArchdroidIconsExportDialog(CommonIconThemeExportDialog):

    config_name = "icons_archdroid"
    timeout = 100

    def do_export(self) -> None:
        export_path = os.path.expanduser(
            self.option_widgets[self.OPTIONS.DEFAULT_PATH].get_text(),
        )
        self.command = [
            "bash",
            os.path.join(ARCHDROID_THEME_DIR, "change_color.sh"),
            "--output", self.theme_name,
            "--destdir", export_path,
            self.temp_theme_path,
        ]
        super().do_export()


class Plugin(OomoxIconsPlugin):

    name = "archdroid"
    display_name = "Archdroid"
    about_text = translate(
        "Port of Google's material design icons for "
        "Android Lollipop 5.0 to Linux. "
        "Some of these icons have been created manually "
        "(and were influenced by Ubuntu Mono, Mint-X and Numix).",
    )
    about_links = [
        {
            "name": translate("Homepage"),
            "url": "https://github.com/GreenRaccoon23/archdroid-icon-theme",
        },
    ]

    export_dialog = ArchdroidIconsExportDialog
    preview_svg_dir = os.path.join(PLUGIN_DIR, "icon_previews/")

    theme_model_icons = [
        {
            "key": "ICONS_ARCHDROID",
            "type": "color",
            "fallback_key": "SEL_BG",
            "display_name": translate("Icons Color"),
        },
    ]

    def preview_transform_function(self, svg_template: str, colorscheme: "ThemeT") -> str:
        return svg_template.replace(
            "%ICONS_ARCHDROID%", colorscheme["ICONS_ARCHDROID"] or FALLBACK_COLOR,
        )
