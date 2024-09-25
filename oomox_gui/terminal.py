import operator
import os
import shutil
import sys
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from .color import (
    SMALLEST_DIFF,
    ColorDiff,
    color_hex_from_list,
    color_list_from_hex,
    hex_darker,
    hex_to_int,
    int_list_from_hex,
    is_dark,
)
from .config import DEFAULT_ENCODING, TERMINAL_TEMPLATE_DIR
from .i18n import translate
from .theme_model import get_theme_model

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import (
        Any,
        Final,
    )

    from .main import OomoxApplicationWindow
    from .theme_file import ThemeT


RED: "Final" = 0
GREEN: "Final" = 1
BLUE: "Final" = 2
VALID_COLOR_CHARS: "Final" = [
    chr(i) for i in range(ord("a"), ord("f") + 1)
] + [
    str(i) for i in range(10)
]


TerminalThemeT = dict[str, str]


def find_closest_color_key(
        color_hex: str,
        colors_hex: TerminalThemeT,
        *,
        highlight: bool = True,
) -> tuple[str | None, ColorDiff]:
    smallest_diff = SMALLEST_DIFF
    smallest_key = None
    highlight_keys = [f"color{i}" for i in range(8, 15 + 1)]
    for preset_key, preset_color in colors_hex.items():
        if (
            (
                highlight
            ) and (
                "color" not in preset_key
            )
        ) or (
            preset_key not in highlight_keys
        ):
            continue
        diff = ColorDiff(preset_color, color_hex)
        # if diff.minabs < smallest_diff.minabs:
        if diff.abs_sum < smallest_diff.abs_sum:
            smallest_diff = diff
            smallest_key = preset_key
    return smallest_key, smallest_diff


def import_xcolors(path: str) -> dict[str, str]:
    hex_colors = {}
    text = Path(
        os.path.expanduser(path),
    ).read_text(encoding=DEFAULT_ENCODING)
    for line in text.split("\n"):
        if line.strip().startswith("!"):
            continue
        pair = [s.strip() for s in line.split(":")]
        if len(pair) < 2:  # noqa: PLR2004
            continue
        key, value = pair
        key = key.replace("*", "")
        value = value.replace("#", "").lower()
        for char in value:
            if char not in VALID_COLOR_CHARS:
                break
        else:
            hex_colors[key] = value
    return hex_colors


def generate_theme_from_hint(
        template_path: str,
        theme_color: str,
        theme_bg: str,
        theme_fg: str,
        theme_hint: str | None = None,
        *,
        auto_swap_colors: bool = True,
) -> TerminalThemeT:
    hex_colors = import_xcolors(template_path)
    if auto_swap_colors and (
            is_dark(theme_bg) != is_dark(hex_colors["background"])
    ):
        theme_bg, theme_fg = theme_fg, theme_bg
    _closest_key: str | None
    diff: ColorDiff
    if theme_hint:
        _closest_key = theme_hint
        diff = ColorDiff(hex_colors[theme_hint], theme_color)
    else:
        _closest_key, diff = find_closest_color_key(
            theme_color, hex_colors, highlight=False,
        )
    modified_colors = {
        key: diff.apply_to(value)
        for key, value in hex_colors.items()
    }
    modified_colors["background"] = theme_bg
    modified_colors["foreground"] = theme_fg
    for source, destinations in {
            "background": ("color0", "color8"),
            "foreground": ("color7", "color15"),
    }.items():
        for key in destinations:
            modified_colors[key] = ColorDiff(
                hex_colors[source], hex_colors[key],
            ).apply_to(
                modified_colors[source],
            )
    return modified_colors


def get_all_colors_from_oomox_colorscheme(palette: "ThemeT") -> list[str]:
    all_colors: list[str] = []
    for section_name, section in get_theme_model().items():
        if section_name == "terminal":
            continue
        for theme_model_item in section:
            if theme_model_item.get("type") != "color":
                continue
            color_name = theme_model_item.get("key")
            if not color_name:
                continue
            color_value = palette.get(theme_model_item["key"])
            if not color_value or color_value in all_colors:
                continue
            all_colors.append(color_value)  # type: ignore[arg-type]
    return all_colors


class ContinueNext(Exception):  # noqa: N818
    pass


# @TODO:
# get_term_width() and ProgressBar() are temporary until progressbar API won't be implemented in UI:
def get_term_width() -> int:
    return shutil.get_terminal_size((80, 80)).columns


class ProgressBar:

    message: str
    print_ratio: float
    index = 0
    progress = 0

    LEFT_DECORATION = "["
    RIGHT_DECORATION = "]"

    def __init__(self, length: int, message: str | None = None) -> None:
        message = message or str(length)
        self.message = message
        width = (
            get_term_width() - len(message) -
            len(self.LEFT_DECORATION) - len(self.RIGHT_DECORATION)
        )
        self.print_ratio = length / width

    def update(self) -> None:
        self.index += 1
        if self.index / self.print_ratio > self.progress:
            self.progress += 1

    def __enter__(self) -> "Callable[[], None]":
        return self.update


def sort_by_saturation(c: list[int]) -> int:
    # pylint: disable=invalid-name
    return abs(c[0] - c[1]) + abs(c[0] - c[2]) + \
        abs(c[1] - c[0]) + abs(c[1] - c[2]) + \
        abs(c[2] - c[1]) + abs(c[2] - c[0])


def get_grayest_colors(palette: list[str]) -> list[str]:
    list_of_colors = [[hex_to_int(s) for s in color_list_from_hex(c)] for c in palette]
    saturation_list = sorted(
        list_of_colors,
        key=sort_by_saturation,
    )
    gray_color_values = saturation_list[:(len(saturation_list) // 3)]
    gray_color_values.sort(key=sum)
    return [color_hex_from_list(c) for c in gray_color_values]


def get_lightness(theme_color: str) -> int:
    return sum(int_list_from_hex(theme_color))


# how far should be the colors to be counted as similar (0 .. 255*3)
# COLOR_DIFF_MARGIN = 30
COLOR_DIFF_MARGIN: "Final" = 60
# 1 means similarity to template the same important as mathing color palette
# COLOR_SIMILARITY_IMPORTANCE = 2
COLOR_SIMILARITY_IMPORTANCE: "Final" = 2.5


def _generate_theme_from_full_palette(  # pylint: disable=too-many-nested-blocks,too-many-locals,too-many-statements,too-many-branches  # noqa: E501,RUF100
        result_callback: "Callable[[TerminalThemeT], None]",
        reference_colors: dict[str, str],
        all_colors: list[str],
        theme_bg: str,
        accuracy: int | None = None,
        *,
        extend_palette: bool = False,
) -> None:
    hex_colors = reference_colors
    # @TODO: refactor it some day :3

    color_start = [-0xff, -0xff, -0xff]
    color_end = [0xff, 0xff, 0xff]

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

    accuracy = accuracy or 0x20
    hex_colors_as_color_lists = {
        key: [
            hex_to_int(s) for s in color_list_from_hex(value)
        ] for key, value in hex_colors.items()
    }
    if extend_palette:
        for color in all_colors.copy():
            for i in (20, 40, 60):
                all_colors.extend((hex_darker(color, i), hex_darker(color, -i)))

    grayest_colors = get_grayest_colors(all_colors)
    bright_colors_set = set(all_colors)
    bright_colors_set.difference_update(grayest_colors)
    bright_colors = list(bright_colors_set)

    bright_colors_as_color_lists = [
        [
            hex_to_int(s) for s in color_list_from_hex(value)
        ] for value in bright_colors
    ]

    best_diff_color_values = [0, 0, 0]
    biggest_number_of_similar: float | None = None
    prev_biggest_number_of_similar: float | None = None
    best_result = None

    _debug_iteration_counter = 0

    while accuracy > 0:
        _debug_iteration_counter += 1
        # print()
        # print(('ITERATION', _debug_iteration_counter))
        progress = ProgressBar(
            length=((int(abs(color_start[0] - color_end[0]) / accuracy) + 2) ** 3),
        )
        red = color_start[RED]
        while red < color_end[RED] + accuracy:
            green = color_start[GREEN]
            while green < color_end[GREEN] + accuracy:
                blue = color_start[BLUE]
                while blue < color_end[BLUE] + accuracy:
                    try:

                        color_list = [red, green, blue]
                        modified_colors = {}
                        for key, value in hex_colors_as_color_lists.items():
                            if not key.startswith("color"):
                                continue
                            new_value = value[:]
                            for i in range(3):
                                new_value[i] = min(
                                    255,
                                    max(
                                        0,
                                        new_value[i] + (red, green, blue)[i],
                                    ),
                                )
                            if (
                                    (key not in {"color0", "color7", "color8", "color15"})
                                    and (not min_lightness <= sum(new_value) <= max_lightness)
                            ):
                                raise ContinueNext  # noqa: TRY301
                            modified_colors[key] = new_value

                        num_of_similar = 0.0
                        for modified_color in modified_colors.values():
                            for bright_color in bright_colors_as_color_lists:
                                abs_diff = 0
                                for i in range(3):
                                    abs_diff += abs(modified_color[i] - bright_color[i])
                                if abs_diff < COLOR_DIFF_MARGIN:
                                    num_of_similar += 1

                        similarity_to_reference = (
                            255 * 3 - sum(abs(c) for c in color_list) * COLOR_SIMILARITY_IMPORTANCE
                        ) / (255 * 3)
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
            color_start[i] = max(best_diff_color_values[i] - accuracy, -255)
            color_end[i] = min(best_diff_color_values[i] + accuracy, 255)
        accuracy = round(accuracy / 2)
        # print(('DEEPER!', accuracy))

    # from fabulous.color import bg256
    # for bright_color in bright_colors:
    #     print(bg256(bright_color, bright_color))

    if not best_result:
        t_t = "Everything went wrong 🥲"
        raise RuntimeError(t_t)

    result_colors = {
        key: color_hex_from_list(c)
        for key, c in best_result.items()
    }
    # return result_colors
    result_callback(result_colors)


class FullPaletteCache:

    _cache: ClassVar[dict[str, dict[str, str]]] = {}

    @classmethod
    def get(cls, key: str) -> dict[str, str] | None:
        return cls._cache.get(key)

    @classmethod
    def put(cls, key: str, value: dict[str, str]) -> None:
        cls._cache[key] = value


def generate_theme_from_full_palette(  # pylint: disable=too-many-arguments,too-many-locals
        palette: "ThemeT",
        theme_bg: str,
        theme_fg: str,
        template_path: str,
        result_callback: "Callable[[TerminalThemeT], None]",
        *,
        auto_swap_colors: bool = True,
        accuracy: int | None = None,
        extend_palette: bool = False,
        window: "OomoxApplicationWindow | None" = None,
        **kwargs: "Any",
) -> None:

    reference_colors = import_xcolors(template_path)

    if auto_swap_colors:
        need_light_bg = (
            get_lightness(reference_colors["background"]) >
            get_lightness(reference_colors["foreground"])
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
            kwargs[name] for name in sorted(kwargs, key=operator.itemgetter(0))
        ] + all_colors,
    ) + template_path + theme_bg + str(accuracy) + str(extend_palette)

    if FullPaletteCache.get(cache_id):
        _generate_theme_from_full_palette_callback(
            cache_id, theme_bg, theme_fg, result_callback,
        )
    else:
        def _callback(generated_colors: TerminalThemeT) -> None:
            FullPaletteCache.put(cache_id, generated_colors)
            _generate_theme_from_full_palette_callback(
                cache_id, theme_bg, theme_fg, result_callback,
            )
        # from time import time
        # before = time()
        if window:
            window.disable(translate("Generating terminal palette…"))
            window.schedule_task(
                lambda: _generate_theme_from_full_palette(
                    _callback,
                    reference_colors,
                    all_colors,
                    theme_bg,
                    accuracy,
                    extend_palette=extend_palette,
                ),
            )
            window.enable()
        else:
            _generate_theme_from_full_palette(
                _callback,
                reference_colors,
                all_colors,
                theme_bg,
                accuracy,
                extend_palette=extend_palette,
            )
        # print(time() - before)


def _generate_theme_from_full_palette_callback(
        cache_id: str,
        theme_bg: str,
        theme_fg: str,
        result_callback: "Callable[[TerminalThemeT], None]",
) -> None:
    cached_palette = FullPaletteCache.get(cache_id)
    if not cached_palette:
        cant_open_palette = f"No cached palette with {cache_id=}"
        raise RuntimeError(cant_open_palette)
    modified_colors = {}
    modified_colors.update(cached_palette)
    modified_colors["background"] = theme_bg
    modified_colors["foreground"] = theme_fg
    result_callback(modified_colors)


def _generate_themes_from_oomox(
        original_colorscheme: "ThemeT",
        result_callback: "Callable[[ThemeT], None]",
        window: "OomoxApplicationWindow | None" = None,
) -> None:
    colorscheme = {}
    colorscheme.update(original_colorscheme)
    term_colorscheme = None

    def _callback(term_colorscheme: TerminalThemeT) -> None:
        _generate_themes_from_oomox_callback(colorscheme, term_colorscheme, result_callback)

    if colorscheme["TERMINAL_THEME_MODE"] == "auto":
        colorscheme["TERMINAL_ACCENT_COLOR"] = colorscheme["SEL_BG"]
        colorscheme["TERMINAL_BACKGROUND"] = colorscheme["TXT_BG"]
        colorscheme["TERMINAL_FOREGROUND"] = colorscheme["TXT_FG"]
        if colorscheme["THEME_STYLE"] == "materia":
            colorscheme["TERMINAL_FOREGROUND"] = colorscheme["FG"]

    terminal_base_template: str = colorscheme["TERMINAL_BASE_TEMPLATE"]  # type: ignore[assignment]
    terminal_theme_accuracy: int = (
        colorscheme["TERMINAL_THEME_ACCURACY"]  # type: ignore[assignment]
    )
    terminal_theme_extend_palette: bool = (
        colorscheme["TERMINAL_THEME_EXTEND_PALETTE"]  # type: ignore[assignment]
    )
    terminal_theme_auto_bgfg: bool = (
        colorscheme["TERMINAL_THEME_AUTO_BGFG"]  # type: ignore[assignment]
    )
    terminal_background: str = colorscheme["TERMINAL_BACKGROUND"]  # type: ignore[assignment]
    terminal_foreground: str = colorscheme["TERMINAL_FOREGROUND"]  # type: ignore[assignment]
    terminal_accent_color: str = colorscheme["TERMINAL_ACCENT_COLOR"]  # type: ignore[assignment]
    if colorscheme["TERMINAL_THEME_MODE"] == "smarty":
        generate_theme_from_full_palette(
            template_path=os.path.join(
                TERMINAL_TEMPLATE_DIR, terminal_base_template,
            ),
            palette=colorscheme,
            theme_bg=terminal_background,
            theme_fg=terminal_foreground,
            auto_swap_colors=terminal_theme_auto_bgfg,
            extend_palette=terminal_theme_extend_palette,
            accuracy=255 + 8 - terminal_theme_accuracy,
            window=window,
            result_callback=_callback,
        )
        return
    if colorscheme["TERMINAL_THEME_MODE"] in {"basic", "auto"}:
        term_colorscheme = generate_theme_from_hint(
            template_path=os.path.join(
                TERMINAL_TEMPLATE_DIR, terminal_base_template,
            ),
            theme_color=terminal_accent_color,
            theme_bg=terminal_background,
            theme_fg=terminal_foreground,
            theme_hint=None,
            auto_swap_colors=terminal_theme_auto_bgfg,
        )
    else:
        term_colorscheme = convert_oomox_theme_to_xrdb(colorscheme)
    _callback(term_colorscheme)


def _generate_themes_from_oomox_callback(
        colorscheme: "ThemeT",
        term_colorscheme: TerminalThemeT,
        result_callback: "Callable[[ThemeT], None]",
) -> None:
    for i in range(16):
        colorscheme[f"TERMINAL_COLOR{i}"] = term_colorscheme[f"color{i}"]
    if colorscheme["TERMINAL_THEME_MODE"] != "manual":
        colorscheme["TERMINAL_BACKGROUND"] = term_colorscheme["background"]
        colorscheme["TERMINAL_FOREGROUND"] = term_colorscheme["foreground"]
        if "cursorColor" in term_colorscheme:
            colorscheme["TERMINAL_CURSOR"] = term_colorscheme["cursorColor"]
    result_callback(colorscheme)


def convert_oomox_theme_to_xrdb(colorscheme: "ThemeT") -> TerminalThemeT:
    term_colorscheme: TerminalThemeT = {}
    for i in range(16):
        theme_key = f"TERMINAL_COLOR{i}"
        term_key = f"color{i}"
        if colorscheme.get(theme_key):
            term_colorscheme[term_key] = colorscheme[theme_key]  # type: ignore[assignment]
    term_colorscheme["background"] = colorscheme["TERMINAL_BACKGROUND"]  # type: ignore[assignment]
    term_colorscheme["foreground"] = colorscheme["TERMINAL_FOREGROUND"]  # type: ignore[assignment]
    term_colorscheme["cursorColor"] = colorscheme["TERMINAL_CURSOR"]  # type: ignore[assignment]
    return term_colorscheme


def generate_xrdb_theme_from_oomox(colorscheme: "ThemeT") -> TerminalThemeT:
    return convert_oomox_theme_to_xrdb(colorscheme)


def generate_terminal_colors_for_oomox(
        colorscheme: "ThemeT",
        result_callback: "Callable[[ThemeT], None]",
        window: "OomoxApplicationWindow | None" = None,
) -> None:
    _generate_themes_from_oomox(
        colorscheme,
        window=window,
        result_callback=result_callback,
    )


CLI_MIN_ARGS_NUM: "Final" = 5


class CliArgs:
    THEME_HINT: "Final" = 5
    AUTO_SWAP_COLORS: "Final" = 6


def cli() -> None:
    args = sys.argv
    if len(args) < CLI_MIN_ARGS_NUM:
        print(
            f"Usage: {sys.argv[0]} "
            "TEMPLATE_PATH ACCENT_COLOR BG FG "
            "[ACCENT_KEY_NAME] [AUTO_DETECT_FG_BG=YES]",
        )
        sys.exit(1)
    template_path = args[1]
    theme_color = args[2]
    theme_bg = args[3]
    theme_fg = args[4]
    theme_hint = args[CliArgs.THEME_HINT] if len(args) > CliArgs.THEME_HINT else None
    auto_swap_colors = (
        (args[CliArgs.AUTO_SWAP_COLORS] not in {"y", "yes", "true", "1"})
        if len(args) > CliArgs.AUTO_SWAP_COLORS else
        False
    )
    term_colorscheme = generate_theme_from_hint(
        template_path=template_path,
        theme_color=theme_color,
        theme_bg=theme_bg,
        theme_fg=theme_fg,
        theme_hint=theme_hint,
        auto_swap_colors=auto_swap_colors,
    )
    print(term_colorscheme)


if __name__ == "__main__":
    cli()
