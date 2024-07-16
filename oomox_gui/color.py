import operator
from collections.abc import Sequence
from typing import TYPE_CHECKING, Annotated

from gi.repository import Gdk

if TYPE_CHECKING:
    from typing import Final


class RGB:
    length: "Final" = 3
    RED: "Final" = 0
    GREEN: "Final" = 1
    BLUE: "Final" = 2
    hex_size = 255


HexColor = Annotated[str, 6]

IntColor = Annotated[Sequence[int], RGB.length]


def hex_to_int(text: "HexColor") -> int:
    return int(f"0x{text}", 0)


def int_to_hex(num: float) -> "HexColor":
    return f"{int(num):02x}"


def color_list_from_hex(color_text: "HexColor") -> "tuple[str, str, str]":
    result: tuple[str, str, str]
    result = operator.itemgetter(slice(2), slice(2, 4), slice(4, 6))(color_text)
    return result


def int_list_from_hex(color_text: "HexColor") -> "IntColor":
    result = [hex_to_int(c) for c in color_list_from_hex(color_text)]
    if len(result) != RGB.length:
        raise TypeError(color_text)
    return (result[RGB.RED], result[RGB.GREEN], result[RGB.BLUE])


def color_hex_from_list(color_list: "IntColor") -> "HexColor":
    return "".join([int_to_hex(i) for i in color_list])


MIN_LIGHTNESS: "Final" = 0
MAX_LIGHTNESS: "Final" = 1


def hex_lightness(color_text: "HexColor") -> Annotated[float, MIN_LIGHTNESS, MAX_LIGHTNESS]:
    # @TODO: use real lightness from HSV or Lab color model
    return sum(
        hex_to_int(channel_text)
        for channel_text in color_list_from_hex(color_text)
    ) / (RGB.hex_size * RGB.length)


def is_dark(color_text: "HexColor") -> bool:
    return hex_lightness(color_text) < (MAX_LIGHTNESS / 2)


def hex_darker(color_text: "HexColor", darken_amount: int = 10) -> "HexColor":
    # @TODO: use real lightness from HSV or Lab color model?
    return color_hex_from_list([
        max(min(hex_to_int(channel_text) - darken_amount, RGB.hex_size), 0)
        for channel_text in color_list_from_hex(color_text)
    ])


RGB_CHANNELS: "Final[list[str]]" = ["r", "g", "b"]


class ColorDiff:
    r: int
    g: int
    b: int

    @property
    def color_list(self) -> "IntColor":
        return [self.r, self.g, self.b]

    @property
    def abs_list(self) -> "IntColor":
        return [abs(c) for c in self.color_list]

    @property
    def abs_sum(self) -> int:
        return sum(self.abs_list)

    @property
    def sat(self) -> int:
        r, g, b = self.abs_list
        return abs(r - g) + abs(r - b) + abs(g - r) + abs(g - b) + abs(b - g) + abs(b - r)

    def __repr__(self) -> str:
        return str(self.abs_sum)

    def __init__(self, theme_color_1: "HexColor", theme_color_2: "HexColor") -> None:
        color_list_1 = color_list_from_hex(theme_color_1)
        color_list_2 = color_list_from_hex(theme_color_2)
        for channel_index, channel_1_text in enumerate(color_list_1):
            channel_1 = hex_to_int(channel_1_text)
            channel_2 = hex_to_int(color_list_2[channel_index])
            setattr(self, RGB_CHANNELS[channel_index], channel_1 - channel_2)

    def apply_to(self, color_text: "HexColor") -> "HexColor":
        color_list = color_list_from_hex(color_text)
        result = ""
        for channel_index, channel_text in enumerate(color_list):
            channel = hex_to_int(channel_text)
            int_result = channel - getattr(self, RGB_CHANNELS[channel_index])
            int_result = max(int_result, 0)
            int_result = min(int_result, RGB.hex_size)
            result += int_to_hex(int_result)
        return result


SMALLEST_DIFF: "Final" = ColorDiff("000000", "ffffff")


def find_closest_color(
        color_hex: "HexColor",
        colors_hex: "Sequence[HexColor]",
        min_lightness: int = MIN_LIGHTNESS,
        max_lightness: int = RGB.hex_size * RGB.length,
) -> "tuple[None, None] | tuple[HexColor, ColorDiff]":
    smallest_diff = SMALLEST_DIFF
    closest_color = None
    if not colors_hex:
        return None, None
    if len(colors_hex) == 1:
        return colors_hex[0], ColorDiff(colors_hex[0], color_hex)
    for preset_color in colors_hex:
        diff = ColorDiff(preset_color, color_hex)
        # @TODO: use real lightness from HSV or Lab color model
        lightness = (sum(int_list_from_hex(preset_color)))
        if (diff.abs_sum < smallest_diff.abs_sum) and (max_lightness >= lightness >= min_lightness):
            smallest_diff = diff
            closest_color = preset_color
    if not closest_color:
        return find_closest_color(color_hex, colors_hex, min_lightness // 2, max_lightness * 2)
    return closest_color, smallest_diff


def convert_theme_color_to_gdk(theme_color: "HexColor") -> Gdk.RGBA:
    gdk_color = Gdk.RGBA()
    gdk_color.parse("#" + theme_color)
    return gdk_color


def convert_gdk_to_theme_color(gdk_color: Gdk.RGBA) -> "HexColor":
    return "".join([
        int_to_hex(n * RGB.hex_size)
        for n in (gdk_color.red, gdk_color.green, gdk_color.blue)
    ])


def mix_gdk_colors(gdk_color_1: Gdk.RGBA, gdk_color_2: Gdk.RGBA, ratio: float) -> Gdk.RGBA:
    result_gdk_color = Gdk.RGBA()
    for attr in ("red", "green", "blue", "alpha"):
        setattr(
            result_gdk_color, attr, (
                getattr(gdk_color_1, attr) * ratio +
                getattr(gdk_color_2, attr) * (1 - ratio)
            ),
        )
    return result_gdk_color


def mix_theme_colors(
        theme_color_1: "HexColor", theme_color_2: "HexColor", ratio: float,
) -> "HexColor":
    return convert_gdk_to_theme_color(
        mix_gdk_colors(
            convert_theme_color_to_gdk(theme_color_1),
            convert_theme_color_to_gdk(theme_color_2),
            ratio=ratio,
        ),
    )
