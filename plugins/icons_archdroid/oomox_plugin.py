import os

from oomox_gui.export.common import FileBasedExportDialog
from oomox_gui.plugin_api import OomoxIconsPlugin


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
ARCHDROID_THEME_DIR = os.path.join(PLUGIN_DIR, "archdroid-icon-theme/")


class ArchdroidIconsExportDialog(FileBasedExportDialog):
    timeout = 100

    def do_export(self):
        self.command = [
            "bash",
            os.path.join(ARCHDROID_THEME_DIR, "change_color.sh"),
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
            'display_name': _('Icons color'),
        },
    ]

    def preview_transform_function(self, svg_template, colorscheme):
        return svg_template.replace(
            "%ICONS_ARCHDROID%", colorscheme["ICONS_ARCHDROID"]
        )
