import sys
import os

from .config import TERMINAL_TEMPLATE_DIR
from .plugin_loader import (
    THEME_PLUGINS, ICONS_PLUGINS, EXPORT_PLUGINS, IMPORT_PLUGINS,
)
from .i18n import _


if sys.version_info.minor >= 5:
    from typing import TYPE_CHECKING  # pylint: disable=wrong-import-order
    if TYPE_CHECKING:
        # pylint: disable=ungrouped-imports
        from typing import List, Dict, Any  # noqa

        ThemeModelValue = Dict[str, Any]


def sorted_dict(_dict):
    return dict(sorted(_dict.items(), key=lambda x: x))


def get_key_indexes(base_theme_model):
    return {
        theme_value['key']: index
        for index, theme_value in enumerate(base_theme_model)
        if 'key' in theme_value
    }


def merge_model_with_plugin(
        theme_model_name, theme_plugin,
        base_theme_model,
        value_filter_key=None
):
    result = []
    plugin_theme_model = getattr(theme_plugin, "theme_model_"+theme_model_name, None)
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
        theme_plugin, "enabled_keys_"+theme_model_name, []
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
        value_filter = base_theme_value.setdefault('value_filter', {})
        value_filter_theme_style = value_filter.setdefault(value_filter_key, [])
        if not isinstance(value_filter_theme_style, list):
            value_filter_theme_style = [value_filter_theme_style, ]
        if theme_plugin.name in value_filter_theme_style:
            continue
        value_filter_theme_style.append(theme_plugin.name)
        base_theme_value['value_filter'][value_filter_key] = value_filter_theme_style
    return result


def merge_model_with_plugins(
        theme_model_name, plugins,
        base_theme_model=None, value_filter_key=None
):
    if base_theme_model is None:
        base_theme_model = []
    whole_theme_model = base_theme_model[::]

    for theme_plugin in plugins.values():
        plugin_theme_model = merge_model_with_plugin(
            theme_model_name=theme_model_name,
            theme_plugin=theme_plugin,
            base_theme_model=base_theme_model,
            value_filter_key=value_filter_key
        )
        whole_theme_model += plugin_theme_model

    return whole_theme_model


def merge_theme_model_with_plugins(theme_model_name, base_theme_model=None):
    return merge_model_with_plugins(
        theme_model_name=theme_model_name,
        base_theme_model=base_theme_model,
        value_filter_key='THEME_STYLE',
        plugins=THEME_PLUGINS,
    )


THEME_MODEL = {
}  # type: Dict[str, List[ThemeModelValue]]


THEME_MODEL['import'] = merge_model_with_plugins(
    theme_model_name='import',
    value_filter_key='FROM_PLUGIN',
    plugins=IMPORT_PLUGINS,
)


THEME_MODEL['base'] = [
    {
        'type': 'separator',
        'display_name': _('Theme Style'),
    },
    {
        'key': 'THEME_STYLE',
        'type': 'options',
        'options': [
            {
                'value': theme_plugin.name,
                'display_name': theme_plugin.display_name,
                'description': theme_plugin.description,
            }
            for theme_plugin in sorted_dict(THEME_PLUGINS).values()
        ],
        'fallback_value': 'oomox',
        'display_name': _('Style for UI elements'),
    },
]

BASE_THEME_MODEL_GTK = [
    {
        'type': 'separator',
        'display_name': _('Theme Colors'),
    },
    {
        'key': 'BG',
        'type': 'color',
        'display_name': _('Background')
    },
    {
        'key': 'FG',
        'type': 'color',
        'display_name': _('Text')
    },
    {
        'key': 'HDR_BG',
        'fallback_key': 'MENU_BG',
        'type': 'color',
        'display_name': _('Header Background')
    },
    {
        'key': 'HDR_FG',
        'fallback_key': 'MENU_FG',
        'type': 'color',
        'display_name': _('Header Text'),
    },
    {
        'key': 'SEL_BG',
        'fallback_key': 'FG',
        'type': 'color',
        'display_name': _('Selected Background')
    },
    {
        'key': 'SEL_FG',
        'fallback_key': 'BG',
        'type': 'color',
        'display_name': _('Selected Text'),
    },
    {
        'key': 'ACCENT_BG',
        'fallback_key': 'SEL_BG',
        'type': 'color',
        'display_name': _('Accent Color (Checkboxes, Radios)'),
    },
    {
        'key': 'TXT_BG',
        'fallback_key': 'BG',
        'type': 'color',
        'display_name': _('Textbox Background')
    },
    {
        'key': 'TXT_FG',
        'fallback_key': 'FG',
        'type': 'color',
        'display_name': _('Textbox Text'),
    },
    {
        'key': 'BTN_BG',
        'fallback_key': 'BG',
        'type': 'color',
        'display_name': _('Button Background')
    },
    {
        'key': 'BTN_FG',
        'fallback_key': 'FG',
        'type': 'color',
        'display_name': _('Button Text'),
    },
    {
        'key': 'HDR_BTN_BG',
        'fallback_key': 'BTN_BG',
        'type': 'color',
        'display_name': _('Header Button Background'),
    },
    {
        'key': 'HDR_BTN_FG',
        'fallback_key': 'BTN_FG',
        'type': 'color',
        'display_name': _('Header Button Text'),
    },
    {
        'key': 'WM_BORDER_FOCUS',
        'fallback_key': 'SEL_BG',
        'type': 'color',
        'display_name': _('Focused Window Border'),
    },
    {
        'key': 'WM_BORDER_UNFOCUS',
        'fallback_key': 'HDR_BG',
        'type': 'color',
        'display_name': _('Unfocused Window Border'),
    },
    # migration of old names:
    {
        'key': 'MENU_BG',
        'fallback_key': 'BG',
        'type': 'color',
        'filter': lambda _v: False
    },
    {
        'key': 'MENU_FG',
        'fallback_key': 'FG',
        'type': 'color',
        'filter': lambda _v: False
    },
]
THEME_MODEL['colors'] = merge_model_with_plugins(
    theme_model_name='gtk',
    base_theme_model=merge_theme_model_with_plugins('gtk', BASE_THEME_MODEL_GTK),
    value_filter_key='FROM_PLUGIN',
    plugins=IMPORT_PLUGINS,
)


BASE_THEME_MODEL_OPTIONS = [
    {
        'type': 'separator',
        'display_name': _('Theme Options'),
    },
    {
        'key': 'ROUNDNESS',
        'type': 'int',
        'fallback_value': 2,
        'display_name': _('Roundness'),
    },
    {
        'key': 'GRADIENT',
        'type': 'float',
        'fallback_value': 0.0,
        'max_value': 2.0,
        'display_name': _('Gradient'),
    },
]
THEME_MODEL['theme_options'] = merge_theme_model_with_plugins('options', BASE_THEME_MODEL_OPTIONS)

BASE_ICON_THEME_MODEL = [
    {
        'type': 'separator',
        'display_name': _('Iconset')
    },
    {
        'key': 'ICONS_STYLE',
        'type': 'options',
        'options': [
            {
                'value': icons_plugin.name,
                'display_name': icons_plugin.display_name,
            }
            for icons_plugin in sorted_dict(ICONS_PLUGINS).values()
        ],
        'fallback_value': 'gnome_colors',
        'display_name': _('Icons Style')
    },
]
THEME_MODEL['icons'] = merge_model_with_plugins(
    base_theme_model=BASE_ICON_THEME_MODEL,
    theme_model_name='icons',
    value_filter_key='ICONS_STYLE',
    plugins=ICONS_PLUGINS,
)


THEME_MODEL['terminal'] = [
    {
        'type': 'separator',
        'display_name': _('Terminal')
    },
    {
        'key': 'TERMINAL_THEME_MODE',
        'type': 'options',
        'options': [
            {'value': 'auto', 'display_name': _('Auto')},
            {'value': 'basic', 'display_name': _('Basic')},
            {'value': 'smarty', 'display_name': _('Advanced')},
            {'value': 'manual', 'display_name': _('Manual')},
        ],
        'fallback_value': 'auto',
        'display_name': _('Theme Options')
    },
    {
        'key': 'TERMINAL_BASE_TEMPLATE',
        'type': 'options',
        'options': [
            {'value': template_name}
            for template_name in sorted(os.listdir(TERMINAL_TEMPLATE_DIR))
        ],
        'fallback_value': 'monovedek',
        'display_name': _('Theme Style'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['auto', 'basic', 'smarty', ],
        },
    },
    {
        'key': 'TERMINAL_BACKGROUND',
        'type': 'color',
        'fallback_key': 'TXT_BG',
        # 'fallback_key': 'HDR_BG',
        'display_name': _('Background'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['basic', 'manual', 'smarty', ],
        },
    },
    {
        'key': 'TERMINAL_FOREGROUND',
        'type': 'color',
        'fallback_key': 'TXT_FG',
        # 'fallback_key': 'HDR_FG',
        'display_name': _('Foreground'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['basic', 'manual', 'smarty', ],
        },
    },
    {
        'key': 'TERMINAL_ACCENT_COLOR',
        'type': 'color',
        'fallback_key': 'SEL_BG',
        'display_name': _('Accent Color'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['basic', ],
        },
    },

    {
        'key': 'TERMINAL_THEME_AUTO_BGFG',
        'type': 'bool',
        'fallback_value': True,
        'display_name': _('Auto-Swap BG/FG'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['auto', 'basic', 'smarty', ],
        },
    },
    {
        'key': 'TERMINAL_THEME_EXTEND_PALETTE',
        'type': 'bool',
        'fallback_value': False,
        'display_name': _('Extend Palette with More Lighter/Darker Colors'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['smarty', ],
        },
    },
    {
        'key': 'TERMINAL_THEME_ACCURACY',
        'type': 'int',
        'fallback_value': 128,
        'display_name': _('Palette Generation Accuracy'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['smarty', ],
        },
        'min_value': 8,
        'max_value': 255,
    },

    # Black
    {
        'key': 'TERMINAL_COLOR0',
        'type': 'color',
        'display_name': _('Black'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    {
        'key': 'TERMINAL_COLOR8',
        'type': 'color',
        'display_name': _('Black Highlight'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    # Red
    {
        'key': 'TERMINAL_COLOR1',
        'type': 'color',
        'display_name': _('Red'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    {
        'key': 'TERMINAL_COLOR9',
        'type': 'color',
        'display_name': _('Red Highlight'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    # Green
    {
        'key': 'TERMINAL_COLOR2',
        'type': 'color',
        'display_name': _('Green'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    {
        'key': 'TERMINAL_COLOR10',
        'type': 'color',
        'display_name': _('Green Highlight'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    # Yellow
    {
        'key': 'TERMINAL_COLOR3',
        'type': 'color',
        'display_name': _('Yellow'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    {
        'key': 'TERMINAL_COLOR11',
        'type': 'color',
        'display_name': _('Yellow Highlight'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    # Blue
    {
        'key': 'TERMINAL_COLOR4',
        'type': 'color',
        'display_name': _('Blue'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    {
        'key': 'TERMINAL_COLOR12',
        'type': 'color',
        'display_name': _('Blue Highlight'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    # Purple
    {
        'key': 'TERMINAL_COLOR5',
        'type': 'color',
        'display_name': _('Purple'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    {
        'key': 'TERMINAL_COLOR13',
        'type': 'color',
        'display_name': _('Purple Highlight'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    # Cyan
    {
        'key': 'TERMINAL_COLOR6',
        'type': 'color',
        'display_name': _('Cyan'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    {
        'key': 'TERMINAL_COLOR14',
        'type': 'color',
        'display_name': _('Cyan Highlight'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    # White
    {
        'key': 'TERMINAL_COLOR7',
        'type': 'color',
        'display_name': _('White'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
    {
        'key': 'TERMINAL_COLOR15',
        'type': 'color',
        'display_name': _('White Highlight'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
]

_theme_export_plugins = merge_theme_model_with_plugins('extra')
THEME_MODEL['export'] = merge_model_with_plugins(
    base_theme_model=_theme_export_plugins,
    theme_model_name='extra',
    plugins=EXPORT_PLUGINS,
)


def get_theme_options_by_key(key, fallback=None):
    result = []
    for _section_id, section in THEME_MODEL.items():
        for theme_option in section:
            if key == theme_option.get('key'):
                result.append(theme_option)
    if not result and fallback:
        return [fallback]
    return result


def get_first_theme_option(key, fallback=None):
    result = get_theme_options_by_key(key, fallback=fallback)
    if result:
        return result[0]
    return {}
