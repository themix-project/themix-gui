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
    description = (
        'GTK+2, GTK+3\n'
        'Cinnamon, GNOME Shell, Metacity, Unity, Xfwm'
    )
    export_dialog = MateriaThemeExportDialog
    gtk_preview_dir = os.path.join(PLUGIN_DIR, "gtk_preview_css/")
    preview_sizes = {
        OomoxThemePlugin.PreviewImageboxesNames.CHECKBOX.name: 24,
    }

    enabled_keys_gtk = [
        'BG',
        'FG',
        'HDR_BG',
        'HDR_FG',
        'SEL_BG',
    ]
    enabled_keys_options = [
        'ROUNDNESS',
    ]

    theme_model_gtk = [
        {
            'key': 'MATERIA_VIEW',
            'type': 'color',
            'fallback_key': 'TXT_BG',
            'display_name': _('View'),
        },
        {
            'key': 'MATERIA_SURFACE',
            'type': 'color',
            'fallback_key': 'BTN_BG',
            'display_name': _('Surface (like Button, Menu, Popover)'),
        },
    ]

    theme_model_options = [
        {
            'key': 'MATERIA_SELECTION_OPACITY',
            'type': 'float',
            'fallback_value': 0.32,
            'max_value': 1.0,
            'display_name': _('Selection Opacity'),
        },
        {
            'key': 'MATERIA_PANEL_OPACITY',
            'type': 'float',
            'fallback_value': 0.6,
            'max_value': 1.0,
            'display_name': _('DE Panel Opacity'),
        },
        {
            'key': 'MATERIA_STYLE_COMPACT',
            'type': 'bool',
            'fallback_value': True,
            'display_name': _('Compact Style'),
        },
    ]

    def preview_before_load_callback(self, preview_object, colorscheme):
        colorscheme["TXT_FG"] = colorscheme["FG"]
        colorscheme["WM_BORDER_FOCUS"] = colorscheme["HDR_BG"]
        colorscheme["WM_BORDER_UNFOCUS"] = colorscheme["MATERIA_SURFACE"]
        colorscheme["HDR_BTN_FG"] = colorscheme["HDR_FG"]
        colorscheme["HDR_BTN_BG"] = colorscheme["HDR_BG"]
        colorscheme["SEL_FG"] = colorscheme["FG"]
        colorscheme["ACCENT_BG"] = colorscheme["SEL_BG"]
        colorscheme["BTN_FG"] = colorscheme["FG"]
        colorscheme["BTN_BG"] = colorscheme["MATERIA_SURFACE"]
        colorscheme["TXT_BG"] = colorscheme["MATERIA_VIEW"]
        colorscheme["GRADIENT"] = 0
        preview_object.WM_BORDER_WIDTH = 0
        _monkeypatch_update_preview_colors(preview_object)
