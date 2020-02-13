import os

from oomox_gui.i18n import _
from oomox_gui.plugin_api import OomoxThemePlugin
from oomox_gui.export_common import CommonGtkThemeExportDialog, OPTION_GTK2_HIDPI
from oomox_gui.color import convert_theme_color_to_gdk, mix_theme_colors

OPTION_DEFAULT_PATH = 'default_path'

PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
THEME_DIR = os.path.join(PLUGIN_DIR, "materia-theme/")


class MateriaThemeExportDialog(CommonGtkThemeExportDialog):

    config_name = 'materia_theme'
    timeout = 1000

    def do_export(self):
        export_path = self.option_widgets[OPTION_DEFAULT_PATH].get_text()
        new_destination_dir, theme_name = export_path.rsplit('/', 1)
        self.command = [
            "bash",
            os.path.join(THEME_DIR, "change_color.sh"),
            "--hidpi", str(self.export_config[OPTION_GTK2_HIDPI]),
            "--target", new_destination_dir,
            "--output", theme_name,
            self.temp_theme_path,
        ]
        super().do_export()
        self.export_config[OPTION_DEFAULT_PATH] = new_destination_dir
        self.export_config.save()

    def __init__(self, transient_for, colorscheme, theme_name, **kwargs):
        default_themes_path = os.path.join(os.environ['HOME'], '.themes')
        super().__init__(
            transient_for=transient_for,
            colorscheme=colorscheme,
            theme_name=theme_name,
            add_options={
                OPTION_DEFAULT_PATH: {
                    'default': default_themes_path,
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
            'key': 'TXT_BG',
            'type': 'color',
            'fallback_key': 'BG',
            'display_name': _('View'),
        },
        {
            'key': 'BTN_BG',
            'type': 'color',
            'fallback_key': 'BG',
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
        colorscheme["WM_BORDER_UNFOCUS"] = colorscheme["BTN_BG"]
        colorscheme["HDR_BTN_FG"] = colorscheme["HDR_FG"]
        colorscheme["HDR_BTN_BG"] = colorscheme["HDR_BG"]
        colorscheme["SEL_FG"] = colorscheme["FG"]
        colorscheme["ACCENT_BG"] = colorscheme["SEL_BG"]
        colorscheme["BTN_FG"] = colorscheme["FG"]
        colorscheme["GRADIENT"] = 0
        preview_object.WM_BORDER_WIDTH = 0
        _monkeypatch_update_preview_colors(preview_object)
