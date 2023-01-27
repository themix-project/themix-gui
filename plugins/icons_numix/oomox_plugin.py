import os
from typing import TYPE_CHECKING

from oomox_gui.config import FALLBACK_COLOR
from oomox_gui.export_common import CommonIconThemeExportDialog
from oomox_gui.i18n import translate
from oomox_gui.plugin_api import OomoxIconsPlugin

if TYPE_CHECKING:
    from typing import Final

    from oomox_gui.preview import IconThemePreview
    from oomox_gui.theme_file import ThemeT


PLUGIN_DIR: "Final" = os.path.dirname(os.path.realpath(__file__))


class NumixIconsExportDialog(CommonIconThemeExportDialog):

    timeout = 100
    config_name = "icons_numix"

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

    # if not os.path.exists('/usr/share/icons/Numix/'):
    #     raise Exception('Numix icon theme need to be installed first')

    name = "numix_icons"
    display_name = "Numix"
    about_text = translate(
        "Numix is the official icon theme from the Numix Project. "
        "It is heavily inspired by, and based upon parts of the "
        "Elementary, Humanity and Gnome icon themes.",
    )
    about_links = [
        {
            "name": translate("Homepage"),
            "url": "https://github.com/numixproject/numix-icon-theme",
        },
    ]

    export_dialog = NumixIconsExportDialog
    preview_svg_dir = os.path.join(PLUGIN_DIR, "icon_previews/0/")

    theme_model_icons = [
        {
            "key": "ICONS_NUMIX_STYLE",
            "type": "options",
            "options": [{
                "value": str(style_id),
                "display_name": translate("Style {number}").format(number=style_id),
            } for style_id in range(6)],
            "display_name": translate("Numix Style"),
        },
        # {
        #     'key': 'ICONS_NUMIX_SHAPE',
        #     'type': 'options',
        #     'options': [{
        #         'value': 'normal',
        #         'display_name': 'Normal',
        #     }, {
        #         'value': 'circle',
        #         'display_name': 'Circle',
        #     }, {
        #         'value': 'square',
        #         'display_name': 'Square',
        #     }],
        #     'display_name': translate('Icons Shape'),
        # },
        {
            "key": "ICONS_LIGHT_FOLDER",
            "type": "color",
            "fallback_key": "SEL_BG",
            "display_name": translate("Light Base (Folders)"),
        },
        # {
        #     'key': 'ICONS_LIGHT',
        #     'fallback_key': 'SEL_BG',
        #     'type': 'color',
        #     'display_name': translate('Light Base'),
        # },
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

    def preview_before_load_callback(
            self, preview_object: "IconThemePreview", colorscheme: "ThemeT",
    ) -> None:
        self.preview_svg_dir = os.path.join(
            PLUGIN_DIR, "icon_previews/", colorscheme["ICONS_NUMIX_STYLE"],
        )
        preview_object.icons_plugin_name = "_update"

    def preview_transform_function(self, svg_template: str, colorscheme: "ThemeT") -> str:
        # ).replace(
        #     "00ff00", colorscheme["ICONS_LIGHT"] or FALLBACK_COLOR
        return svg_template.replace(
            "%LIGHT%", colorscheme["ICONS_LIGHT_FOLDER"] or FALLBACK_COLOR,
        ).replace(
            "%MEDIUM%", colorscheme["ICONS_MEDIUM"] or FALLBACK_COLOR,
        ).replace(
            "%DARK%", colorscheme["ICONS_DARK"] or FALLBACK_COLOR,
        )
