import os

from oomox_gui.config import FALLBACK_COLOR
from oomox_gui.export_common import FileBasedExportDialog
from oomox_gui.plugin_api import OomoxIconsPlugin
from oomox_gui.i18n import _


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))


class PapirusIconsExportDialog(FileBasedExportDialog):
    timeout = 100

    def do_export(self):
        self.command = [
            "bash",
            os.path.join(PLUGIN_DIR, "change_color.sh"),
            "-o", self.theme_name,
            self.temp_theme_path,
        ]
        super().do_export()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.do_export()


class Plugin(OomoxIconsPlugin):
    name = 'papirus_icons'
    display_name = 'Papirus'
    export_dialog = PapirusIconsExportDialog
    preview_svg_dir = os.path.join(PLUGIN_DIR, "icon_previews/")

    theme_model_icons = [
        {
            'key': 'ICONS_PAPIRUS_THEME',
            'type': 'options',
            'options': [{
                'value': 'Papirus',
                'display_name': 'Papirus',
            }, {
                'value': 'Papirus-Dark',
                'display_name': 'Papirus-Dark',
            }, {
                'value': 'Papirus-Light',
                'display_name': 'Papirus-Light',
            }],
            'display_name': _('Base Theme'),
        },
        {
            'key': 'ICONS_LIGHT_FOLDER',
            'type': 'color',
            'fallback_key': 'SEL_BG',
            'display_name': _('Light Base (Folders)'),
        },
        {
            'key': 'ICONS_MEDIUM',
            'type': 'color',
            'fallback_key': 'BTN_BG',
            'display_name': _('Medium Base'),
        },
        {
            'key': 'ICONS_DARK',
            'type': 'color',
            'fallback_key': 'HDR_BG',
            'display_name': _('Dark Stroke'),
        },
    ]

    def preview_transform_function(self, svg_template, colorscheme):
        return svg_template.replace(
            "%LIGHT%", colorscheme["ICONS_LIGHT_FOLDER"] or FALLBACK_COLOR
        ).replace(
            "%MEDIUM%", colorscheme["ICONS_MEDIUM"] or FALLBACK_COLOR
        ).replace(
            "%DARK%", colorscheme["ICONS_DARK"] or FALLBACK_COLOR
        )
