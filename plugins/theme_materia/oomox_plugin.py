import os

from oomox_gui.export_common import GtkThemeExportDialog, OPTION_GTK2_HIDPI
from oomox_gui.plugin_api import OomoxThemePlugin


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
THEME_DIR = os.path.join(PLUGIN_DIR, "materia-theme/")


class MateriaThemeExportDialog(GtkThemeExportDialog):
    timeout = 1000

    def do_export(self):
        self.command = [
            "bash",
            os.path.join(THEME_DIR, "change_color.sh"),
            "--hidpi", str(self.export_config[OPTION_GTK2_HIDPI]),
            "--output", self.theme_name,
            self.temp_theme_path,
        ]
        super().do_export()


class Plugin(OomoxThemePlugin):

    name = 'materia'
    display_name = 'Materia'
    description = '(GTK+2, GTK+3, Gnome Shell, Metacity, Unity, Xfwm)'
    export_dialog = MateriaThemeExportDialog
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
        'BTN_BG',
        'BTN_FG',
    ]

    theme_model_gtk = []

    theme_model_options = [
        {
            'key': 'GTK3_GENERATE_DARK',
            'type': 'bool',
            'fallback_value': True,
            'display_name': _('(GTK3) Add dark variant'),
        },
        {
            'key': 'MATERIA_STYLE_COMPACT',
            'type': 'bool',
            'fallback_value': True,
            'display_name': _('Compact style'),
        },
    ]

    theme_model_other = [
        {
            'key': 'GNOME_SHELL_PANEL_OPACITY',
            'type': 'float',
            'fallback_value': 0.6,
            'max_value': 1.0,
            'display_name': _('(Gnome Shell) Panel opacity'),
        },
    ]

    def preview_before_load_callback(self, preview_object, colorscheme):
        colorscheme["TXT_FG"] = colorscheme["FG"]
        colorscheme["WM_BORDER_FOCUS"] = colorscheme["MENU_BG"]
        colorscheme["WM_BORDER_UNFOCUS"] = colorscheme["BTN_BG"]
        colorscheme["HDR_BTN_FG"] = colorscheme["MENU_FG"]
        colorscheme["HDR_BTN_BG"] = colorscheme["MENU_BG"]
        colorscheme["ROUNDNESS"] = 0
        colorscheme["GRADIENT"] = 0
        preview_object.WM_BORDER_WIDTH = 0
