import os

from oomox_gui.config import FALLBACK_COLOR
from oomox_gui.export_common import FileBasedExportDialog
from oomox_gui.plugin_api import OomoxIconsPlugin
from oomox_gui.i18n import _


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
ARCHDROID_THEME_DIR = os.path.join(PLUGIN_DIR, "archdroid-icon-theme/")


class ArchdroidIconsExportDialog(FileBasedExportDialog):
    timeout = 100

    def do_export(self):
        self.command = [
            "bash",
            os.path.join(ARCHDROID_THEME_DIR, "change_color.sh"),
            "-o", self.theme_name,
            self.temp_theme_path,
        ]
        super().do_export()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.do_export()


class Plugin(OomoxIconsPlugin):

    name = 'archdroid'
    display_name = 'Archdroid'
    export_dialog = ArchdroidIconsExportDialog
    preview_svg_dir = os.path.join(PLUGIN_DIR, "icon_previews/")

    theme_model_icons = [
        {
            'key': 'ICONS_ARCHDROID',
            'type': 'color',
            'fallback_key': 'SEL_BG',
            'display_name': _('Icons Color'),
        },
    ]

    def preview_transform_function(self, svg_template, colorscheme):
        return svg_template.replace(
            "%ICONS_ARCHDROID%", colorscheme["ICONS_ARCHDROID"] or FALLBACK_COLOR
        )
