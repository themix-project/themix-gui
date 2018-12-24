from gi.repository import Gtk

from .terminal import generate_xrdb_theme_from_oomox
from .color import convert_theme_color_to_gdk
from .i18n import _


WIDGET_SPACING = 10


class TerminalThemePreview(Gtk.Box):

    LEFT_MARGIN = 18

    COLOR_ROWS = (
        (_("black"), 0, 8),
        (_("red"), 1, 9),
        (_("green"), 2, 10),
        (_("yellow"), 3, 11),
        (_("blue"), 4, 12),
        (_("purple"), 5, 13),
        (_("cyan"), 6, 14),
        (_("white"), 7, 15),
    )
    terminal_widgets = None

    def __init__(self):
        super().__init__()
        self.set_margin_right(WIDGET_SPACING)
        self.set_margin_left(WIDGET_SPACING)

        self.background = Gtk.Grid(row_spacing=6, column_spacing=6)
        self.background.set_halign(Gtk.Align.CENTER)
        self.background.set_margin_top(WIDGET_SPACING // 2)
        self.background.set_margin_bottom(WIDGET_SPACING)
        self.background.set_margin_right(WIDGET_SPACING * 2)

        self.terminal_widgets = {}
        twi = self.terminal_widgets

        twi["normal"] = Gtk.Label()
        twi["normal"].set_markup("<tt>{}</tt>".format(_("terminal colors:")))
        self.background.attach(twi["normal"], 1, 1, 2, 1)
        previous_row = twi["normal"]
        previous_row.set_margin_left(self.LEFT_MARGIN)
        for color_row in self.COLOR_ROWS:
            color_name, normal_id, highlight_id = color_row
            key1 = "color{}".format(normal_id)
            key2 = "color{}".format(highlight_id)
            twi[key1] = Gtk.Label()
            twi[key2] = Gtk.Label()
            twi[key1].set_markup("<tt>{}</tt>".format(color_name))
            twi[key2].set_markup("<tt>{}</tt>".format(color_name))
            self.background.attach_next_to(
                twi[key1], previous_row,
                Gtk.PositionType.BOTTOM, 1, 1
            )
            self.background.attach_next_to(
                twi[key2], twi[key1],
                Gtk.PositionType.RIGHT, 1, 1
            )
            previous_row = twi[key1]
            previous_row.set_margin_left(self.LEFT_MARGIN)
        self.set_center_widget(self.background)

    def update_preview(self, colorscheme):
        term_colorscheme = generate_xrdb_theme_from_oomox(colorscheme)
        converted = {
            key: convert_theme_color_to_gdk(theme_value)
            for key, theme_value in term_colorscheme.items()
        }
        term_bg = converted["background"]
        self.terminal_widgets["normal"].override_color(
            Gtk.StateType.NORMAL, converted["foreground"]
        )
        self.override_background_color(Gtk.StateType.NORMAL, term_bg)
        for color_row in self.COLOR_ROWS:
            _color_name, normal_id, highlight_id = color_row
            key1 = "color{}".format(normal_id)
            key2 = "color{}".format(highlight_id)
            self.terminal_widgets[key1].override_color(
                Gtk.StateType.NORMAL, converted[key1]
            )
            self.terminal_widgets[key2].override_color(
                Gtk.StateType.NORMAL, term_bg
            )
            self.terminal_widgets[key2].override_background_color(
                Gtk.StateType.NORMAL, converted[key2]
            )
