import os

from gi.repository import Gtk

from oomox_gui.export_common import OPTION_GTK2_HIDPI, GtkThemeExportDialog
from oomox_gui.plugin_api import OomoxThemePlugin


OPTION_GTK3_CURRENT_VERSION_ONLY = 'OPTION_GTK3_CURRENT_VERSION_ONLY'
OPTION_EXPORT_CINNAMON_THEME = 'OPTION_EXPORT_CINNAMON_THEME'


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
GTK_THEME_DIR = os.path.join(PLUGIN_DIR, "gtk-theme/")


class OomoxThemeExportDialog(GtkThemeExportDialog):
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
        # if self.export_config[OPTION_EXPORT_CINNAMON_THEME]:
            # make_opts += ["css_cinnamon"]
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
                    'display_name': _("Generate theme only for the current _GTK+3 version"),
                },
                # OPTION_EXPORT_CINNAMON_THEME: {
                    # 'default': False,
                    # 'display_name': _("Generate theme for _Cinnamon"),
                # },
            },
            **kwargs
        )


class Plugin(OomoxThemePlugin):

    name = 'oomox'
    display_name = 'Numix-based'
    description = '(GTK+2, GTK+3, Metacity, Openbox, Qt5ct, Unity, Xfwm)'
    export_dialog = OomoxThemeExportDialog
    gtk_preview_css_dir = os.path.join(PLUGIN_DIR, "gtk_preview_css/")

    enabled_keys_gtk = [
        'BG',
        'FG',
        'MENU_BG',
        'MENU_FG',
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
            'key': 'OUTLINE_WIDTH',
            'type': 'int',
            'fallback_value': 1,
            'display_name': _('(GTK3) Focused outline width'),
        },
        {
            'key': 'BTN_OUTLINE_WIDTH',
            'type': 'int',
            'fallback_value': 1,
            'display_name': _('(GTK3) Focused button outline width'),
        },
        {
            'key': 'BTN_OUTLINE_OFFSET',
            'type': 'int',
            'fallback_value': -3,
            'min_value': -20,
            'display_name': _('(GTK3) Focused button outline offset'),
        },
    ]

    theme_model_other = [
        {
            'key': 'UNITY_DEFAULT_LAUNCHER_STYLE',
            'type': 'bool',
            'fallback_value': False,
            'display_name': _('(Unity) Use default launcher style'),
        },
    ]

    theme_model_extra = [
    ]

    def preview_before_load_callback(self, preview_object, colorscheme):
        preview_object.WM_BORDER_WIDTH = 2
