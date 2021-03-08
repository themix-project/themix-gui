# -*- coding: utf-8 -*-
import os
import sys
import re
import shutil

from .i18n import _
from .config import TERMINAL_TEMPLATE_DIR
from .color import (
    SMALLEST_DIFF, ColorDiff, is_dark,
    hex_to_int, color_list_from_hex, color_hex_from_list, hex_darker,
    int_list_from_hex,
)


if sys.version_info.minor >= 5:
    from typing import TYPE_CHECKING  # pylint: disable=wrong-import-order
    if TYPE_CHECKING:
        # pylint: disable=ungrouped-imports
        from typing import Dict  # noqa


RED = 0
GREEN = 1
BLUE = 2


def find_closest_color_key(color_hex, colors_hex, highlight=True):
    smallest_diff = SMALLEST_DIFF
    smallest_key = None
    highlight_keys = ["color{}".format(i) for i in range(8, 15 + 1)]
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
    chr(i) for i in range(ord('a'), ord('f') + 1)
] + [
    str(i) for i in range(10)
]


def import_xcolors(path):
    hex_colors = {}
    with open(os.path.expanduser(path)) as file_object:
        for line in file_object.read().split('\n'):
            if line.strip().startswith('!'):
                continue
            pair = list(s.strip() for s in line.split(':'))
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


def generate_theme_from_hint(  # pylint: disable=too-many-arguments
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


def get_all_colors_from_oomox_colorscheme(palette):
    # pylint:disable=bad-option-value,import-outside-toplevel
    from .theme_model import THEME_MODEL

    all_colors = []
    for section_name, section in THEME_MODEL.items():
        if section_name == 'terminal':
            continue
        for theme_model_item in section:
            if theme_model_item.get('type') != 'color':
                continue
            color_name = theme_model_item.get('key')
            if not color_name:
                continue
            color_value = palette.get(theme_model_item['key'])
            if not color_value or color_value in all_colors:
                continue
            all_colors.append(color_value)
    return all_colors


class ContinueNext(Exception):
    pass


# @TODO:
# These two functions are temporary until progressbar API won't be implemented in UI
def get_term_width():
    return shutil.get_terminal_size((80, 80)).columns


class ProgressBar():

    message = None
    print_ratio = None
    index = 0
    progress = 0

    LEFT_DECORATION = '['
    RIGHT_DECORATION = ']'
    # EMPTY = '-'
    # FULL = '#'

    def __init__(self, length, message=None):
        message = message or str(length)
        self.message = message
        width = (
            get_term_width() - len(message) -
            len(self.LEFT_DECORATION) - len(self.RIGHT_DECORATION)
        )
        self.print_ratio = length / width
        # sys.stderr.write(message)
        # sys.stderr.write(self.LEFT_DECORATION + self.EMPTY * width + self.RIGHT_DECORATION)
        # sys.stderr.write('{}[\bb'.format(chr(27)) * (width + len(self.RIGHT_DECORATION)))
        # sys.stderr.flush()

    def update(self):
        self.index += 1
        if self.index / self.print_ratio > self.progress:
            self.progress += 1
            # sys.stderr.write(self.FULL)
            # sys.stderr.flush()

    def __enter__(self):
        return self.update

    # def __exit__(self, *exc_details):
        # sys.stderr.write('\n')
# ######## END


def sort_by_saturation(c):
    # pylint: disable=invalid-name
    return abs(c[0]-c[1])+abs(c[0]-c[2]) + \
        abs(c[1]-c[0])+abs(c[1]-c[2]) + \
        abs(c[2]-c[1])+abs(c[2]-c[0])


def get_grayest_colors(palette):
    list_of_colors = [[hex_to_int(s) for s in color_list_from_hex(c)] for c in palette]
    saturation_list = sorted(
        list_of_colors,
        key=sort_by_saturation
    )
    gray_colors = saturation_list[:(len(saturation_list)//3)]
    gray_colors.sort(key=sum)
    gray_colors = [color_hex_from_list(c) for c in gray_colors]
    return gray_colors


def get_lightness(theme_color):
    return sum(int_list_from_hex(theme_color))


def _generate_theme_from_full_palette(
        result_callback,
        reference_colors, all_colors, theme_bg,
        accuracy=None, extend_palette=False,
):  # noqa  pylint: disable=invalid-name,too-many-nested-blocks,too-many-locals,too-many-statements,too-many-branches,too-many-arguments
    hex_colors = reference_colors
    # @TODO: refactor it some day :3

    # how far should be the colors to be counted as similar (0 .. 255*3)
    # DIFF_MARGIN = 30
    DIFF_MARGIN = 60

    # criterias to recognize bright colors (0 .. 255*3)
    is_dark_bg = is_dark(theme_bg)

    max_possible_lightness = 255 * 3
    # @TODO: use real lightness from HSV or Lab color model
    lightness_delta = sum(int_list_from_hex(theme_bg)) * (1 if is_dark_bg else -1) + \
        max_possible_lightness // 6
    min_lightness = max_possible_lightness // 38
    max_lightness = max_possible_lightness - min_lightness
    if is_dark_bg:
        min_lightness = lightness_delta
    else:
        max_lightness = max_possible_lightness - lightness_delta
    # BRIGHTNESS_MARGIN = 20

    # 1 means similarity to template the same important as mathing color palette
    # SIMILARITY_IMPORTANCE = 2
    SIMILARITY_IMPORTANCE = 2.5

    accuracy = accuracy or 0x20
    hex_colors_as_color_lists = {
        key: [
            hex_to_int(s) for s in color_list_from_hex(value)
        ] for key, value in hex_colors.items()
    }
    if extend_palette:
        for color in all_colors[:]:
            for i in (20, 40, 60):
                all_colors.append(hex_darker(color, i))
                all_colors.append(hex_darker(color, -i))

    grayest_colors = get_grayest_colors(all_colors)
    bright_colors = set(all_colors)
    bright_colors.difference_update(grayest_colors)
    bright_colors = list(bright_colors)

    bright_colors_as_color_lists = [
        [
            hex_to_int(s) for s in color_list_from_hex(value)
        ] for value in bright_colors
    ]

    START = [-0xff, -0xff, -0xff]
    END = [0xff, 0xff, 0xff]
    best_diff_color_values = [0, 0, 0]
    biggest_number_of_similar = None
    prev_biggest_number_of_similar = 'not_found'
    best_result = None

    _debug_iteration_counter = 0

    while accuracy > 0:
        _debug_iteration_counter += 1
        # print()
        # print(('ITERATION', _debug_iteration_counter))
        progress = ProgressBar(
            length=((int(abs(START[0] - END[0])/accuracy) + 2) ** 3)
        )
        red = START[RED]
        while red < END[RED] + accuracy:
            green = START[GREEN]
            while green < END[GREEN] + accuracy:
                blue = START[BLUE]
                while blue < END[BLUE] + accuracy:
                    try:

                        color_list = [red, green, blue]
                        modified_colors = {}
                        for key, value in hex_colors_as_color_lists.items():
                            if not key.startswith('color'):
                                continue
                            new_value = value[:]
                            for i in range(3):
                                new_value[i] = min(
                                    255,
                                    max(
                                        0,
                                        new_value[i] + (red, green, blue)[i]
                                    )
                                )
                            if key not in ['color0', 'color7', 'color8', 'color15']:
                                if not min_lightness <= sum(new_value) <= max_lightness:
                                    raise ContinueNext()
                            modified_colors[key] = new_value

                        num_of_similar = 0
                        for modified_color in modified_colors.values():
                            for bright_color in bright_colors_as_color_lists:
                                abs_diff = 0
                                for i in range(3):
                                    abs_diff += abs(modified_color[i] - bright_color[i])
                                if abs_diff < DIFF_MARGIN:
                                    num_of_similar += 1

                        similarity_to_reference = (
                            255*3 - sum([abs(c) for c in color_list]) * SIMILARITY_IMPORTANCE
                        ) / (255*3)
                        num_of_similar *= similarity_to_reference

                        if (
                                biggest_number_of_similar is None
                        ) or (
                            num_of_similar > biggest_number_of_similar
                        ):
                            biggest_number_of_similar = num_of_similar
                            best_result = modified_colors
                            best_diff_color_values[RED] = red
                            best_diff_color_values[GREEN] = green
                            best_diff_color_values[BLUE] = blue

                    except ContinueNext:
                        pass
                    progress.update()
                    blue += accuracy
                green += accuracy
            red += accuracy

        if biggest_number_of_similar == prev_biggest_number_of_similar:
            # print('good enough')
            break
        prev_biggest_number_of_similar = biggest_number_of_similar
        for i in range(3):
            START[i] = max(best_diff_color_values[i] - accuracy, -255)
            END[i] = min(best_diff_color_values[i] + accuracy, 255)
        accuracy = round(accuracy / 2)
        # print(('DEEPER!', accuracy))

    # from fabulous.color import bg256
    # for bright_color in bright_colors:
    #     print(bg256(bright_color, bright_color))

    modified_colors = {
        key: color_hex_from_list(c)
        for key, c in best_result.items()
    }
    # return modified_colors
    result_callback(modified_colors)


_FULL_PALETTE_CACHE = {}  # type: Dict[str, Dict[str, str]]


def generate_theme_from_full_palette(
        palette, theme_bg, theme_fg, template_path,
        app, result_callback,
        auto_swap_colors=True, accuracy=None, extend_palette=None,
        **kwargs
):  # pylint: disable=invalid-name,too-many-arguments,too-many-locals

    reference_colors = import_xcolors(template_path)

    if auto_swap_colors:
        need_light_bg = (
            get_lightness(reference_colors['background']) >
            get_lightness(reference_colors['foreground'])
        )
        have_light_bg = (
            get_lightness(theme_bg) >
            get_lightness(theme_fg)
        )
        if (
                have_light_bg and not need_light_bg
        ) or (
            not have_light_bg and need_light_bg
        ):
            theme_bg, theme_fg = theme_fg, theme_bg

    all_colors = sorted(get_all_colors_from_oomox_colorscheme(palette))
    cache_id = str(
        [
            kwargs[name] for name in sorted(kwargs, key=lambda x: x[0])
        ] + all_colors
    ) + template_path + theme_bg + str(accuracy) + str(extend_palette)

    if cache_id in _FULL_PALETTE_CACHE:
        _generate_theme_from_full_palette_callback(
            cache_id, theme_bg, theme_fg, result_callback
        )
    else:
        def _callback(generated_colors):
            _FULL_PALETTE_CACHE[cache_id] = generated_colors
            _generate_theme_from_full_palette_callback(
                cache_id, theme_bg, theme_fg, result_callback
            )
        # from time import time
        # before = time()
        app.disable(_("Generating terminal palette…"))
        app.schedule_task(
            _generate_theme_from_full_palette,
            _callback,
            reference_colors,
            all_colors,
            theme_bg,
            accuracy,
            extend_palette,
        )
        app.enable()
        # print(time() - before)


def _generate_theme_from_full_palette_callback(cache_id, theme_bg, theme_fg, result_callback):
    modified_colors = {}
    modified_colors.update(_FULL_PALETTE_CACHE[cache_id])
    modified_colors["background"] = theme_bg
    modified_colors["foreground"] = theme_fg
    result_callback(modified_colors)


def _generate_themes_from_oomox(
        original_colorscheme,
        app, result_callback,
):
    colorscheme = {}
    colorscheme.update(original_colorscheme)
    term_colorscheme = None

    def _callback(term_colorscheme):
        _generate_themes_from_oomox_callback(colorscheme, term_colorscheme, result_callback)

    if colorscheme['TERMINAL_THEME_MODE'] in ('auto', ):
        colorscheme["TERMINAL_ACCENT_COLOR"] = colorscheme["SEL_BG"]
        colorscheme["TERMINAL_BACKGROUND"] = colorscheme["TXT_BG"]
        colorscheme["TERMINAL_FOREGROUND"] = colorscheme["TXT_FG"]
        if colorscheme["THEME_STYLE"] == "materia":
            colorscheme["TERMINAL_FOREGROUND"] = colorscheme["FG"]
    if colorscheme['TERMINAL_THEME_MODE'] == 'smarty':
        generate_theme_from_full_palette(
            template_path=os.path.join(
                TERMINAL_TEMPLATE_DIR, colorscheme["TERMINAL_BASE_TEMPLATE"]
            ),
            palette=colorscheme,
            theme_bg=colorscheme["TERMINAL_BACKGROUND"],
            theme_fg=colorscheme["TERMINAL_FOREGROUND"],
            auto_swap_colors=colorscheme["TERMINAL_THEME_AUTO_BGFG"],
            extend_palette=colorscheme["TERMINAL_THEME_EXTEND_PALETTE"],
            accuracy=255+8-colorscheme.get("TERMINAL_THEME_ACCURACY"),
            app=app, result_callback=_callback,
        )
        return
    if colorscheme['TERMINAL_THEME_MODE'] in ('basic', 'auto'):
        term_colorscheme = generate_theme_from_hint(
            template_path=os.path.join(
                TERMINAL_TEMPLATE_DIR, colorscheme["TERMINAL_BASE_TEMPLATE"]
            ),
            theme_color=colorscheme["TERMINAL_ACCENT_COLOR"],
            theme_bg=colorscheme["TERMINAL_BACKGROUND"],
            theme_fg=colorscheme["TERMINAL_FOREGROUND"],
            theme_hint=None,
            auto_swap_colors=colorscheme["TERMINAL_THEME_AUTO_BGFG"]
        )
    else:
        term_colorscheme = convert_oomox_theme_to_xrdb(colorscheme)
    _callback(term_colorscheme)


def _generate_themes_from_oomox_callback(
        colorscheme, term_colorscheme, result_callback,
):
    for i in range(16):
        theme_key = "TERMINAL_COLOR{}".format(i)
        term_key = "color{}".format(i)
        colorscheme[theme_key] = term_colorscheme[term_key]
    if colorscheme['TERMINAL_THEME_MODE'] != 'manual':
        colorscheme['TERMINAL_BACKGROUND'] = term_colorscheme['background']
        colorscheme['TERMINAL_FOREGROUND'] = term_colorscheme['foreground']
    result_callback(colorscheme)


def convert_oomox_theme_to_xrdb(colorscheme):
    term_colorscheme = {}
    for i in range(16):
        theme_key = "TERMINAL_COLOR{}".format(i)
        term_key = "color{}".format(i)
        if colorscheme.get(theme_key):
            term_colorscheme[term_key] = \
                    colorscheme[theme_key]
    term_colorscheme['background'] = colorscheme['TERMINAL_BACKGROUND']
    term_colorscheme['foreground'] = colorscheme['TERMINAL_FOREGROUND']
    return term_colorscheme


def generate_xrdb_theme_from_oomox(colorscheme):
    return convert_oomox_theme_to_xrdb(colorscheme)


def generate_terminal_colors_for_oomox(
        colorscheme,
        app, result_callback,
):
    _generate_themes_from_oomox(
        colorscheme,
        app=app, result_callback=result_callback,
    )


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
    term_colorscheme = generate_theme_from_hint(
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
