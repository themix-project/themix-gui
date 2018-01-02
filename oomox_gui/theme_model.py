import os

from .config import terminal_template_dir


theme_model = [
    {
        'key': 'THEME_STYLE',
        'type': 'options',
        'options': [
            {
                'value': 'oomox',
                'display_name': 'Numix-based',
                'description': '(GTK+2, GTK+3, Metacity, Openbox, Qt5ct, Unity, Xfwm)',
            }, {
                'value': 'materia',
                'display_name': 'Materia',
                'description': '(GTK+2, GTK+3, Gnome Shell, Metacity, Unity, Xfwm)',
            }
        ],
        'fallback_value': 'oomox',
        'display_name': _('Theme style'),
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
        'value_filter': {
            'THEME_STYLE': 'materia'
        },
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
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
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
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
    },
    {
        'key': 'HDR_BTN_FG',
        'fallback_key': 'BTN_FG',
        'type': 'color',
        'display_name': _('Header button text'),
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
    },
    {
        'key': 'WM_BORDER_FOCUS',
        'fallback_key': 'SEL_BG',
        'type': 'color',
        'display_name': _('Focused window border'),
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
    },
    {
        'key': 'WM_BORDER_UNFOCUS',
        'fallback_key': 'MENU_BG',
        'type': 'color',
        'display_name': _('Unfocused window border'),
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
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
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
    },
    {
        'key': 'SPACING',
        'type': 'int',
        'fallback_value': 3,
        'display_name': _('(GTK3) Spacing'),
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
    },
    {
        'key': 'GRADIENT',
        'type': 'float',
        'fallback_value': 0.0,
        'display_name': _('(GTK3) Gradient'),
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
    },
    {
        'key': 'GTK3_GENERATE_DARK',
        'type': 'bool',
        'fallback_value': True,
        'display_name': _('(GTK3) Add dark variant'),
    },
    {
        'key': 'MATERIA_STYLE_COMPACT',
        'type': 'bool',
        'fallback_value': True,
        'display_name': _('Compact style'),
        'value_filter': {
            'THEME_STYLE': 'materia'
        },
    },
    {
        'key': 'GNOME_SHELL_PANEL_OPACITY',
        'type': 'float',
        'fallback_value': 0.6,
        'max_value': 1.0,
        'display_name': _('Gnome Shell panel opacity'),
        'value_filter': {
            'THEME_STYLE': 'materia'
        },
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
        'value_filter': {
            'ICONS_STYLE': 'archdroid',
        },
    },
    {
        'key': 'ICONS_LIGHT_FOLDER',
        'type': 'color',
        'fallback_key': 'SEL_BG',
        'display_name': _('Light base (folders)'),
        'value_filter': {
            'ICONS_STYLE': 'gnome_colors',
        },
    },
    {
        'key': 'ICONS_LIGHT',
        'fallback_key': 'SEL_BG',
        'type': 'color',
        'display_name': _('Light base'),
        'value_filter': {
            'ICONS_STYLE': 'gnome_colors',
        },
    },
    {
        'key': 'ICONS_MEDIUM',
        'type': 'color',
        'fallback_key': 'BTN_BG',
        'display_name': _('Medium base'),
        'value_filter': {
            'ICONS_STYLE': 'gnome_colors',
        },
    },
    {
        'key': 'ICONS_DARK',
        'type': 'color',
        'fallback_key': 'MENU_BG',
        'display_name': _('Dark stroke'),
        'value_filter': {
            'ICONS_STYLE': 'gnome_colors',
        },
    },

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
        ],
        'fallback_value': 'auto',
        'display_name': _('Theme options')
    },
    {
        'key': 'TERMINAL_BASE_TEMPLATE',
        'type': 'options',
        'options': [
            {'value': template_name}
            for template_name in sorted(os.listdir(terminal_template_dir))
        ],
        'fallback_value': 'monovedek',
        'display_name': _('Theme style'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['auto', 'basic'],
        },
    },
    {
        'key': 'TERMINAL_THEME_AUTO_BGFG',
        'type': 'bool',
        'fallback_value': True,
        'display_name': _('Auto-swap BG/FG'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['auto', 'basic'],
        },
    },
    {
        'key': 'TERMINAL_BACKGROUND',
        'type': 'color',
        'fallback_key': 'TXT_BG',
        # 'fallback_key': 'MENU_BG',
        'display_name': _('Terminal background'),
        'value_filter': {
            'TERMINAL_THEME_MODE': ['basic', 'manual'],
        },
    },
    {
        'key': 'TERMINAL_FOREGROUND',
        'type': 'color',
        'fallback_key': 'TXT_FG',
        # 'fallback_key': 'MENU_FG',
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

    {
        'type': 'separator',
        'display_name': _('Spotify')
    },
    {
        'key': 'SPOTIFY_PROTO_BG',
        'type': 'color',
        'fallback_key': 'MENU_BG',
        'display_name': _('Spotify background'),
    },
    {
        'key': 'SPOTIFY_PROTO_FG',
        'type': 'color',
        'fallback_key': 'MENU_FG',
        'display_name': _('Spotify foreground'),
    },
    {
        'key': 'SPOTIFY_PROTO_SEL',
        'type': 'color',
        'fallback_key': 'SEL_BG',
        'display_name': _('Spotify accent color'),
    },

    {
        'type': 'separator',
        'display_name': _('Text input caret'),
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
    },
    {
        'key': 'CARET1_FG',
        'type': 'color',
        'fallback_key': 'TXT_FG',
        'display_name': _('Primary caret color'),
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
    },
    {
        'key': 'CARET2_FG',
        'type': 'color',
        'fallback_key': 'TXT_FG',
        'display_name': _('Secondary caret color'),
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
    },
    {
        'key': 'CARET_SIZE',
        'type': 'float',
        'fallback_value': 0.04,  # GTK's default
        'display_name': _('Caret aspect ratio'),
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
    },

    {
        'type': 'separator',
        'display_name': _('Other options'),
    },
    {
        'key': 'GNOME_SHELL_PANEL_OPACITY',
        'type': 'float',
        'fallback_value': 0.6,
        'max_value': 1.0,
        'display_name': _('Gnome Shell panel opacity'),
        'value_filter': {
            'THEME_STYLE': 'materia'
        },
    },
    {
        'key': 'UNITY_DEFAULT_LAUNCHER_STYLE',
        'type': 'bool',
        'fallback_value': False,
        'display_name': _('(Unity) Use default launcher style'),
        'value_filter': {
            'THEME_STYLE': 'oomox'
        },
    },
]
