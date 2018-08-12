import os
import gc

from oomox_gui.plugin_api import OomoxImportPlugin
from oomox_gui.config import TERMINAL_TEMPLATE_DIR
from oomox_gui.color import (
    hex_to_int, color_list_from_hex, color_hex_from_list,
    find_closest_color, hex_darker
)
from oomox_gui.terminal import (
    import_xcolors,
)
from oomox_gui.helpers import get_plugin_module
from oomox_gui.i18n import _


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))


LOW_QUALITY = 100
MEDIUM_QUALITY = 200
HIGH_QUALITY = 400
ULTRA_QUALITY = 1000


image_analyzer = get_plugin_module('ima', os.path.join(PLUGIN_DIR, 'ima.py'))  # pylint: disable=invalid-name


def sort_by_saturation(c):
    # pylint: disable=invalid-name
    return abs(c[0]-c[1])+abs(c[0]-c[2]) + \
        abs(c[1]-c[0])+abs(c[1]-c[2]) + \
        abs(c[2]-c[1])+abs(c[2]-c[0])


def get_gray_colors(palette):
    list_of_colors = [[hex_to_int(s) for s in color_list_from_hex(c)] for c in palette]
    saturation_list = sorted(
        list_of_colors,
        key=sort_by_saturation
    )
    gray_colors = saturation_list[:(len(saturation_list)//3)]
    gray_colors.sort(key=sum)
    gray_colors = [color_hex_from_list(c) for c in gray_colors]
    return gray_colors


class Plugin(OomoxImportPlugin):

    name = 'import_pil'
    display_name = 'PIL-based images import'
    file_extensions = (
        '.jpg',
        '.png',
        '.gif',
    )

    default_theme = {
        "TERMINAL_THEME_MODE": "manual",
        "TERMINAL_THEME_AUTO_BGFG": False,
    }
    default_themes = {
        "lcars": {
            "TERMINAL_THEME_MODE": "manual",
            "ROUNDNESS": 20,
            "ICONS_STYLE": "archdroid",
        }
    }
    translation_common = {
        "NAME": "scheme",

        "TERMINAL_COLOR0": "color0",
        "TERMINAL_COLOR1": "color1",
        "TERMINAL_COLOR2": "color2",
        "TERMINAL_COLOR3": "color3",
        "TERMINAL_COLOR4": "color4",
        "TERMINAL_COLOR5": "color5",
        "TERMINAL_COLOR6": "color6",
        "TERMINAL_COLOR7": "color7",
        "TERMINAL_COLOR8": "color8",
        "TERMINAL_COLOR9": "color9",
        "TERMINAL_COLOR10": "color10",
        "TERMINAL_COLOR11": "color11",
        "TERMINAL_COLOR12": "color12",
        "TERMINAL_COLOR13": "color13",
        "TERMINAL_COLOR14": "color14",
        "TERMINAL_COLOR15": "color15",

        "TERMINAL_BACKGROUND": "background",
        "TERMINAL_FOREGROUND": "foreground",
        "TERMINAL_ACCENT_COLOR": "color3",
    }
    theme_translations = {
        "1": {
            "BG": "color7",
            "FG": "color0",
            "TXT_BG": "foreground",
            "TXT_FG": "background",
            "SEL_BG": "color4",
            "SEL_FG": "color15",
            "MENU_BG": "background",
            "MENU_FG": "color7",
            "BTN_BG": "color8",
            "BTN_FG": "foreground",
            "HDR_BTN_BG": "background",
            "HDR_BTN_FG": "foreground",

            "ICONS_LIGHT_FOLDER": "color12",
            "ICONS_LIGHT": "color14",
            "ICONS_MEDIUM": "color6",
            "ICONS_DARK": "color4",
        },
        "2": {
            "BG": "color7",
            "FG": "color0",
            "TXT_BG": "foreground",
            "TXT_FG": "color0",
            "SEL_BG": "color1",
            "SEL_FG": "foreground",
            "MENU_BG": "background",
            "MENU_FG": "color7",
            "BTN_BG": "color12",
            "BTN_FG": "color0",
            "WM_BORDER_FOCUS": "color10",
            "ICONS_LIGHT_FOLDER": "color13",
            "ICONS_LIGHT": "color9",
            "ICONS_MEDIUM": "color1",
            "ICONS_DARK": "color5",
        },
        "3": {
            "BG": "color7",
            "FG": "color0",
            "TXT_BG": "foreground",
            "TXT_FG": "color0",
            "SEL_BG": "color3",
            "SEL_FG": "color0",
            "MENU_BG": "background",
            "MENU_FG": "color7",
            "BTN_BG": "color12",
            "BTN_FG": "color0",
            "WM_BORDER_FOCUS": "color3",
            "ICONS_LIGHT_FOLDER": "color13",
            "ICONS_LIGHT": "color9",
            "ICONS_MEDIUM": "color1",
            "ICONS_DARK": "color5",
        },
        "4": {
            "BG": "color5",
            "FG": "color0",
            "MENU_BG": "color4",
            "MENU_FG": "color1",
            "SEL_BG": "color4",
            "SEL_FG": "color0",
            "TXT_BG": "color6",
            "TXT_FG": "color1",
            "BTN_BG": "color3",
            "BTN_FG": "color0",
            "HDR_BTN_BG": "color5",
            "HDR_BTN_FG": "color1",
        },
        "lcars": {
            "BG": "background",
            "FG": "foreground",
            "TXT_BG": "background",
            "TXT_FG": "color11",
            "SEL_BG": "color1",
            "SEL_FG": "background",
            "MENU_BG": "background",
            "MENU_FG": "color7",
            "BTN_BG": "color10",
            "BTN_FG": "color0",
            "HDR_BTN_BG": "color12",
            "HDR_BTN_FG": "background",
            "WM_BORDER_FOCUS": "color10",
            "ICONS_ARCHDROID": "color12",
        },
    }

    theme_model_import = [
        {
            'display_name': _('Import colors from image: '),
            'type': 'separator',
            'value_filter': {
                'FROM_PLUGIN': ['import_pil']
            },
        },
        {
            'key': '_PIL_PALETTE_QUALITY',
            'type': 'options',
            'options': [{
                'value': LOW_QUALITY,
                'display_name': 'low',
            }, {
                'value': MEDIUM_QUALITY,
                'display_name': 'medium',
            }, {
                'value': HIGH_QUALITY,
                'display_name': 'high',
            }, {
                'value': ULTRA_QUALITY,
                'display_name': 'ultra',
            }],
            'fallback_value': LOW_QUALITY,
            'display_name': _('Image analysis quality'),
            'reload_theme': True,
        },
        {
            'key': '_PIL_PALETTE_STYLE',
            'type': 'options',
            'options': [
                {'value': template_name}
                for template_name in sorted(os.listdir(TERMINAL_TEMPLATE_DIR))
            ],
            'fallback_value': 'monovedek_pale_gray',
            'display_name': _('Palette style'),
            'reload_theme': True,
        },
        {
            'key': '_PIL_PALETTE_STRICT',
            'type': 'bool',
            'fallback_value': False,
            'display_name': _('Stronger follow palette template'),
            'reload_theme': True,
        },
        {
            'key': '_PIL_PALETTE_INVERSE',
            'type': 'bool',
            'fallback_value': False,
            'display_name': _('Dark/Light colors'),
            'reload_theme': True,
        },
        {
            'key': '_PIL_THEME_TEMPLATE',
            'type': 'options',
            'options': [
                {'value': template_name}
                for template_name in sorted(theme_translations.keys())
            ],
            'fallback_value': '1',
            'display_name': _('GUI theme template'),
            'reload_theme': True,
        },
        {
            'key': '_PIL_IMAGE_PREVIEW',
            'type': 'image_path',
            'fallback_value': None,
            'display_name': _('Image thumbnail'),
        },
        {
            'display_name': _('Theme options: '),
            'type': 'separator',
            'value_filter': {
                'FROM_PLUGIN': ['import_pil']
            },
        },
    ]

    def read_colorscheme_from_path(self, preset_path):
        from oomox_gui.theme_model import THEME_MODEL_BY_KEY

        THEME_MODEL_BY_KEY['_PIL_IMAGE_PREVIEW']['fallback_value'] = preset_path
        image_palette = self.generate_terminal_palette(
            THEME_MODEL_BY_KEY.get('_PIL_PALETTE_STYLE', {}).get('fallback_value'),
            preset_path
        )
        inverse_palette = bool(
            THEME_MODEL_BY_KEY.get('_PIL_PALETTE_INVERSE', {}).get('fallback_value')
        )

        theme_template = THEME_MODEL_BY_KEY.get('_PIL_THEME_TEMPLATE', {}).get('fallback_value')
        oomox_theme = {}
        oomox_theme.update(self.default_theme)
        if theme_template in self.default_themes:
            oomox_theme.update(self.default_themes[theme_template])
        translation = {}
        translation.update(self.translation_common)
        translation.update(
            self.theme_translations[theme_template]
        )
        for oomox_key, image_palette_key in translation.items():
            if image_palette_key in image_palette:
                oomox_theme[oomox_key] = image_palette[image_palette_key]

        if inverse_palette:
            oomox_theme['TERMINAL_FOREGROUND'], oomox_theme['TERMINAL_BACKGROUND'] = \
                oomox_theme['TERMINAL_BACKGROUND'], oomox_theme['TERMINAL_FOREGROUND']
        return oomox_theme

    _palette_cache = {}
    _terminal_palette_cache = {}

    @classmethod
    def get_image_palette(cls, image_path, quality, use_whole_palette):
        _id = image_path+str(quality)+str(use_whole_palette)
        if not cls._palette_cache.get(_id):
            cls._palette_cache[_id] = image_analyzer.get_hex_palette(
                image_path, quality=quality, use_whole_palette=use_whole_palette
            )
        return cls._palette_cache[_id]

    @classmethod
    def _generate_terminal_palette(cls, template_path, image_path, quality, use_whole_palette):
        hex_palette = cls.get_image_palette(image_path, quality, use_whole_palette)[:]
        gray_colors = get_gray_colors(hex_palette)
        ACCURACY = 40  # pylint: disable=invalid-name
        hex_palette += [hex_darker(c, ACCURACY) for c in gray_colors]
        hex_palette += [hex_darker(c, -ACCURACY) for c in gray_colors]
        reference_palette = import_xcolors(os.path.join(TERMINAL_TEMPLATE_DIR, template_path))
        result_palette = {}
        for key, value in reference_palette.items():
            closest_color, _diff = find_closest_color(value, hex_palette)
            result_palette[key] = closest_color
        gc.collect()
        return result_palette

    @classmethod
    def generate_terminal_palette(cls, template_path, image_path):
        from oomox_gui.theme_model import THEME_MODEL_BY_KEY
        quality = int(
            THEME_MODEL_BY_KEY.get('_PIL_PALETTE_QUALITY', {}).get('fallback_value')
        )
        use_whole_palette = bool(
            THEME_MODEL_BY_KEY.get('_PIL_PALETTE_STRICT', {}).get('fallback_value')
        )
        _id = template_path+image_path+str(quality)+str(use_whole_palette)
        if not cls._terminal_palette_cache.get(_id):
            cls._terminal_palette_cache[_id] = cls._generate_terminal_palette(
                template_path, image_path, quality, use_whole_palette
            )
        palette = {}
        palette.update(cls._terminal_palette_cache[_id])
        return palette
