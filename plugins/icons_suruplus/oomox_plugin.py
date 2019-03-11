# pylint: disable=too-few-public-methods
import os

from oomox_gui.config import FALLBACK_COLOR
from oomox_gui.export_common import ExportDialogWithOptions
from oomox_gui.plugin_api import OomoxIconsPlugin
from oomox_gui.i18n import _
from oomox_gui.color import mix_theme_colors


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))

OPTION_DEFAULT_PATH = 'default_path'


class SuruPlusIconsExportDialog(ExportDialogWithOptions):

    timeout = 300
    config_name = 'icons_suru'

    def do_export(self):
        export_path = self.option_widgets[OPTION_DEFAULT_PATH].get_text()

        self.command = [
            "bash",
            os.path.join(PLUGIN_DIR, "change_color.sh"),
            "-o", self.theme_name,
            "--destdir", export_path,
            self.temp_theme_path,
        ]
        super().do_export()

        new_destdir_guess = export_path.rsplit('/'+self.theme_name, 1)
        if new_destdir_guess:
            new_destination_dir = new_destdir_guess[0]
        else:
            new_destination_dir = os.path.abspath(
                os.path.join(export_path, '/..')
            )
        self.export_config[OPTION_DEFAULT_PATH] = new_destination_dir
        self.export_config.save()

    def __init__(self, *args, **kwargs):
        default_icons_path = os.path.join(os.environ['HOME'], '.icons')
        if os.environ.get('XDG_CURRENT_DESKTOP', '').lower() in ('kde', 'lxqt', ):
            default_icons_path = os.path.join(
                os.environ.get(
                    'XDG_DATA_HOME',
                    os.path.join(os.environ['HOME'], '.local/share')
                ),
                'icons',
            )
        super().__init__(
            *args,
            export_options={
                OPTION_DEFAULT_PATH: {
                    'default': default_icons_path,
                    'display_name': _("Export _path: "),
                },
            },
            **kwargs
        )
        self.option_widgets[OPTION_DEFAULT_PATH].set_text(
            os.path.join(
                self.export_config[OPTION_DEFAULT_PATH],
                self.theme_name,
            )
        )


class Plugin(OomoxIconsPlugin):
    name = 'suruplus_icons'
    display_name = 'Suru++'
    export_dialog = SuruPlusIconsExportDialog
    preview_svg_dir = os.path.join(PLUGIN_DIR, "icon_previews/")

    theme_model_icons = [
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
        {
            'key': 'ICONS_SYMBOLIC_ACTION',
            'type': 'color',
            'fallback_function': lambda colors: mix_theme_colors(
                colors['MENU_FG'], colors['BTN_FG'],
                0.66
            ),
            'display_name': _('Actions Icons'),
            'value_filter': {
                'SURUPLUS_GRADIENT_ENABLED': False,
            },
        },
        {
            'key': 'ICONS_SYMBOLIC_PANEL',
            'type': 'color',
            'fallback_key': 'FG',
            'display_name': _('Panel Icons'),
        },
        {
            'key': 'SURUPLUS_GRADIENT_ENABLED',
            'type': 'bool',
            'fallback_value': False,
            'reload_options': True,
            'display_name': _('Enable Gradients'),
        },
        {
            'key': 'SURUPLUS_GRADIENT1',
            'type': 'color',
            'fallback_key': 'ICONS_SYMBOLIC_ACTION',
            'display_name': _('Gradient Start Color'),
            'value_filter': {
                'SURUPLUS_GRADIENT_ENABLED': True,
            },
        },
        {
            'key': 'SURUPLUS_GRADIENT2',
            'type': 'color',
            'fallback_key': 'SEL_BG',
            'display_name': _('Gradient End Color'),
            'value_filter': {
                'SURUPLUS_GRADIENT_ENABLED': True,
            },
        },
    ]

    def preview_transform_function(self, svg_template, colorscheme):
        icon_preview = svg_template.replace(
            "%LIGHT%", colorscheme["ICONS_LIGHT_FOLDER"] or FALLBACK_COLOR
        ).replace(
            "%MEDIUM%", colorscheme["ICONS_MEDIUM"] or FALLBACK_COLOR
        ).replace(
            "%DARK%", colorscheme["ICONS_DARK"] or FALLBACK_COLOR
        ).replace(
            "%SYMBOLIC_ACTION%", colorscheme["ICONS_SYMBOLIC_ACTION"] or FALLBACK_COLOR
        ).replace(
            "%SYMBOLIC_PANEL%", colorscheme["ICONS_SYMBOLIC_PANEL"] or FALLBACK_COLOR
        )
        if colorscheme['SURUPLUS_GRADIENT_ENABLED'] and 'arrongin' in svg_template:
            icon_preview = icon_preview.replace(
                "currentColor", "url(#arrongin)"
            ).replace(
                "%GRADIENT1%", colorscheme["SURUPLUS_GRADIENT1"] or FALLBACK_COLOR
            ).replace(
                "%GRADIENT2%", colorscheme["SURUPLUS_GRADIENT2"] or FALLBACK_COLOR
            )
        return icon_preview
