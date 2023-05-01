import os
from typing import TYPE_CHECKING

from .config import DEFAULT_ENCODING
from .i18n import translate
from .plugin_loader import PluginLoader
from .theme_model import get_theme_model

if TYPE_CHECKING:
    from collections.abc import Callable

    from .theme_file import ThemeT, ThemeValueT
    from .theme_model import ThemeModelValue


class NoPluginsInstalledError(Exception):

    def __init__(self, theme_value: "ThemeModelValue") -> None:
        self.theme_value = theme_value
        super().__init__(
            translate("No plugins installed for {plugin_type}").format(
                plugin_type=self.theme_value["display_name"],
            ),
        )


def str_to_bool(value: str) -> bool:
    return value.lower() == "true"


def parse_theme_value(
        theme_value: "ThemeModelValue",
        colorscheme: "ThemeT",
) -> "ThemeValueT":
    result_value: "ThemeValueT | None" = colorscheme.get(theme_value["key"])
    fallback_key: str | None = theme_value.get("fallback_key")
    fallback_value: "ThemeValueT | None" = theme_value.get("fallback_value")
    fallback_function = theme_value.get("fallback_function")

    if result_value is None:
        if fallback_value is not None:
            result_value = fallback_value
        elif fallback_key:
            result_value = colorscheme[fallback_key]
        elif fallback_function:
            result_value = fallback_function(colorscheme)

    value_type = theme_value["type"]
    if value_type == "bool" and isinstance(result_value, str):
        return str_to_bool(result_value)
    if value_type == "int":
        return int(result_value)  # type: ignore[arg-type]
    if value_type == "float":
        return float(result_value)  # type: ignore[arg-type]
    if value_type == "options":
        available_options = [option["value"] for option in theme_value["options"]]
        if result_value not in available_options:
            if fallback_value in available_options:
                return fallback_value
            if not available_options:
                raise NoPluginsInstalledError(theme_value)
            return available_options[0]

    return result_value  # type: ignore[return-value]


def _set_fallback_values(
        preset_path: str,
        colorscheme: "ThemeT",
        from_plugin: str | None = None,
) -> None:
    key: str | None
    if not colorscheme:
        theme_keys = [
            item["key"]
            for section in get_theme_model().values()
            for item in section
            if "key" in item
        ]

        theme_keys.append("NOGUI")

        with open(preset_path, encoding=DEFAULT_ENCODING) as file_object:
            for line in file_object.readlines():
                key, _sep, value = line.strip().partition("=")
                if key.startswith("#") or key not in theme_keys:
                    continue
                colorscheme[key] = value

    for section in get_theme_model().values():  # @TODO: store theme in memory also in two levels?
        for theme_model_item in section:
            key = theme_model_item.get("key")
            if not key:
                continue
            try:
                colorscheme[key] = parse_theme_value(theme_model_item, colorscheme)
            except NoPluginsInstalledError as exc:
                colorscheme[key] = exc
    if from_plugin:
        colorscheme["FROM_PLUGIN"] = from_plugin


def read_colorscheme_from_path(
        preset_path: str,
        callback: "Callable[[ThemeT, ], None]",
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
                def _get_actual_callback(
                        plugin_to_use: str | None,
                ) -> "Callable[[ThemeT], None]":
                    def actual_callback(colorscheme2: "ThemeT") -> None:
                        _set_fallback_values(preset_path, colorscheme2, plugin_to_use)
                        callback(colorscheme2)
                    return actual_callback
                plugin.read_colorscheme_from_path(
                    preset_path,
                    callback=_get_actual_callback(from_plugin),  # type: ignore[call-arg]
                )
                return
            colorscheme = plugin.read_colorscheme_from_path(preset_path)
            break

    _set_fallback_values(preset_path, colorscheme, from_plugin)
    callback(colorscheme)
    return  # <-- this is quite stupid from pylint's side to ask for this
