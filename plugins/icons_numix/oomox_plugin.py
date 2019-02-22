import os

from oomox_gui.config import FALLBACK_COLOR
from oomox_gui.export_common import FileBasedExportDialog
from oomox_gui.plugin_api import OomoxIconsPlugin
from oomox_gui.i18n import _


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))


class NumixIconsExportDialog(FileBasedExportDialog):
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

    # if not os.path.exists('/usr/share/icons/Numix/'):
    #     raise Exception('Numix icon theme need to be installed first')

    name = 'numix_icons'
    display_name = 'Numix'
    export_dialog = NumixIconsExportDialog
    preview_svg_dir = os.path.join(PLUGIN_DIR, "icon_previews/0/")

    theme_model_icons = [
        {
            'key': 'ICONS_NUMIX_STYLE',
            'type': 'options',
            'options': [{
                'value': str(style_id),
                'display_name': _("Style {number}").format(number=style_id),
            } for style_id in range(6)],
            'display_name': _('Numix Style'),
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
        #     'display_name': _('Icons Shape'),
        # },
        {
            'key': 'ICONS_LIGHT_FOLDER',
            'type': 'color',
            'fallback_key': 'SEL_BG',
            'display_name': _('Light Base (Folders)'),
        },
        # {
        #     'key': 'ICONS_LIGHT',
        #     'fallback_key': 'SEL_BG',
        #     'type': 'color',
        #     'display_name': _('Light Base'),
        # },
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

    def preview_before_load_callback(self, preview_object, colorscheme):
        self.preview_svg_dir = os.path.join(
            PLUGIN_DIR, "icon_previews/", colorscheme["ICONS_NUMIX_STYLE"]
        )
        preview_object.icons_plugin_name = '_update'

    def preview_transform_function(self, svg_template, colorscheme):
        # ).replace(
        #     "00ff00", colorscheme["ICONS_LIGHT"] or FALLBACK_COLOR
        return svg_template.replace(
            "%LIGHT%", colorscheme["ICONS_LIGHT_FOLDER"] or FALLBACK_COLOR
        ).replace(
            "%MEDIUM%", colorscheme["ICONS_MEDIUM"] or FALLBACK_COLOR
        ).replace(
            "%DARK%", colorscheme["ICONS_DARK"] or FALLBACK_COLOR
        )
