import os
import sys
import re

from .config import TERMINAL_TEMPLATE_DIR
from .color import SMALLEST_DIFF, ColorDiff, is_dark


def find_closest_color_key(color_hex, colors_hex, highlight=True):
    smallest_diff = SMALLEST_DIFF
    smallest_key = None
    highlight_keys = ["color{}".format(i) for i in range(8, 15+1)]
    for preset_key, preset_color in colors_hex.items():
        if (
                highlight
        ) and (
            "color" not in preset_key
        ) or (
            preset_key not in highlight_keys
        ):
            continue
        diff = ColorDiff(preset_color, color_hex)
        # if diff.minabs < smallest_diff.minabs:
        if diff.abs < smallest_diff.abs:
            smallest_diff = diff
            smallest_key = preset_key
    return smallest_key, smallest_diff


VALID_COLOR_CHARS = [
    chr(i) for i in range(ord('a'), ord('f')+1)
] + [
    str(i) for i in range(10)
]


def import_xcolors(path):
    hex_colors = {}
    with open(os.path.expanduser(path)) as file_object:
        for line in file_object.read().split('\n'):
            if line.strip().startswith('!'):
                continue
            pair = list([s.strip() for s in line.split(':')])
            if len(pair) < 2:
                continue
            key, value = pair
            key = key.replace('*', '')
            value = value.replace('#', '').lower()
            for char in value:
                if char not in VALID_COLOR_CHARS:
                    break
            else:
                hex_colors[key] = value
    return hex_colors


def generate_theme(  # pylint: disable=too-many-arguments
        template_path, theme_color, theme_bg, theme_fg,
        theme_hint=None, auto_swap_colors=True
):
    hex_colors = import_xcolors(template_path)
    if auto_swap_colors and (
            is_dark(theme_bg) != is_dark(hex_colors['background'])
    ):
        theme_bg, theme_fg = theme_fg, theme_bg
    _closest_key, diff = None, None
    if theme_hint:
        _closest_key = theme_hint
        diff = ColorDiff(hex_colors[theme_hint], theme_color)
    else:
        _closest_key, diff = find_closest_color_key(
            theme_color, hex_colors, highlight=False
        )
    modified_colors = {
        key: diff.apply_to(value)
        for key, value in hex_colors.items()
    }
    modified_colors["background"] = theme_bg
    modified_colors["foreground"] = theme_fg
    for source, destinations in {
            "background": ("color0", "color8",),
            "foreground": ("color7", "color15",),
    }.items():
        for key in destinations:
            modified_colors[key] = ColorDiff(
                hex_colors[source], hex_colors[key]
            ).apply_to(
                modified_colors[source]
            )
    return modified_colors


def generate_themes_from_oomox(original_colorscheme):
    colorscheme = {}
    colorscheme.update(original_colorscheme)
    if colorscheme['TERMINAL_THEME_MODE'] == 'auto':
        colorscheme["TERMINAL_ACCENT_COLOR"] = colorscheme["SEL_BG"]
        colorscheme["TERMINAL_BACKGROUND"] = colorscheme["TXT_BG"]
        colorscheme["TERMINAL_FOREGROUND"] = colorscheme["TXT_FG"]
    term_colorscheme = generate_theme(
        template_path=os.path.join(
            TERMINAL_TEMPLATE_DIR, colorscheme["TERMINAL_BASE_TEMPLATE"]
        ),
        theme_color=colorscheme["TERMINAL_ACCENT_COLOR"],
        theme_bg=colorscheme["TERMINAL_BACKGROUND"],
        theme_fg=colorscheme["TERMINAL_FOREGROUND"],
        theme_hint=None,
        auto_swap_colors=colorscheme["TERMINAL_THEME_AUTO_BGFG"]
    )
    for i in range(16):
        theme_key = "TERMINAL_COLOR{}".format(i)
        term_key = "color{}".format(i)
        if colorscheme.get(theme_key):
            term_colorscheme[term_key] = \
                    colorscheme[theme_key]
        else:
            colorscheme[theme_key] = \
                term_colorscheme[term_key]
    return term_colorscheme, colorscheme


def generate_xrdb_theme_from_oomox(colorscheme):
    term_colorscheme, _ = generate_themes_from_oomox(colorscheme)
    return term_colorscheme


def generate_terminal_colors_for_oomox(colorscheme):  # pylint: disable=invalid-name
    _, new_oomox_colorscheme = generate_themes_from_oomox(colorscheme)
    return new_oomox_colorscheme


def natural_sort(list_to_sort):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return [convert(c) for c in re.split('([0-9]+)', key)]

    return sorted(list_to_sort, key=alphanum_key)


def generate_xresources(colorscheme):
    color_keys = colorscheme.keys()
    color_regex = re.compile('color[0-9]')
    return '\n'.join([
        "*{key}:  #{value}".format(
            key=key, value=colorscheme[key]
        )
        for key in (
            sorted([
                key for key in color_keys
                if not color_regex.match(key)
            ]) +
            natural_sort([
                key for key in color_keys
                if color_regex.match(key)
            ])
        )
    ])


def cli():
    args = sys.argv
    if len(args) < 5:
        print(
            "Usage: {} "
            "TEMPLATE_PATH ACCENT_COLOR BG FG "
            "[ACCENT_KEY_NAME] [AUTO_DETECT_FG_BG=YES]".format(
                sys.argv[0]
            )
        )
        sys.exit(1)
    template_path = args[1]
    theme_color = args[2]
    theme_bg = args[3]
    theme_fg = args[4]
    theme_hint = args[5] if len(args) > 5 else None
    auto_swap_colors = (args[6] not in ["y", "yes", "true", "1"]) \
        if len(args) > 6 else None
    term_colorscheme = generate_theme(
        template_path=template_path,
        theme_color=theme_color,
        theme_bg=theme_bg,
        theme_fg=theme_fg,
        theme_hint=theme_hint,
        auto_swap_colors=auto_swap_colors,
    )
    print(generate_xresources(term_colorscheme))


if __name__ == '__main__':
    cli()
