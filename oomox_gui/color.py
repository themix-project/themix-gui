from gi.repository import Gdk


def hex_to_int(text):
    return int("0x{}".format(text), 0)


def int_to_hex(myint):
    return "{0:02x}".format(int(myint))


def color_list_from_hex(color_text):
    return [color_text[:2], color_text[2:4], color_text[4:]]


def int_list_from_hex(color_text):
    return [hex_to_int(c) for c in color_list_from_hex(color_text)]


def color_hex_from_list(color_list):
    return ''.join([int_to_hex(i) for i in color_list])


def hex_lightness(color_text):
    # @TODO: use real lightness from HSV or Lab color model
    return sum([
        hex_to_int(channel_text)
        for channel_text in color_list_from_hex(color_text)
    ]) / 765


def is_dark(color_text):
    return hex_lightness(color_text) < 0.5


def hex_darker(color_text, darken_amount=10):
    # @TODO: use real lightness from HSV or Lab color model?
    return color_hex_from_list([
        max(min(hex_to_int(channel_text) - darken_amount, 255), 0)
        for channel_text in color_list_from_hex(color_text)
    ])


class ColorDiff():
    r = None  # pylint: disable=invalid-name
    g = None  # pylint: disable=invalid-name
    b = None  # pylint: disable=invalid-name

    @property
    def list(self):
        return [self.r, self.g, self.b]

    @property
    def abs_list(self):
        return [abs(c) for c in self.list]

    @property
    def abs(self):
        return sum(self.abs_list)

    @property
    def sat(self):
        r, g, b = self.abs_list  # pylint: disable=invalid-name
        return abs(r-g)+abs(r-b) + abs(g-r)+abs(g-b) + abs(b-g)+abs(b-r)

    def __repr__(self):
        return str(self.abs)

    channels = ['r', 'g', 'b']

    def __init__(self, theme_color_1, theme_color_2):
        color_list_1 = color_list_from_hex(theme_color_1)
        color_list_2 = color_list_from_hex(theme_color_2)
        for channel_index, channel_1_text in enumerate(color_list_1):
            channel_1 = hex_to_int(channel_1_text)
            channel_2 = hex_to_int(color_list_2[channel_index])
            setattr(self, self.channels[channel_index], channel_1-channel_2)

    def apply_to(self, color_text):
        color_list = color_list_from_hex(color_text)
        result = ''
        for channel_index, channel_text in enumerate(color_list):
            channel = hex_to_int(channel_text)
            int_result = channel - getattr(self, self.channels[channel_index])
            if int_result < 0:
                int_result = 0
            if int_result > 255:
                int_result = 255
            result += int_to_hex(int_result)
        return result


SMALLEST_DIFF = ColorDiff("000000", "ffffff")


def find_closest_color(color_hex, colors_hex, min_lightness=0, max_lightness=255*3):
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
        if (diff.abs < smallest_diff.abs) and (max_lightness >= lightness >= min_lightness):
            smallest_diff = diff
            closest_color = preset_color
    if not closest_color:
        return find_closest_color(color_hex, colors_hex, min_lightness//2, max_lightness*2)
    return closest_color, smallest_diff


def convert_theme_color_to_gdk(theme_color):
    gdk_color = Gdk.RGBA()
    gdk_color.parse("#" + theme_color)
    return gdk_color


def convert_gdk_to_theme_color(gdk_color):
    return "".join([
        int_to_hex(n * 255)
        for n in (gdk_color.red, gdk_color.green, gdk_color.blue)
    ])


def mix_gdk_colors(gdk_color_1, gdk_color_2, ratio):
    result_gdk_color = Gdk.RGBA()
    for attr in ('red', 'green', 'blue', 'alpha'):
        setattr(
            result_gdk_color, attr, (
                getattr(gdk_color_1, attr) * ratio +
                getattr(gdk_color_2, attr) * (1 - ratio)
            )
        )
    return result_gdk_color


def mix_theme_colors(theme_color_1, theme_color_2, ratio):
    return convert_gdk_to_theme_color(
        mix_gdk_colors(
            convert_theme_color_to_gdk(theme_color_1),
            convert_theme_color_to_gdk(theme_color_2),
            ratio=ratio
        )
    )
