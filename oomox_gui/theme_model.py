import os
from typing import TYPE_CHECKING

from .config import TERMINAL_TEMPLATE_DIR
from .i18n import translate
from .plugin_loader import PluginLoader

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from typing import Any

    from typing_extensions import NotRequired, TypedDict

    from .plugin_api import OomoxPlugin
    from .theme_file import ThemeValueT

    class Option(TypedDict, total=False):
        value: str | int
        display_name: NotRequired[str]
        description: NotRequired[str]

    class ThemeModelValue(TypedDict, total=False):
        key: str
        type: str
        fallback_key: NotRequired[str]
        fallback_value: NotRequired[Any]
        fallback_function: NotRequired[Callable[[dict[str, Any]], Any]]
        display_name: NotRequired[str]
        min_value: NotRequired[Any]
        max_value: NotRequired[Any]
        options: NotRequired[list[Option]]
        value_filter: NotRequired[dict[str, list[ThemeValueT] | ThemeValueT]]
        filter: NotRequired[Callable[[dict[str, Any]], bool]]
        reload_theme: NotRequired[bool]
        reload_options: NotRequired[bool]

    ThemeModelSection = list[ThemeModelValue]
    ThemeModel = dict[str, ThemeModelSection]


def sorted_dict(_dict: dict) -> dict:  # type: ignore[type-arg]
    return dict(sorted(_dict.items(), key=lambda x: x))


def get_key_indexes(base_theme_model: "list[ThemeModelValue]") -> "dict[str, int]":
    return {
        theme_value["key"]: index
        for index, theme_value in enumerate(base_theme_model)
        if "key" in theme_value
    }


def merge_model_with_plugin(
        theme_model_name: str,
        theme_plugin: "OomoxPlugin",
        base_theme_model: "list[ThemeModelValue]",
        value_filter_key: "str | None" = None,
) -> "ThemeModelSection":
    result: ThemeModelSection = []
    plugin_theme_model = getattr(theme_plugin, "theme_model_" + theme_model_name, None)
    if not plugin_theme_model:
        return result
    plugin_theme_model_keys = []
    for theme_value in plugin_theme_model:
        if isinstance(theme_value, str):
            plugin_theme_model_keys.append(theme_value)
        else:
            result.append(theme_value)
    if not value_filter_key:
        return result
    plugin_enabled_keys = getattr(
        theme_plugin, "enabled_keys_" + theme_model_name, [],
    )
    key_indexes = get_key_indexes(base_theme_model)
    for base_theme_value in [
            theme_option for theme_option in plugin_theme_model
            if not isinstance(theme_option, str)
    ] + [
        base_theme_model[key_indexes[key]]
        for key in plugin_theme_model_keys + plugin_enabled_keys
        if key in key_indexes
    ]:
        value_filter = base_theme_value.setdefault("value_filter", {})
        value_filter_theme_style = value_filter.setdefault(value_filter_key, [])
        if not isinstance(value_filter_theme_style, list):
            value_filter_theme_style = [value_filter_theme_style]
        if theme_plugin.name in value_filter_theme_style:
            continue
        value_filter_theme_style.append(theme_plugin.name)
        base_theme_value["value_filter"][value_filter_key] = value_filter_theme_style
    return result


def merge_model_with_plugins(
        theme_model_name: str,
        plugins: "Mapping[str, OomoxPlugin]",
        base_theme_model: "ThemeModelSection | None" = None,
        value_filter_key: "str | None" = None,
) -> "ThemeModelSection":
    if base_theme_model is None:
        base_theme_model = []
    whole_theme_model = base_theme_model[::]

    for theme_plugin in plugins.values():
        plugin_theme_model = merge_model_with_plugin(
            theme_model_name=theme_model_name,
            theme_plugin=theme_plugin,
            base_theme_model=base_theme_model,
            value_filter_key=value_filter_key,
        )
        whole_theme_model += plugin_theme_model

    return whole_theme_model


def get_theme_model_uncached() -> "ThemeModel":
    #  @TODO: refactor theme_model loader into class

    def merge_theme_model_with_plugins(
            theme_model_name: str,
            base_theme_model: "ThemeModelSection | None" = None,
    ) -> "ThemeModelSection":
        return merge_model_with_plugins(
            theme_model_name=theme_model_name,
            base_theme_model=base_theme_model,
            value_filter_key="THEME_STYLE",
            plugins=PluginLoader.get_theme_plugins(),
        )

    theme_model: ThemeModel = {}

    theme_model["import"] = merge_model_with_plugins(
        theme_model_name="import",
        value_filter_key="FROM_PLUGIN",
        plugins=PluginLoader.get_import_plugins(),
    )

    theme_model["base"] = [
        {
            "type": "separator",
            "display_name": translate("Theme Style"),
        },
        {
            "key": "THEME_STYLE",
            "type": "options",
            "options": [
                {
                    "value": theme_plugin.name,
                    "display_name": theme_plugin.display_name,
                    "description": theme_plugin.description,
                }
                for theme_plugin in sorted_dict(PluginLoader.get_theme_plugins()).values()
            ],
            "fallback_value": "oomox",
            "display_name": translate("Style for UI elements"),
        },
    ]

    base_theme_model_gtk: ThemeModelSection = [
        {
            "type": "separator",
            "display_name": translate("Theme Colors"),
        },
        {
            "key": "BG",
            "type": "color",
            "display_name": translate("Background"),
        },
        {
            "key": "FG",
            "type": "color",
            "display_name": translate("Text"),
        },
        {
            "key": "HDR_BG",
            "fallback_key": "MENU_BG",
            "type": "color",
            "display_name": translate("Header Background"),
        },
        {
            "key": "HDR_FG",
            "fallback_key": "MENU_FG",
            "type": "color",
            "display_name": translate("Header Text"),
        },
        {
            "key": "SEL_BG",
            "fallback_key": "FG",
            "type": "color",
            "display_name": translate("Selected Background"),
        },
        {
            "key": "SEL_FG",
            "fallback_key": "BG",
            "type": "color",
            "display_name": translate("Selected Text"),
        },
        {
            "key": "ACCENT_BG",
            "fallback_key": "SEL_BG",
            "type": "color",
            "display_name": translate("Accent Color (Checkboxes, Radios)"),
        },
        {
            "key": "TXT_BG",
            "fallback_key": "BG",
            "type": "color",
            "display_name": translate("Textbox Background"),
        },
        {
            "key": "TXT_FG",
            "fallback_key": "FG",
            "type": "color",
            "display_name": translate("Textbox Text"),
        },
        {
            "key": "BTN_BG",
            "fallback_key": "BG",
            "type": "color",
            "display_name": translate("Button Background"),
        },
        {
            "key": "BTN_FG",
            "fallback_key": "FG",
            "type": "color",
            "display_name": translate("Button Text"),
        },
        {
            "key": "HDR_BTN_BG",
            "fallback_key": "BTN_BG",
            "type": "color",
            "display_name": translate("Header Button Background"),
        },
        {
            "key": "HDR_BTN_FG",
            "fallback_key": "BTN_FG",
            "type": "color",
            "display_name": translate("Header Button Text"),
        },
        {
            "key": "WM_BORDER_FOCUS",
            "fallback_key": "SEL_BG",
            "type": "color",
            "display_name": translate("Focused Window Border"),
        },
        {
            "key": "WM_BORDER_UNFOCUS",
            "fallback_key": "HDR_BG",
            "type": "color",
            "display_name": translate("Unfocused Window Border"),
        },
        # migration of old names:
        {
            "key": "MENU_BG",
            "fallback_key": "BG",
            "type": "color",
            "filter": lambda _v: False,
        },
        {
            "key": "MENU_FG",
            "fallback_key": "FG",
            "type": "color",
            "filter": lambda _v: False,
        },
    ]
    theme_model["colors"] = merge_model_with_plugins(
        theme_model_name="gtk",
        base_theme_model=merge_theme_model_with_plugins("gtk", base_theme_model_gtk),
        value_filter_key="FROM_PLUGIN",
        plugins=PluginLoader.get_import_plugins(),
    )

    base_theme_model_options: ThemeModelSection = [
        {
            "type": "separator",
            "display_name": translate("Theme Options"),
        },
        {
            "key": "ROUNDNESS",
            "type": "int",
            "fallback_value": 2,
            "display_name": translate("Roundness"),
        },
        {
            "key": "GRADIENT",
            "type": "float",
            "fallback_value": 0.0,
            "max_value": 2.0,
            "display_name": translate("Gradient"),
        },
    ]
    theme_model["theme_options"] = merge_theme_model_with_plugins(
        "options", base_theme_model_options,
    )

    base_icon_theme_model: ThemeModelSection = [
        {
            "type": "separator",
            "display_name": translate("Iconset"),
        },
        {
            "key": "ICONS_STYLE",
            "type": "options",
            "options": [
                {
                    "value": icons_plugin.name,
                    "display_name": icons_plugin.display_name,
                }
                for icons_plugin in sorted_dict(PluginLoader.get_icons_plugins()).values()
            ],
            "fallback_value": "gnome_colors",
            "display_name": translate("Icons Style"),
        },
    ]
    theme_model["icons"] = merge_model_with_plugins(
        base_theme_model=base_icon_theme_model,
        theme_model_name="icons",
        value_filter_key="ICONS_STYLE",
        plugins=PluginLoader.get_icons_plugins(),
    )

    theme_model["terminal"] = [
        {
            "type": "separator",
            "display_name": translate("Terminal"),
        },
        {
            "key": "TERMINAL_THEME_MODE",
            "type": "options",
            "options": [
                {"value": "auto", "display_name": translate("Auto")},
                {"value": "basic", "display_name": translate("Basic")},
                {"value": "smarty", "display_name": translate("Advanced")},
                {"value": "manual", "display_name": translate("Manual")},
            ],
            "fallback_value": "auto",
            "display_name": translate("Theme Options"),
        },
        {
            "key": "TERMINAL_BASE_TEMPLATE",
            "type": "options",
            "options": [
                {"value": template_name}
                for template_name in sorted(os.listdir(TERMINAL_TEMPLATE_DIR))
            ],
            "fallback_value": "monovedek",
            "display_name": translate("Theme Style"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["auto", "basic", "smarty"],
            },
        },
        {
            "key": "TERMINAL_BACKGROUND",
            "type": "color",
            "fallback_key": "TXT_BG",
            # 'fallback_key': 'HDR_BG',
            "display_name": translate("Background"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["basic", "manual", "smarty"],
            },
        },
        {
            "key": "TERMINAL_FOREGROUND",
            "type": "color",
            "fallback_key": "TXT_FG",
            # 'fallback_key': 'HDR_FG',
            "display_name": translate("Foreground"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["basic", "manual", "smarty"],
            },
        },
        {
            "key": "TERMINAL_CURSOR",
            "type": "color",
            "fallback_key": "TERMINAL_FOREGROUND",
            "display_name": translate("Cursor"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["basic", "manual", "smarty"],
            },
        },
        {
            "key": "TERMINAL_ACCENT_COLOR",
            "type": "color",
            "fallback_key": "SEL_BG",
            "display_name": translate("Accent Color"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["basic"],
            },
        },

        {
            "key": "TERMINAL_THEME_AUTO_BGFG",
            "type": "bool",
            "fallback_value": True,
            "display_name": translate("Auto-Swap BG/FG"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["auto", "basic", "smarty"],
            },
        },
        {
            "key": "TERMINAL_THEME_EXTEND_PALETTE",
            "type": "bool",
            "fallback_value": False,
            "display_name": translate("Extend Palette with More Lighter/Darker Colors"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["smarty"],
            },
        },
        {
            "key": "TERMINAL_THEME_ACCURACY",
            "type": "int",
            "fallback_value": 128,
            "display_name": translate("Palette Generation Accuracy"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["smarty"],
            },
            "min_value": 8,
            "max_value": 255,
        },

        # Black
        {
            "key": "TERMINAL_COLOR0",
            "type": "color",
            "display_name": translate("Black"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        {
            "key": "TERMINAL_COLOR8",
            "type": "color",
            "display_name": translate("Black Highlight"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        # Red
        {
            "key": "TERMINAL_COLOR1",
            "type": "color",
            "display_name": translate("Red"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        {
            "key": "TERMINAL_COLOR9",
            "type": "color",
            "display_name": translate("Red Highlight"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        # Green
        {
            "key": "TERMINAL_COLOR2",
            "type": "color",
            "display_name": translate("Green"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        {
            "key": "TERMINAL_COLOR10",
            "type": "color",
            "display_name": translate("Green Highlight"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        # Yellow
        {
            "key": "TERMINAL_COLOR3",
            "type": "color",
            "display_name": translate("Yellow"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        {
            "key": "TERMINAL_COLOR11",
            "type": "color",
            "display_name": translate("Yellow Highlight"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        # Blue
        {
            "key": "TERMINAL_COLOR4",
            "type": "color",
            "display_name": translate("Blue"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        {
            "key": "TERMINAL_COLOR12",
            "type": "color",
            "display_name": translate("Blue Highlight"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        # Purple
        {
            "key": "TERMINAL_COLOR5",
            "type": "color",
            "display_name": translate("Purple"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        {
            "key": "TERMINAL_COLOR13",
            "type": "color",
            "display_name": translate("Purple Highlight"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        # Cyan
        {
            "key": "TERMINAL_COLOR6",
            "type": "color",
            "display_name": translate("Cyan"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        {
            "key": "TERMINAL_COLOR14",
            "type": "color",
            "display_name": translate("Cyan Highlight"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        # White
        {
            "key": "TERMINAL_COLOR7",
            "type": "color",
            "display_name": translate("White"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
        {
            "key": "TERMINAL_COLOR15",
            "type": "color",
            "display_name": translate("White Highlight"),
            "value_filter": {
                "TERMINAL_THEME_MODE": ["manual"],
            },
        },
    ]

    _theme_export_plugins = merge_theme_model_with_plugins("extra")
    theme_model["export"] = merge_model_with_plugins(
        base_theme_model=_theme_export_plugins,
        theme_model_name="extra",
        plugins=PluginLoader.get_export_plugins(),
    )

    return theme_model


class CachedThemeModel:

    _theme_model = None

    @classmethod
    def get(cls) -> "ThemeModel":
        if not cls._theme_model:
            cls._theme_model = get_theme_model_uncached()
        return cls._theme_model


def get_theme_model() -> "ThemeModel":
    return CachedThemeModel.get()


def get_theme_options_by_key(
        key: str,
        fallback: "ThemeModelValue | None" = None,
) -> "list[ThemeModelValue]":
    result = [
        theme_option
        for section in get_theme_model().values()
        for theme_option in section
        if key == theme_option.get("key")
    ]
    if not result and fallback:
        return [fallback]
    return result


def get_first_theme_option(
        key: str,
        fallback: "ThemeModelValue | None" = None,
) -> "ThemeModelValue":
    result = get_theme_options_by_key(key, fallback=fallback)
    if result:
        return result[0]
    return {}
