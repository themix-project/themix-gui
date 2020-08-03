import os
import random

from gi.repository import Gdk

from oomox_gui.plugin_api import OomoxImportPlugin
from oomox_gui.color import convert_gdk_to_theme_color


PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))


def get_random_gdk_color():
    return Gdk.RGBA(random.random(), random.random(), random.random(), 1)


def get_random_theme_color():
    return convert_gdk_to_theme_color(get_random_gdk_color())


class ColorRandomizator():

    def __init__(self):
        self.colors = {}

    def get_theme_color_by_id(self, random_id):
        color = self.colors.get(random_id)
        if not color:
            color = self.colors[random_id] = get_random_theme_color()
        return color


class Plugin(OomoxImportPlugin):

    name = 'import_random'
    display_name = 'Random'
    plugin_theme_dir = os.path.abspath(
        os.path.join(PLUGIN_DIR, 'colors')
    )

    theme_model_import = [
        # {
        #     'display_name': _('Generate Random Colortheme:'),
        #     'type': 'separator',
        #     'value_filter': {
        #         'FROM_PLUGIN': 'import_random',
        #     },
        # },
        # {
        #     'key': 'BASE16_GENERATE_DARK',
        #     'type': 'bool',
        #     'fallback_value': False,
        #     'display_name': _('Generate Dark GUI Variant'),
        #     'reload_theme': True,
        # },
    ]

    def read_colorscheme_from_path(self, preset_path):
        # pylint:disable=bad-option-value,import-outside-toplevel
        from oomox_gui.theme_model import THEME_MODEL

        theme_keys = [
            item['key']
            for section in THEME_MODEL.values()
            for item in section
            if 'key' in item
        ]

        colorscheme = {}

        randomizator = ColorRandomizator()

        with open(preset_path) as file_object:
            for line in file_object.readlines():
                key, _sep, value = line.strip().partition('=')
                if key.startswith("#") or key not in theme_keys:
                    continue
                if value == 'random_color':
                    value = get_random_theme_color()
                elif value.startswith('random_color'):
                    _, _, random_id = value.partition('random_color')
                    value = randomizator.get_theme_color_by_id(random_id)
                colorscheme[key] = value

        return colorscheme
