import os

from oomox_gui.plugin_api import OomoxThemeFormatPlugin


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))


class Plugin(OomoxThemeFormatPlugin):

    name = 'format_base16'
    display_name = 'Base16 YML format import'
    file_extension = '.yml'

    theme_model_gtk = [
        {
            'key': 'BASE16_GENERATE_DARK',
            'type': 'bool',
            'fallback_value': False,
            'display_name': _('Generate dark Base16 variant'),
            'reload_theme': True,
        },
    ]

    default_theme = {
        "TERMINAL_THEME_MODE": "manual",
    }
    translation_common = {
        "NAME": "scheme",

        "TERMINAL_COLOR0": "base00",
        "TERMINAL_COLOR1": "base08",
        "TERMINAL_COLOR2": "base0b",
        "TERMINAL_COLOR3": "base09",
        "TERMINAL_COLOR4": "base0d",
        "TERMINAL_COLOR5": "base0e",
        "TERMINAL_COLOR6": "base0c",
        "TERMINAL_COLOR7": "base05",
        "TERMINAL_COLOR8": "base02",
        "TERMINAL_COLOR9": "base08",  # @TODO: lighter
        "TERMINAL_COLOR10": "base0b",  # @TODO: lighter
        "TERMINAL_COLOR11": "base0a",
        "TERMINAL_COLOR12": "base0d",  # @TODO: lighter
        "TERMINAL_COLOR13": "base0e",  # @TODO: lighter
        "TERMINAL_COLOR14": "base0c",  # @TODO: lighter
        "TERMINAL_COLOR15": "base07",

        "ICONS_LIGHT_FOLDER": "base0c",
        "ICONS_LIGHT": "base0c",
        "ICONS_MEDIUM": "base0d",
        "ICONS_DARK": "base03",
    }
    translation_light = {
        "BG": "base05",
        "FG": "base00",
        "MENU_BG": "base04",
        "MENU_FG": "base01",
        "SEL_BG": "base0d",
        "SEL_FG": "base00",
        "TXT_BG": "base06",
        "TXT_FG": "base01",
        "BTN_BG": "base03",
        "BTN_FG": "base07",
        "HDR_BTN_BG": "base05",
        "HDR_BTN_FG": "base01",

        "TERMINAL_BACKGROUND": "base01",
        "TERMINAL_FOREGROUND": "base06",
        "TERMINAL_ACCENT_COLOR": "base0d",
    }
    translation_dark = {
        "BG": "base01",
        "FG": "base06",
        "MENU_BG": "base00",
        "MENU_FG": "base05",
        "SEL_BG": "base08",
        "SEL_FG": "base00",
        "TXT_BG": "base02",
        "TXT_FG": "base07",
        "BTN_BG": "base00",
        "BTN_FG": "base05",
        "HDR_BTN_BG": "base01",
        "HDR_BTN_FG": "base05",

        "TERMINAL_COLOR8": "base01",
        "TERMINAL_BACKGROUND": "base02",
        "TERMINAL_FOREGROUND": "base07",
        "TERMINAL_ACCENT_COLOR": "base08",
    }

    def read_colorscheme_from_path(self, preset_path):
        from oomox_gui.theme_model import THEME_MODEL_BY_KEY

        base16_theme = {}
        with open(preset_path) as f:
            for line in f.readlines():
                try:
                    key, value, *rest = line.split()
                    key = key.rstrip(':').lower()
                    value = value.strip('\'"').lower()
                    base16_theme[key] = value
                except Exception:
                    pass

        oomox_theme = {}
        oomox_theme.update(self.default_theme)
        translation = {}
        translation.update(self.translation_common)
        if THEME_MODEL_BY_KEY.get('BASE16_GENERATE_DARK', {}).get('fallback_value'):
            translation.update(self.translation_dark)
        else:
            translation.update(self.translation_light)
        for oomox_key, base16_key in translation.items():
            if base16_key in base16_theme:
                oomox_theme[oomox_key] = base16_theme[base16_key]
        return oomox_theme
