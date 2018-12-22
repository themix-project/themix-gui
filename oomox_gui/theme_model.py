import os

from .config import TERMINAL_TEMPLATE_DIR
from .plugin_loader import (
    THEME_PLUGINS, ICONS_PLUGINS, EXPORT_PLUGINS, IMPORT_PLUGINS,
)
from .i18n import _


def sorted_dict(_dict):
    return dict(sorted(_dict.items(), key=lambda x: x))


def get_base_keys(base_theme_model):
    return {
        theme_value['key']: index
        for index, theme_value in enumerate(base_theme_model)
        if 'key' in theme_value
    }


def merge_model_with_base(
        whole_theme_model, plugin_model_name,
        plugins, base_theme_model=None, value_filter_key=None
):
    if base_theme_model is None:
        base_theme_model = []
    base_keys = get_base_keys(base_theme_model)

    if value_filter_key:
        for theme_value in base_theme_model:
            if 'key' in theme_value:
                theme_value.setdefault('value_filter', {}).setdefault(value_filter_key, [])

    for theme_plugin in plugins.values():
        plugin_theme_model = getattr(theme_plugin, "theme_model_"+plugin_model_name)
        for theme_value in plugin_theme_model:
            if 'key' not in theme_value or theme_value['key'] not in base_keys:
                base_theme_model.append(theme_value)
                base_keys = get_base_keys(base_theme_model)
        plugin_theme_model_keys = [
            theme_value['key']
            for theme_value in plugin_theme_model
            if 'key' in theme_value
        ]
        plugin_enabled_keys = getattr(
            theme_plugin, "enabled_keys_"+plugin_model_name, []
        )
        if not value_filter_key:
            continue
        for key in plugin_theme_model_keys + plugin_enabled_keys:
            base_theme_value = base_theme_model[base_keys[key]]
            value_filter = base_theme_value.setdefault('value_filter', {})
            value_filter_theme_style = value_filter.setdefault(value_filter_key, [])
            if not isinstance(value_filter_theme_style, list):
                value_filter_theme_style = [value_filter_theme_style, ]
            value_filter_theme_style.append(theme_plugin.name)
            base_theme_value['value_filter'][value_filter_key] = value_filter_theme_style
    whole_theme_model += base_theme_model


def merge_theme_model_with_base(whole_theme_model, base_theme_model, plugin_model_name):
    return merge_model_with_base(
        whole_theme_model=whole_theme_model,
        base_theme_model=base_theme_model,
        plugin_model_name=plugin_model_name,
        value_filter_key='THEME_STYLE',
        plugins=THEME_PLUGINS,
    )


THEME_MODEL = []
merge_model_with_base(
    whole_theme_model=THEME_MODEL,
    plugin_model_name='import',
    value_filter_key='FROM_PLUGIN',
    plugins=IMPORT_PLUGINS,
)
THEME_MODEL = THEME_MODEL + [
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
        'display_name': _('Theme style'),
    },
]

BASE_THEME_MODEL_GTK = [
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
        'display_name': _('Header background')
    },
    {
        'key': 'HDR_FG',
        'fallback_key': 'MENU_FG',
        'type': 'color',
        'display_name': _('Header text'),
    },
    {
        'key': 'SEL_BG',
        'type': 'color',
        'display_name': _('Selection highlight')
    },
    {
        'key': 'SEL_FG',
        'type': 'color',
        'display_name': _('Selection text'),
    },
    {
        'key': 'ACCENT_BG',
        'fallback_key': 'SEL_BG',
        'type': 'color',
        'display_name': _('Accent color (checkboxes, radios)'),
    },
    {
        'key': 'TXT_BG',
        'type': 'color',
        'display_name': _('Textbox background')
    },
    {
        'key': 'TXT_FG',
        'type': 'color',
        'display_name': _('Textbox text'),
    },
    {
        'key': 'BTN_BG',
        'type': 'color',
        'display_name': _('Button background')
    },
    {
        'key': 'BTN_FG',
        'type': 'color',
        'display_name': _('Button text'),
    },
    {
        'key': 'HDR_BTN_BG',
        'fallback_key': 'BTN_BG',
        'type': 'color',
        'display_name': _('Header button background'),
    },
    {
        'key': 'HDR_BTN_FG',
        'fallback_key': 'BTN_FG',
        'type': 'color',
        'display_name': _('Header button text'),
    },
    {
        'key': 'WM_BORDER_FOCUS',
        'fallback_key': 'SEL_BG',
        'type': 'color',
        'display_name': _('Focused window border'),
    },
    {
        'key': 'WM_BORDER_UNFOCUS',
        'fallback_key': 'HDR_BG',
        'type': 'color',
        'display_name': _('Unfocused window border'),
    },
    # migration of old names:
    {
        'key': 'MENU_BG',
        'fallback_key': 'BG',
        'type': 'color',
        'filter': lambda v: False
    },
    {
        'key': 'MENU_FG',
        'fallback_key': 'FG',
        'type': 'color',
        'filter': lambda v: False
    },
]
merge_theme_model_with_base(THEME_MODEL, BASE_THEME_MODEL_GTK, 'gtk')

BASE_THEME_MODEL_OPTIONS = [
    {
        'type': 'separator',
        'display_name': _('Theme options'),
    },
    {
        'key': 'ROUNDNESS',
        'type': 'int',
        'fallback_value': 2,
        'display_name': _('Roundness'),
    },
    {
        'key': 'SPACING',
        'type': 'int',
        'fallback_value': 3,
        'display_name': _('(GTK3) Spacing'),
    },
    {
        'key': 'GRADIENT',
        'type': 'float',
        'fallback_value': 0.0,
        'display_name': _('(GTK3) Gradient'),
    },
    {
        'key': 'GTK3_GENERATE_DARK',
        'type': 'bool',
        'fallback_value': True,
        'display_name': _('(GTK3) Add dark variant'),
    },
]
merge_theme_model_with_base(THEME_MODEL, BASE_THEME_MODEL_OPTIONS, 'options')

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
        'display_name': _('Icons style')
    },
]
THEME_MODEL += BASE_ICON_THEME_MODEL
merge_model_with_base(
    whole_theme_model=THEME_MODEL,
    plugin_model_name='icons',
    value_filter_key='ICONS_STYLE',
    plugins=ICONS_PLUGINS,
)

THEME_MODEL += [
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
            {'value': 'manual', 'display_name': _('Manual')},
            {'value': 'smarty', 'display_name': _('Experimental')},
        ],
        'fallback_value': 'auto',
        'display_name': _('Theme options')
    },
    {
        'key': 'TERMINAL_BASE_TEMPLATE',
        'type': 'options',
        'options': [
            {'value': template_name}
            for template_name in sorted(os.listdir(TERMINAL_TEMPLATE_DIR))
        ],
        'fallback_value': 'monovedek',
        'display_name': _('Theme style'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['auto', 'basic', 'smarty', ],
        },
    },
    {
        'key': 'TERMINAL_THEME_AUTO_BGFG',
        'type': 'bool',
        'fallback_value': True,
        'display_name': _('Auto-swap BG/FG'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['auto', 'basic', 'smarty', ],
        },
    },
    {
        'key': 'TERMINAL_THEME_EXTEND_PALETTE',
        'type': 'bool',
        'fallback_value': False,
        'display_name': _('Extend palette with more lighter/darker colors'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['smarty', ],
        },
    },
    {
        'key': 'TERMINAL_THEME_ACCURACY',
        'type': 'int',
        'fallback_value': 128,
        'display_name': _('Palette generation accuracy'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['smarty', ],
        },
        'min_value': 8,
        'max_value': 255,
    },
    {
        'key': 'TERMINAL_BACKGROUND',
        'type': 'color',
        'fallback_key': 'TXT_BG',
        # 'fallback_key': 'HDR_BG',
        'display_name': _('Terminal background'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['basic', 'manual'],
        },
    },
    {
        'key': 'TERMINAL_FOREGROUND',
        'type': 'color',
        'fallback_key': 'TXT_FG',
        # 'fallback_key': 'HDR_FG',
        'display_name': _('Terminal foreground'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['basic', 'manual'],
        },
    },
    {
        'key': 'TERMINAL_ACCENT_COLOR',
        'type': 'color',
        'fallback_key': 'SEL_BG',
        'display_name': _('Terminal accent color'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['basic', ],
        },
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
        'display_name': _('Black highlight'),
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
        'display_name': _('Red highlight'),
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
        'display_name': _('Green highlight'),
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
        'display_name': _('Yellow highlight'),
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
        'display_name': _('Blue highlight'),
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
        'display_name': _('Purple highlight'),
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
        'display_name': _('Cyan highlight'),
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
        'display_name': _('White highlight'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['manual', ],
        },
    },
]

merge_theme_model_with_base(THEME_MODEL, [], 'extra')
merge_model_with_base(
    whole_theme_model=THEME_MODEL,
    plugin_model_name='extra',
    plugins=EXPORT_PLUGINS,
)

BASE_THEME_MODEL_OTHER = [
    {
        'type': 'separator',
        'display_name': _('Other options'),
    },
]
merge_theme_model_with_base(THEME_MODEL, BASE_THEME_MODEL_OTHER, 'other')

THEME_MODEL_BY_KEY = {
    value['key']: value
    for value in THEME_MODEL
    if 'key' in value
}
