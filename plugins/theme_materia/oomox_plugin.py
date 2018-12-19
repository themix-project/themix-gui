import os

from oomox_gui.i18n import _
from oomox_gui.plugin_api import OomoxThemePlugin
from oomox_gui.export_common import GtkThemeExportDialog, OPTION_GTK2_HIDPI
from oomox_gui.color import convert_theme_color_to_gdk, mix_theme_colors


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


def _monkeypatch_update_preview_colors(preview_object):
    _monkeypatch_id = '_materia_update_colors_monkeypatched'

    if getattr(preview_object, _monkeypatch_id, None):
        return

    old_update_preview_colors = preview_object.update_preview_colors

    def _update_preview_colors(colorscheme):
        old_update_preview_colors(colorscheme)
        if colorscheme["THEME_STYLE"] == "materia":
            preview_object.override_widget_color(
                preview_object.gtk_preview.sel_label, preview_object.BG,
                convert_theme_color_to_gdk(
                    mix_theme_colors(
                        colorscheme["SEL_BG"],
                        colorscheme["BG"],
                        colorscheme["MATERIA_SELECTION_OPACITY"]
                    )
                )
            )
            preview_object.override_widget_color(
                preview_object.gtk_preview.entry, preview_object.BG,
                convert_theme_color_to_gdk(
                    mix_theme_colors(
                        colorscheme["FG"],
                        colorscheme["BG"],
                        0.04
                    )
                )
            )

    preview_object.update_preview_colors = _update_preview_colors
    setattr(preview_object, _monkeypatch_id, True)


class Plugin(OomoxThemePlugin):

    name = 'materia'
    display_name = 'Materia'
    description = '(GTK+2, GTK+3, Cinnamon, Gnome Shell, Metacity, Unity, Xfwm)'
    export_dialog = MateriaThemeExportDialog
    gtk_preview_dir = os.path.join(PLUGIN_DIR, "gtk_preview_css/")
    preview_sizes = {
        OomoxThemePlugin.PreviewImageboxesNames.CHECKBOX.name: 24,
    }

    enabled_keys_gtk = [
        'BG',
        'FG',
        'BTN_BG',
        'TXT_BG',
        'MENU_BG',
        'MENU_FG',
        'SEL_BG',
    ]
    enabled_keys_options = [
        'ROUNDNESS',
    ]

    theme_model_gtk = []

    theme_model_options = [
        {
            'key': 'MATERIA_SELECTION_OPACITY',
            'type': 'float',
            'fallback_value': 0.32,
            'max_value': 1.0,
            'display_name': _('Selection Opacity'),
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
        colorscheme["SEL_FG"] = colorscheme["FG"]
        colorscheme["ACCENT_BG"] = colorscheme["SEL_BG"]
        colorscheme["BTN_FG"] = colorscheme["FG"]
        colorscheme["GRADIENT"] = 0
        preview_object.WM_BORDER_WIDTH = 0
        _monkeypatch_update_preview_colors(preview_object)
