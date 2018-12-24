import os

from oomox_gui.plugin_api import OomoxImportPlugin
from oomox_gui.i18n import _


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))


class Plugin(OomoxImportPlugin):

    name = 'import_base16'
    display_name = 'Base16'
    import_text = 'From Base16 YML Format'
    file_extensions = ('.yml', )
    plugin_theme_dir = os.path.abspath(
        os.path.join(PLUGIN_DIR, 'base16-data/db/schemes')
    )

    theme_model_import = [
        {
            'display_name': _('Base16 Import Options'),
            'type': 'separator',
            'value_filter': {
                'FROM_PLUGIN': 'import_base16',
            },
        },
        {
            'key': 'BASE16_GENERATE_DARK',
            'type': 'bool',
            'fallback_value': False,
            'display_name': _('Generate Dark GUI Variant'),
            'reload_theme': True,
        },
        {
            'display_name': _('Edit Imported Theme'),
            'type': 'separator',
            'value_filter': {
                'FROM_PLUGIN': 'import_base16',
            },
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
        "HDR_BG": "base04",
        "HDR_FG": "base01",
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
        "HDR_BG": "base00",
        "HDR_FG": "base05",
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
        with open(preset_path) as preset_file:
            for line in preset_file.readlines():
                try:
                    key, value, *_rest = line.split()
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
