import os

from gi.repository import Gtk

from oomox_gui.export_common import OPTION_GTK2_HIDPI, CommonGtkThemeExportDialog
from oomox_gui.plugin_api import OomoxThemePlugin
from oomox_gui.i18n import _


OPTION_GTK3_CURRENT_VERSION_ONLY = 'OPTION_GTK3_CURRENT_VERSION_ONLY'
OPTION_EXPORT_CINNAMON_THEME = 'OPTION_EXPORT_CINNAMON_THEME'


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
GTK_THEME_DIR = os.path.join(PLUGIN_DIR, "gtk-theme/")


class OomoxThemeExportDialog(CommonGtkThemeExportDialog):
    timeout = 100
    config_name = 'gtk_theme_oomox'

    def do_export(self):
        self.command = [
            "bash",
            os.path.join(GTK_THEME_DIR, "change_color.sh"),
            "--hidpi", str(self.export_config[OPTION_GTK2_HIDPI]),
            "--output", self.theme_name,
            self.temp_theme_path,
        ]
        make_opts = []
        if self.export_config[OPTION_GTK3_CURRENT_VERSION_ONLY]:
            if Gtk.get_minor_version() >= 20:
                make_opts += ["gtk320"]
            else:
                make_opts += ["gtk3"]
        else:
            make_opts += ["gtk3", "gtk320"]
        if self.export_config[OPTION_EXPORT_CINNAMON_THEME]:
            make_opts += ["css_cinnamon"]
        if make_opts:
            self.command += [
                "--make-opts", " ".join(make_opts),
            ]
        super().do_export()

    def __init__(self, transient_for, colorscheme, theme_name, **kwargs):
        super().__init__(
            transient_for=transient_for,
            colorscheme=colorscheme,
            theme_name=theme_name,
            add_options={
                OPTION_GTK3_CURRENT_VERSION_ONLY: {
                    'default': False,
                    'display_name': _("Generate theme only for the current _GTK+3 version\n"
                                      "instead of both 3.18 and 3.20+"),
                },
                OPTION_EXPORT_CINNAMON_THEME: {
                    'default': False,
                    'display_name': _("Generate theme for _Cinnamon"),
                },
            },
            **kwargs
        )


class Plugin(OomoxThemePlugin):

    name = 'oomox'
    display_name = 'Oomox (Numix-Based)'
    description = (
        'GTK+2, GTK+3, Qt5ct\n'
        'Cinnamon, Metacity, Openbox, Unity, Xfwm'
    )
    export_dialog = OomoxThemeExportDialog
    gtk_preview_dir = os.path.join(PLUGIN_DIR, "gtk_preview_css/")

    enabled_keys_gtk = [
        'BG',
        'FG',
        'HDR_BG',
        'HDR_FG',
        'SEL_BG',
        'SEL_FG',
        'ACCENT_BG',
        'TXT_BG',
        'TXT_FG',
        'BTN_BG',
        'BTN_FG',
        'HDR_BTN_BG',
        'HDR_BTN_FG',
        'WM_BORDER_FOCUS',
        'WM_BORDER_UNFOCUS',
    ]

    enabled_keys_options = [
        'ROUNDNESS',
        'SPACING',
        'GRADIENT',
        'GTK3_GENERATE_DARK',
    ]

    theme_model_options = [
        {
            'type': 'separator',
            'display_name': _('GTK3 Theme Options'),
            'value_filter': {
                'THEME_STYLE': 'oomox',
            },
        },
        {
            'key': 'SPACING',
            'type': 'int',
            'fallback_value': 3,
            'display_name': _('Spacing'),
        },
        {
            'key': 'OUTLINE_WIDTH',
            'type': 'int',
            'fallback_value': 1,
            'display_name': _('Focused Outline Width'),
        },
        {
            'key': 'BTN_OUTLINE_WIDTH',
            'type': 'int',
            'fallback_value': 1,
            'display_name': _('Focused Button Outline Width'),
        },
        {
            'key': 'BTN_OUTLINE_OFFSET',
            'type': 'int',
            'fallback_value': -3,
            'min_value': -20,
            'display_name': _('Focused Button Outline Offset'),
        },
        {
            'key': 'GTK3_GENERATE_DARK',
            'type': 'bool',
            'fallback_value': True,
            'display_name': _('Add Dark Variant'),
        },

        {
            'type': 'separator',
            'display_name': _('Text Input Caret'),
            'value_filter': {
                'THEME_STYLE': 'oomox',
            },
        },
        {
            'key': 'CARET1_FG',
            'type': 'color',
            'fallback_key': 'TXT_FG',
            'display_name': _('Primary Caret Color'),
        },
        {
            'key': 'CARET2_FG',
            'type': 'color',
            'fallback_key': 'TXT_FG',
            'display_name': _('Secondary Caret Color'),
        },
        {
            'key': 'CARET_SIZE',
            'type': 'float',
            'fallback_value': 0.04,  # GTK's default
            'display_name': _('Caret Aspect Ratio'),
        },
        # ]

        # theme_model_extra = [
        {
            'type': 'separator',
            'display_name': _('Desktop Environments'),
            'value_filter': {
                'THEME_STYLE': 'oomox',
            },
        },
        {
            'key': 'CINNAMON_OPACITY',
            'type': 'float',
            'fallback_value': 1.0,
            'max_value': 1.0,
            'display_name': _('Cinnamon: Opacity'),
        },
        {
            'key': 'UNITY_DEFAULT_LAUNCHER_STYLE',
            'type': 'bool',
            'fallback_value': False,
            'display_name': _('Unity: Use Default Launcher Style'),
        },
    ]

    def preview_before_load_callback(self, preview_object, colorscheme):
        preview_object.WM_BORDER_WIDTH = 2
