def create_value_filter(key, value):
    def value_filter(colorscheme):
        return colorscheme[key] == value
    return value_filter


theme_model = [
    {
        'key': 'BG',
        'type': 'color',
        'display_name': 'Background'
    },
    {
        'key': 'FG',
        'type': 'color',
        'display_name': 'Foreground/text'
    },
    {
        'key': 'MENU_BG',
        'type': 'color',
        'display_name': 'Menu/toolbar background'
    },
    {
        'key': 'MENU_FG',
        'type': 'color',
        'display_name': 'Menu/toolbar text'
    },
    {
        'key': 'SEL_BG',
        'type': 'color',
        'display_name': 'Selection highlight'
    },
    {
        'key': 'SEL_FG',
        'type': 'color',
        'display_name': 'Selection text'
    },
    {
        'key': 'TXT_BG',
        'type': 'color',
        'display_name': 'Textbox background'
    },
    {
        'key': 'TXT_FG',
        'type': 'color',
        'display_name': 'Textbox text'
    },
    {
        'key': 'BTN_BG',
        'type': 'color',
        'display_name': 'Button background'
    },
    {
        'key': 'BTN_FG',
        'type': 'color',
        'display_name': 'Button text'
    },
    {
        'key': 'HDR_BTN_BG',
        'fallback_key': 'BTN_BG',
        'type': 'color',
        'display_name': 'Header button background'
    },
    {
        'key': 'HDR_BTN_FG',
        'fallback_key': 'BTN_FG',
        'type': 'color',
        'display_name': 'Header button text'
    },

    {
        'type': 'separator',
        'display_name': 'Options'
    },

    {
        'key': 'ROUNDNESS',
        'type': 'int',
        'fallback_value': 2,
        'display_name': 'Roundness'
    },
    {
        'key': 'SPACING',
        'type': 'int',
        'fallback_value': 3,
        'display_name': '(GTK3) Spacing'
    },
    {
        'key': 'GRADIENT',
        'type': 'float',
        'fallback_value': 0.0,
        'display_name': '(GTK3) Gradient'
    },
    {
        'key': 'GTK3_GENERATE_DARK',
        'type': 'bool',
        'fallback_value': True,
        'display_name': '(GTK3) Add dark variant'
    },
    {
        'key': 'GTK2_HIDPI',
        'type': 'bool',
        'fallback_value': False,
        'display_name': '(GTK2) HiDPI'
    },

    {
        'type': 'separator',
        'display_name': 'Iconset'
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
        'display_name': 'Icons style'
    },
    {
        'key': 'ICONS_ARCHDROID',
        'type': 'color',
        'fallback_key': 'SEL_BG',
        'display_name': 'Icons color',
        'filter': create_value_filter('ICONS_STYLE', 'archdroid')
    },
    {
        'key': 'ICONS_LIGHT_FOLDER',
        'type': 'color',
        'fallback_key': 'SEL_BG',
        'display_name': 'Light base (folders)',
        'filter': create_value_filter('ICONS_STYLE', 'gnome_colors')
    },
    {
        'key': 'ICONS_LIGHT',
        'fallback_key': 'SEL_BG',
        'type': 'color',
        'display_name': 'Light base',
        'filter': create_value_filter('ICONS_STYLE', 'gnome_colors')
    },
    {
        'key': 'ICONS_MEDIUM',
        'type': 'color',
        'fallback_key': 'BTN_BG',
        'display_name': 'Medium base',
        'filter': create_value_filter('ICONS_STYLE', 'gnome_colors')
    },
    {
        'key': 'ICONS_DARK',
        'type': 'color',
        'fallback_key': 'BTN_FG',
        'display_name': 'Dark stroke',
        'filter': create_value_filter('ICONS_STYLE', 'gnome_colors')
    },
]
