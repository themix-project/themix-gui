from .theme_model import THEME_MODEL
from .color import get_random_theme_color
from .xrdb import XrdbCache
from .plugin_loader import theme_format_plugins


def str_to_bool(value):
    return value.lower() == 'true'


def parse_theme_color_value(result_value):
    if not result_value:
        return None
    if result_value == 'random_color':
        result_value = get_random_theme_color()
    elif result_value.startswith('xrdb.'):
        xrdb_color = XrdbCache.get().get(result_value.replace('xrdb.', ''))
        if xrdb_color and xrdb_color.startswith('#'):
            result_value = xrdb_color.replace('#', '')
    return result_value


def parse_theme_value(theme_value, colorscheme):
    result_value = colorscheme.get(theme_value['key'])
    fallback_key = theme_value.get('fallback_key')
    fallback_value = theme_value.get('fallback_value')

    if result_value is None and (fallback_key or fallback_value is not None):
        if fallback_value is not None:
            result_value = fallback_value
        else:
            result_value = colorscheme[fallback_key]

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
    colorscheme = {}

    from_plugin = None
    for plugin_name, plugin in theme_format_plugins.items():
        if preset_path.endswith(plugin.file_extension):
            colorscheme = plugin.read_colorscheme_from_path(preset_path)
            from_plugin = plugin_name
            break
    if not colorscheme:
        theme_keys = [item['key'] for item in THEME_MODEL if 'key' in item]

        theme_keys.append('NOGUI')

        with open(preset_path) as file_object:
            for line in file_object.readlines():
                parsed_line = line.strip().split('=')
                key = parsed_line[0]
                if not key.startswith("#"):
                    if key in theme_keys and len(parsed_line) > 1:
                        colorscheme[key] = parsed_line[1]

    for theme_model_item in THEME_MODEL:
        key = theme_model_item.get('key')
        if not key:
            continue
        colorscheme[key] = parse_theme_value(theme_model_item, colorscheme)
    if from_plugin:
        colorscheme['FROM_PLUGIN'] = from_plugin

    XrdbCache.clear()
    return colorscheme
