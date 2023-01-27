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


class SuruPlusIconsExportDialog(CommonIconThemeExportDialog):

    timeout = 300
    config_name = "icons_suru"

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
    name = "suruplus_icons"
    display_name = "Suru++"
    about_text = translate(
        "A cyberpunkish, elegant, futuristic, macOS-like, Papirus-like "
        "and modern Suru icons based on Suru iconset.",
    )
    about_links = [
        {
            "name": translate("Homepage"),
            "url": "https://github.com/gusbemacbe/suru-plus",
        },
    ]

    export_dialog = SuruPlusIconsExportDialog
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
            "value_filter": {
                "SURUPLUS_GRADIENT_ENABLED": False,
            },
        },
        {
            "key": "ICONS_SYMBOLIC_PANEL",
            "type": "color",
            "fallback_key": "FG",
            "display_name": translate("Panel Icons"),
        },
        {
            "key": "SURUPLUS_GRADIENT_ENABLED",
            "type": "bool",
            "fallback_value": False,
            "reload_options": True,
            "display_name": translate("Enable Gradients"),
        },
        {
            "key": "SURUPLUS_GRADIENT1",
            "type": "color",
            "fallback_key": "ICONS_SYMBOLIC_ACTION",
            "display_name": translate("Gradient Start Color"),
            "value_filter": {
                "SURUPLUS_GRADIENT_ENABLED": True,
            },
        },
        {
            "key": "SURUPLUS_GRADIENT2",
            "type": "color",
            "fallback_key": "SEL_BG",
            "display_name": translate("Gradient End Color"),
            "value_filter": {
                "SURUPLUS_GRADIENT_ENABLED": True,
            },
        },
    ]

    def preview_transform_function(self, svg_template: str, colorscheme: "ThemeT") -> str:
        icon_preview = svg_template.replace(
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
        if colorscheme["SURUPLUS_GRADIENT_ENABLED"] and "arrongin" in svg_template:
            return icon_preview.replace(
                "currentColor", "url(#arrongin)",
            ).replace(
                "%GRADIENT1%", colorscheme["SURUPLUS_GRADIENT1"] or FALLBACK_COLOR,
            ).replace(
                "%GRADIENT2%", colorscheme["SURUPLUS_GRADIENT2"] or FALLBACK_COLOR,
            )
        return icon_preview
