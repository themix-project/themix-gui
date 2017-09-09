def create_value_filter(key, value):
    def value_filter(colorscheme):
        return colorscheme[key] == value
    return value_filter


theme_model = [
    {
        'key': 'THEME_STYLE',
        'type': 'options',
        'options': [
            {
                'value': 'oomox',
                'display_name': 'Numix-based'
            }, {
                'value': 'flatplat',
                'display_name': 'Flat-Plat'
            }
        ],
        'fallback_value': 'oomox',
        'display_name': _('Theme style')
    },
    {
        'key': 'BG',
        'type': 'color',
        'display_name': _('Background')
    },
    {
        'key': 'FG',
        'type': 'color',
        'display_name': _('Foreground/text')
    },
    {
        'key': 'MENU_BG',
        'type': 'color',
        'display_name': _('Menu/toolbar background')
    },
    {
        'key': 'MENU_FG',
        'type': 'color',
        'display_name': _('Menu/toolbar text'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
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
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },
    {
        'key': 'ACCENT_BG',
        'fallback_key': 'SEL_BG',
        'type': 'color',
        'display_name': _('Accent color (checkboxes, radios)'),
        'filter': create_value_filter('THEME_STYLE', 'flatplat'),
    },
    {
        'key': 'TXT_BG',
        'type': 'color',
        'display_name': _('Textbox background')
    },
    {
        'key': 'TXT_FG',
        'type': 'color',
        'display_name': _('Textbox text')
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
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },
    {
        'key': 'HDR_BTN_BG',
        'fallback_key': 'BTN_BG',
        'type': 'color',
        'display_name': _('Header button background'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },
    {
        'key': 'HDR_BTN_FG',
        'fallback_key': 'BTN_FG',
        'type': 'color',
        'display_name': _('Header button text'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },
    {
        'key': 'WM_BORDER_FOCUS',
        'fallback_key': 'SEL_BG',
        'type': 'color',
        'display_name': _('Focused window border'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },
    {
        'key': 'WM_BORDER_UNFOCUS',
        'fallback_key': 'MENU_BG',
        'type': 'color',
        'display_name': _('Unfocused window border'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },

    {
        'type': 'separator',
        'display_name': _('Theme options'),
    },

    {
        'key': 'ROUNDNESS',
        'type': 'int',
        'fallback_value': 2,
        'display_name': _('Roundness'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },
    {
        'key': 'SPACING',
        'type': 'int',
        'fallback_value': 3,
        'display_name': _('(GTK3) Spacing'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },
    {
        'key': 'GRADIENT',
        'type': 'float',
        'fallback_value': 0.0,
        'display_name': _('(GTK3) Gradient'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },
    {
        'key': 'GTK3_GENERATE_DARK',
        'type': 'bool',
        'fallback_value': True,
        'display_name': _('(GTK3) Add dark variant'),
    },
    {
        'key': 'GTK2_HIDPI',
        'type': 'bool',
        'fallback_value': False,
        'display_name': _('(GTK2) HiDPI'),
    },
    {
        'key': 'FLATPACK_STYLE_COMPACT',
        'type': 'bool',
        'fallback_value': True,
        'display_name': _('Compact style'),
        'filter': create_value_filter('THEME_STYLE', 'flatplat'),
    },

    {
        'type': 'separator',
        'display_name': _('Text input caret'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },
    {
        'key': 'CARET1_FG',
        'type': 'color',
        'fallback_key': 'TXT_FG',
        'display_name': _('Primary caret color'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },
    {
        'key': 'CARET2_FG',
        'type': 'color',
        'fallback_key': 'TXT_FG',
        'display_name': _('Secondary caret color'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },
    {
        'key': 'CARET_SIZE',
        'type': 'float',
        'fallback_value': 0.04,  # GTK's default
        'display_name': _('Caret aspect ratio'),
        'filter': create_value_filter('THEME_STYLE', 'oomox'),
    },

    {
        'type': 'separator',
        'display_name': _('Iconset')
    },

    {
        'key': 'ICONS_STYLE',
        'type': 'options',
        'options': [
            {
                'value': 'gnome_colors',
                'display_name': 'Gnome-Colors'
            }, {
                'value': 'archdroid',
                'display_name': 'ArchDroid'
            }
        ],
        'fallback_value': 'gnome_colors',
        'display_name': _('Icons style')
    },
    {
        'key': 'ICONS_ARCHDROID',
        'type': 'color',
        'fallback_key': 'SEL_BG',
        'display_name': _('Icons color'),
        'filter': create_value_filter('ICONS_STYLE', 'archdroid')
    },
    {
        'key': 'ICONS_LIGHT_FOLDER',
        'type': 'color',
        'fallback_key': 'SEL_BG',
        'display_name': _('Light base (folders)'),
        'filter': create_value_filter('ICONS_STYLE', 'gnome_colors')
    },
    {
        'key': 'ICONS_LIGHT',
        'fallback_key': 'SEL_BG',
        'type': 'color',
        'display_name': _('Light base'),
        'filter': create_value_filter('ICONS_STYLE', 'gnome_colors')
    },
    {
        'key': 'ICONS_MEDIUM',
        'type': 'color',
        'fallback_key': 'BTN_BG',
        'display_name': _('Medium base'),
        'filter': create_value_filter('ICONS_STYLE', 'gnome_colors')
    },
    {
        'key': 'ICONS_DARK',
        'type': 'color',
        'fallback_key': 'MENU_BG',
        'display_name': _('Dark stroke'),
        'filter': create_value_filter('ICONS_STYLE', 'gnome_colors')
    },

    {
        'type': 'separator',
        'display_name': _('Other options')
    },
    {
        'key': 'UNITY_DEFAULT_LAUNCHER_STYLE',
        'type': 'bool',
        'fallback_value': False,
        'display_name': _('(Unity) Use default launcher style')
    },
]
