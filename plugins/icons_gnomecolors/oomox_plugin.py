import os

from oomox_gui.config import FALLBACK_COLOR
from oomox_gui.export.common import FileBasedExportDialog
from oomox_gui.plugin_api import OomoxIconsPlugin


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
GNOME_COLORS_ICON_THEME_DIR = os.path.join(PLUGIN_DIR, "gnome-colors-icon-theme/")


class GnomeColorsIconsExportDialog(FileBasedExportDialog):
    timeout = 600

    def do_export(self):
        self.command = [
            "bash",
            os.path.join(GNOME_COLORS_ICON_THEME_DIR, "change_color.sh"),
            "-o", self.theme_name,
            self.temp_theme_path,
        ]
        super().do_export()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.do_export()


class Plugin(OomoxIconsPlugin):

    name = 'gnome_colors'
    display_name = 'Gnome-Colors'
    export_dialog = GnomeColorsIconsExportDialog
    preview_svg_dir = os.path.join(PLUGIN_DIR, "icon_previews/")

    theme_model_icons = [
        {
            'key': 'ICONS_LIGHT_FOLDER',
            'type': 'color',
            'fallback_key': 'SEL_BG',
            'display_name': _('Light base (folders)'),
        },
        {
            'key': 'ICONS_LIGHT',
            'fallback_key': 'SEL_BG',
            'type': 'color',
            'display_name': _('Light base'),
        },
        {
            'key': 'ICONS_MEDIUM',
            'type': 'color',
            'fallback_key': 'BTN_BG',
            'display_name': _('Medium base'),
        },
        {
            'key': 'ICONS_DARK',
            'type': 'color',
            'fallback_key': 'MENU_BG',
            'display_name': _('Dark stroke'),
        },
    ]

    def preview_transform_function(self, svg_template, colorscheme):
        return svg_template.replace(
            "LightFolderBase", colorscheme["ICONS_LIGHT_FOLDER"] or FALLBACK_COLOR
        ).replace(
            "LightBase", colorscheme["ICONS_LIGHT"] or FALLBACK_COLOR
        ).replace(
            "MediumBase", colorscheme["ICONS_MEDIUM"] or FALLBACK_COLOR
        ).replace(
            "DarkStroke", colorscheme["ICONS_DARK"] or FALLBACK_COLOR
        )
