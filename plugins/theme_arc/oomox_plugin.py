import os
from typing import TYPE_CHECKING

from gi.repository import Gtk

from oomox_gui.color import mix_theme_colors
from oomox_gui.export_common import ExportDialogWithOptions
from oomox_gui.i18n import translate

# from oomox_gui.export_common import OPTION_GTK2_HIDPI
from oomox_gui.plugin_api import OomoxThemePlugin

if TYPE_CHECKING:
    from typing import Any, Final

    from oomox_gui.preview import ThemePreview
    from oomox_gui.theme_file import ThemeT


PLUGIN_DIR: "Final" = os.path.dirname(os.path.realpath(__file__))
THEME_DIR: "Final" = os.path.join(PLUGIN_DIR, "arc-theme/")

OPTION_EXPORT_CINNAMON_THEME: "Final" = "OPTION_EXPORT_CINNAMON_THEME"
OPTION_EXPORT_GNOME_SHELL_THEME: "Final" = "OPTION_EXPORT_GNOME_SHELL_THEME"
OPTION_EXPORT_XFWM_THEME: "Final" = "OPTION_EXPORT_XFWM_THEME"


class ArcThemeExportDialog(ExportDialogWithOptions):

    config_name = "arc_theme"
    timeout = 1000

    def do_export(self) -> None:
        self.command = [
            "bash",
            os.path.join(THEME_DIR, "change_color.sh"),
            # "--hidpi", str(self.export_config[OPTION_GTK2_HIDPI]),
            "--output", self.theme_name,
            self.temp_theme_path,
        ]
        autogen_opts = []
        if not self.export_config[OPTION_EXPORT_CINNAMON_THEME]:
            autogen_opts += ["--disable-cinnamon"]
        if not self.export_config[OPTION_EXPORT_GNOME_SHELL_THEME]:
            autogen_opts += ["--disable-gnome-shell"]
        if not self.export_config[OPTION_EXPORT_XFWM_THEME]:
            autogen_opts += ["--disable-xfwm"]
        if autogen_opts:
            self.command += [
                "--autogen-opts", " ".join(autogen_opts),
            ]
        super().do_export()

    def __init__(
            self,
            transient_for: Gtk.Window,
            colorscheme: "ThemeT",
            theme_name: str,
            **kwargs: "Any",
    ) -> None:
        super().__init__(
            transient_for=transient_for,
            colorscheme=colorscheme,
            theme_name=theme_name,
            override_options={
                OPTION_EXPORT_CINNAMON_THEME: {
                    "default": False,
                    "display_name": translate("Generate theme for _Cinnamon"),
                },
                OPTION_EXPORT_GNOME_SHELL_THEME: {
                    "default": False,
                    "display_name": translate("Generate theme for GNOME _Shell"),
                },
                OPTION_EXPORT_XFWM_THEME: {
                    "default": False,
                    "display_name": translate("Generate theme for _Xfwm"),
                },
            },
            **kwargs,
        )


def _monkeypatch_update_preview_borders(preview_object: "ThemePreview") -> None:
    _monkeypatch_id = "_arc_borders_monkeypatched"

    if getattr(preview_object, _monkeypatch_id, None):
        return

    old_update_preview_borders = preview_object.update_preview_borders

    def _update_preview_borders(colorscheme: "ThemeT") -> None:
        if colorscheme["THEME_STYLE"] != "arc":
            old_update_preview_borders(colorscheme)
        else:
            for widget_name, widget, border_color in (
                    (
                        "button",
                        preview_object.gtk_preview.button,
                        colorscheme["ARC_WIDGET_BORDER_COLOR"],
                    ), (
                        "headerbar_button",
                        preview_object.gtk_preview.headerbar.button,
                        mix_theme_colors(
                            colorscheme["HDR_BTN_FG"],
                            colorscheme["HDR_BTN_BG"],
                            0.12,
                        ),
                    ), (
                        "entry",
                        preview_object.gtk_preview.entry,
                        colorscheme["ARC_WIDGET_BORDER_COLOR"],
                    ),
            ):
                css_provider_border_color = preview_object.css_providers.border.get(widget_name)
                if not css_provider_border_color:
                    css_provider_border_color = \
                        preview_object.css_providers.border[widget_name] = \
                        Gtk.CssProvider()
                css_provider_border_color.load_from_data(
                    f"""
                    * {{
                        border-color: #{border_color};
                        border-radius: {colorscheme["ROUNDNESS"]}px;
                    }}
                    """.encode("ascii"),
                )
                Gtk.StyleContext.add_provider(
                    widget.get_style_context(),
                    css_provider_border_color,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
                )

    preview_object.update_preview_borders = _update_preview_borders
    setattr(preview_object, _monkeypatch_id, True)


class Plugin(OomoxThemePlugin):

    name = "arc"
    display_name = "Arc"
    description = (
        "GTK+2, GTK+3\n"
        "Cinnamon, GNOME Shell, Metacity, Openbox, Unity, Xfwm"
    )
    about_links = [
        {
            "name": translate("Homepage"),
            "url": "https://github.com/arc-design/arc-theme",
        },
    ]

    export_dialog = ArcThemeExportDialog
    gtk_preview_dir = os.path.join(PLUGIN_DIR, "gtk_preview_css/")
    preview_sizes = {
        OomoxThemePlugin.PreviewImageboxesNames.CHECKBOX.name: 16,
    }

    enabled_keys_gtk = [
        "BG",
        "FG",
        "HDR_BG",
        "HDR_FG",
        "SEL_BG",
        "SEL_FG",
        "TXT_BG",
        "BTN_BG",
        "HDR_BTN_BG",
        "ACCENT_BG",
    ]
    # enabled_keys_options = [
    #     'ROUNDNESS',
    # ]

    theme_model_gtk = [
        {
            "key": "ARC_WIDGET_BORDER_COLOR",
            "fallback_function": lambda colors: mix_theme_colors(
                colors["BTN_BG"], colors["BTN_FG"],
                0.75,
            ),
            "type": "color",
            "display_name": translate("Border"),
            "description": translate("not supported by GTK+2 theme"),
        },
    ]

    theme_model_options = [
        {
            "key": "ARC_TRANSPARENCY",
            "type": "bool",
            "fallback_value": True,
            "display_name": translate("Enable Theme Transparency"),
            "description": translate("not supported by GTK+2 theme"),
        },
        # {
        #     'key': 'GTK3_GENERATE_DARK',
        #     'type': 'bool',
        #     'fallback_value': True,
        #     'display_name': translate('(GTK3) Add Dark Variant'),
        # },
    ]

    def preview_before_load_callback(
            self, preview_object: "ThemePreview", colorscheme: "ThemeT",
    ) -> None:
        colorscheme["TXT_FG"] = colorscheme["FG"]
        colorscheme["BTN_FG"] = colorscheme["FG"]
        colorscheme["HDR_BTN_FG"] = colorscheme["HDR_FG"]
        colorscheme["WM_BORDER_FOCUS"] = colorscheme["HDR_BG"]
        colorscheme["WM_BORDER_UNFOCUS"] = colorscheme["BTN_BG"]
        colorscheme["GRADIENT"] = 0
        colorscheme["ROUNDNESS"] = 0
        preview_object.WM_BORDER_WIDTH = 0
        _monkeypatch_update_preview_borders(preview_object)
