import os

from .theme_model import THEME_MODEL
from .xrdb import XrdbCache
from .plugin_loader import IMPORT_PLUGINS


def str_to_bool(value):
    return value.lower() == 'true'


def parse_theme_color_value(result_value):
    if not result_value:
        return None
    if result_value.startswith('xrdb.'):
        xrdb_color = XrdbCache.get().get(result_value.replace('xrdb.', ''))
        if xrdb_color and xrdb_color.startswith('#'):
            result_value = xrdb_color.replace('#', '')
    return result_value


def parse_theme_value(theme_value, colorscheme):  # pylint: disable=too-many-branches
    result_value = colorscheme.get(theme_value['key'])
    fallback_key = theme_value.get('fallback_key')
    fallback_value = theme_value.get('fallback_value')
    fallback_function = theme_value.get('fallback_function')

    if result_value is None:
        if fallback_value is not None:
            result_value = fallback_value
        elif fallback_key:
            result_value = colorscheme[fallback_key]
        elif fallback_function:
            result_value = fallback_function(colorscheme)

    value_type = theme_value['type']
    if value_type == 'color':
        result_value = parse_theme_color_value(result_value)
    if value_type == 'bool':
        if isinstance(result_value, str):
            result_value = str_to_bool(result_value)
    elif value_type == 'int':
        result_value = int(result_value)
    elif value_type == 'float':
        result_value = float(result_value)
    elif value_type == 'options':
        available_options = [option['value'] for option in theme_value['options']]
        if result_value not in available_options:
            if fallback_value in available_options:
                result_value = fallback_value
            else:
                result_value = available_options[0]

    return result_value


def read_colorscheme_from_path(preset_path):
    preset_path = os.path.abspath(preset_path)
    colorscheme = {}
    from_plugin = None

    for plugin_name, plugin in IMPORT_PLUGINS.items():
        if preset_path.startswith(plugin.user_theme_dir) or (
                plugin.plugin_theme_dir and (
                    preset_path.startswith(plugin.plugin_theme_dir)
                )
        ):
            colorscheme = plugin.read_colorscheme_from_path(preset_path)
            from_plugin = plugin_name
            break

    if not colorscheme:
        theme_keys = [item['key'] for item in THEME_MODEL if 'key' in item]

        theme_keys.append('NOGUI')

        with open(preset_path) as file_object:
            for line in file_object.readlines():
                key, _sep, value = line.strip().partition('=')
                if key.startswith("#") or key not in theme_keys:
                    continue
                colorscheme[key] = value

    for theme_model_item in THEME_MODEL:
        key = theme_model_item.get('key')
        if not key:
            continue
        colorscheme[key] = parse_theme_value(theme_model_item, colorscheme)
    if from_plugin:
        colorscheme['FROM_PLUGIN'] = from_plugin

    XrdbCache.clear()
    return colorscheme
