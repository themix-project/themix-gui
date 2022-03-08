import os
from typing import Dict, Union, Callable

from .i18n import translate
from .theme_model import get_theme_model
from .plugin_loader import PluginLoader
from .config import DEFAULT_ENCODING


ColorScheme = Dict[str, Union[str, bool, int, float]]


class NoPluginsInstalled(Exception):

    def __init__(self, theme_value):
        self.theme_value = theme_value
        super().__init__(
            translate("No plugins installed for {plugin_type}").format(
                plugin_type=self.theme_value['display_name']
            )
        )


def str_to_bool(value):
    return value.lower() == 'true'


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
                if not available_options:
                    raise NoPluginsInstalled(theme_value)
                result_value = available_options[0]

    return result_value


def _set_fallback_values(preset_path, colorscheme, from_plugin):
    if not colorscheme:
        theme_keys = [
            item['key']
            for section in get_theme_model().values()
            for item in section
            if 'key' in item
        ]

        theme_keys.append('NOGUI')

        with open(preset_path, encoding=DEFAULT_ENCODING) as file_object:
            for line in file_object.readlines():
                key, _sep, value = line.strip().partition('=')
                if key.startswith("#") or key not in theme_keys:
                    continue
                colorscheme[key] = value

    for section in get_theme_model().values():  # @TODO: store theme in memory also in two levels?
        for theme_model_item in section:
            key = theme_model_item.get('key')
            if not key:
                continue
            try:
                colorscheme[key] = parse_theme_value(theme_model_item, colorscheme)
            except NoPluginsInstalled as exc:
                colorscheme[key] = exc
    if from_plugin:
        colorscheme['FROM_PLUGIN'] = from_plugin


def read_colorscheme_from_path(
        preset_path: str,
        callback: Callable[[ColorScheme, ], None]
) -> None:
    preset_path = os.path.abspath(preset_path)
    colorscheme = {}
    from_plugin = None

    for plugin_name, plugin in PluginLoader.get_import_plugins().items():
        if preset_path.startswith(plugin.user_theme_dir) or (
                plugin.plugin_theme_dir and (
                    preset_path.startswith(plugin.plugin_theme_dir)
                )
        ):
            from_plugin = plugin_name
            if plugin.is_async:
                def actual_callback(_colorscheme):
                    _set_fallback_values(preset_path, _colorscheme, from_plugin)
                    callback(_colorscheme)
                plugin.read_colorscheme_from_path(preset_path, callback=actual_callback)
                return
            colorscheme = plugin.read_colorscheme_from_path(preset_path)
            break

    _set_fallback_values(preset_path, colorscheme, from_plugin)
    callback(colorscheme)
    return  # <-- this is quite stupid from pylint's side to ask for this
