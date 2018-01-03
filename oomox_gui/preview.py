import os
from gi.repository import Gtk, GLib

from .theme_model import theme_model
from .helpers import (
    convert_theme_color_to_gdk, mix_theme_colors, FALLBACK_COLOR
)
from .preview_terminal import TerminalThemePreview
from .preview_icons import IconThemePreview


WIDGET_SPACING = 10


class ThemePreview(Gtk.Grid):

    BG = 'bg'
    FG = 'fg'

    WM_BORDER_WIDTH = 2

    theme_plugin_name = None
    terminal_preview = None
    icons_preview = None

    _need_size_update = False

    css_provider = None
    css_providers_theme = None
    css_provider_caret = None
    css_provider_wm_border_color = None
    css_provider_headerbar_border = None
    css_providers_gradient = None
    css_providers_border_color = None
    css_provider_reset_external_styles = None

    def __init__(self):
        super().__init__(row_spacing=6, column_spacing=6)
        self.css_providers_theme = {}
        self.css_provider_reset_external_styles = Gtk.CssProvider()
        self.css_provider_reset_external_styles.load_from_data((
            """
            * {
                box-shadow:none;
                border: none;
            }
            """
        ).encode('ascii'))
        self.css_provider_caret = Gtk.CssProvider()
        self.css_provider_wm_border_color = Gtk.CssProvider()
        self.css_provider_headerbar_border = Gtk.CssProvider()
        self.css_provider_headerbar_border.load_from_data((
            """
            headerbar {
                border: none;
            }
            """
        ).encode('ascii'))
        self.css_providers_gradient = {}
        self.css_providers_border_color = {}
        self._init_widgets()

    def override_color(self, widget, value, color, state=Gtk.StateType.NORMAL):
        if value == self.BG:
            return widget.override_background_color(state, color)
        elif value == self.FG:
            return widget.override_color(state, color)

    def update_preview_carets(self, colorscheme):
        self.css_provider_caret.load_from_data((
            (Gtk.get_minor_version() >= 20 and """
            * {{
                caret-color: #{primary_caret_color};
                -gtk-secondary-caret-color: #{secondary_caret_color};
                -GtkWidget-cursor-aspect-ratio: {caret_aspect_ratio};
            }}
            """ or """
            * {{
                -GtkWidget-cursor-color: #{primary_caret_color};
                -GtkWidget-secondary-cursor-color: #{secondary_caret_color};
                -GtkWidget-cursor-aspect-ratio: {caret_aspect_ratio};
            }}
            """).format(
                primary_caret_color=colorscheme['CARET1_FG'],
                secondary_caret_color=colorscheme['CARET2_FG'],
                caret_aspect_ratio=colorscheme['CARET_SIZE']
            )
        ).encode('ascii'))
        Gtk.StyleContext.add_provider(
            self.entry.get_style_context(),
            self.css_provider_caret,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def update_preview_gradients(self, colorscheme):
        gradient = colorscheme['GRADIENT']
        if gradient == 0:
            return self.reset_gradients()
        for widget, color_key in zip(
            [
                self.button,
                self.headerbar_button,
                self.entry,
                self.headerbar,
            ],
            [
                "BTN_BG",
                "HDR_BTN_BG",
                "TXT_BG",
                "MENU_BG"
            ]
        ):
            color = colorscheme[color_key]
            css_provider_gradient = self.css_providers_gradient.get(color_key)
            if not css_provider_gradient:
                css_provider_gradient = \
                        self.css_providers_gradient[color_key] = \
                        Gtk.CssProvider()
            css_provider_gradient.load_from_data((
                 """
                * {{
                    background-image: linear-gradient(to bottom,
                        shade(#{color}, {amount1}),
                        shade(#{color}, {amount2})
                    );
                }}
                """.format(
                        color=color,
                        amount1=1 - gradient / 2,
                        amount2=1 + gradient * 2
                    )
            ).encode('ascii'))
            Gtk.StyleContext.add_provider(
                widget.get_style_context(),
                css_provider_gradient,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def reset_gradients(self):
        css_provider_gradient = self.css_providers_gradient.get("reset")
        if not css_provider_gradient:
            css_provider_gradient = \
                    self.css_providers_gradient["reset"] = \
                    Gtk.CssProvider()
            css_provider_gradient.load_from_data((
                 """
                * {
                    background-image: none;
                }
                """
            ).encode('ascii'))
        for widget in [
            self.button,
            self.headerbar_button,
            self.entry,
            self.headerbar,
        ]:
            Gtk.StyleContext.add_provider(
                widget.get_style_context(),
                css_provider_gradient,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def update_preview_borders(self, colorscheme):
        for widget_name, fg, bg, ratio in (
            (
                "button",
                colorscheme['BTN_FG'],
                colorscheme['BTN_BG'],
                0.22
            ), (
                "headerbar_button",
                colorscheme['HDR_BTN_FG'],
                colorscheme['HDR_BTN_BG'],
                0.22
            ), (
                "entry",
                mix_theme_colors(
                    colorscheme['TXT_FG'], colorscheme['TXT_BG'], 0.20
                ),
                colorscheme['BG'],
                0.69
            ),
        ):
            widget = getattr(self, widget_name)
            border_color = mix_theme_colors(fg, bg, ratio)
            css_provider_border_color = self.css_providers_border_color.get(widget_name)
            if not css_provider_border_color:
                css_provider_border_color = \
                    self.css_providers_border_color[widget_name] = \
                    Gtk.CssProvider()
            css_provider_border_color.load_from_data(
                """
                * {{
                    border-color: #{border_color};
                    border-radius: {roundness}px;
                }}
                """.format(
                    border_color=border_color,
                    roundness=colorscheme["ROUNDNESS"],
                ).encode('ascii')
            )
            Gtk.StyleContext.add_provider(
                widget.get_style_context(),
                css_provider_border_color,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def update_preview_colors(self, colorscheme):

        def mix(a, b, amount):
            return convert_theme_color_to_gdk(
                mix_theme_colors(colorscheme[b], colorscheme[a], amount)
            )

        converted = {
            theme_value['key']: convert_theme_color_to_gdk(
                colorscheme[theme_value['key']] or FALLBACK_COLOR
            )
            for theme_value in theme_model if (
                theme_value['type'] == 'color' and
                not theme_value['key'].startswith('TERMINAL_')
            )
        }

        self.override_color(self.bg, self.BG, converted["BG"])
        self.override_color(self.label, self.FG, converted["FG"])
        self.override_color(self.sel_label, self.FG, converted["SEL_FG"])
        self.override_color(self.sel_label, self.BG, converted["SEL_BG"])
        self.override_color(self.entry, self.FG, converted["TXT_FG"])
        self.override_color(self.entry, self.BG, converted["TXT_BG"])
        self.override_color(self.entry, self.FG, converted["SEL_FG"],
                            state=Gtk.StateFlags.SELECTED)
        self.override_color(self.entry, self.BG, converted["SEL_BG"],
                            state=Gtk.StateFlags.SELECTED)
        self.override_color(self.button, self.FG, converted["BTN_FG"])
        self.override_color(self.button, self.BG, converted["BTN_BG"])
        for item in self.menubar:
            self.override_color(item, self.FG, converted["MENU_FG"])
            self.override_color(item, self.BG, mix("MENU_BG", "MENU_FG", 0.21),
                                state=Gtk.StateFlags.PRELIGHT)
            # FIXME: :hover { color: shade("MENU_FG", 1.08); }
            for widget in self.get_menu_widgets(item.get_submenu()):
                if isinstance(widget, Gtk.MenuShell):
                    self.override_color(widget, self.BG, converted["MENU_BG"])
                    self.override_color(widget, self.FG, converted["MENU_FG"])
                else:
                    if not widget.get_sensitive():  # :disabled
                        color = mix("MENU_FG", "MENU_BG", 0.5)
                    else:
                        color = converted["MENU_FG"]
                    self.override_color(widget, self.FG, color)
                self.override_color(widget, self.BG, converted["SEL_BG"],
                                    state=Gtk.StateFlags.PRELIGHT)
                self.override_color(widget, self.FG, converted["SEL_FG"],
                                    state=Gtk.StateFlags.PRELIGHT)
        self.override_color(self.menubar, self.BG, converted["MENU_BG"])
        self.override_color(self.headerbar, self.BG, converted["MENU_BG"])
        self.override_color(self.headerbar_title, self.FG, converted["MENU_FG"])
        self.override_color(self.headerbar_button, self.FG,
                            converted["HDR_BTN_FG"])
        self.override_color(self.headerbar_button, self.BG,
                            converted["HDR_BTN_BG"])

        self.override_color(self.icons_preview, self.BG,
                            converted["TXT_BG"])

        self.css_provider_wm_border_color.load_from_data("""
            * {{
                border-color: #{border_color};
                /*border-radius: {roundness}px;*/
                border-width: {wm_border_width}px;
                border-style: solid;
            }}
        """.format(
            border_color=colorscheme['WM_BORDER_FOCUS'],
            roundness=colorscheme['ROUNDNESS'],
            wm_border_width=self.WM_BORDER_WIDTH
        ).encode('ascii'))
        Gtk.StyleContext.add_provider(
            self.bg.get_style_context(),
            self.css_provider_wm_border_color,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def update_preview(self, colorscheme, theme_plugin, icons_plugin):
        if not theme_plugin:
            return
        _colorscheme = colorscheme
        colorscheme = {}
        colorscheme.update(_colorscheme)
        theme_plugin.preview_before_load_callback(self, colorscheme)

        self.override_css_style(colorscheme, theme_plugin)
        self.update_preview_colors(colorscheme)
        self.update_preview_borders(colorscheme)
        self.update_preview_carets(colorscheme)
        self.update_preview_gradients(colorscheme)

        self.icons_preview.update_preview(colorscheme, icons_plugin)
        self.terminal_preview.update_preview(colorscheme)

    def create_menu(self, n_items, has_submenus=False):
        menu = Gtk.Menu()
        for i in range(0, n_items):
            sensitive = (i + 1) % 3 != 0
            label = _('Item {id}') if sensitive else _('Insensitive Item {id}')
            item = Gtk.MenuItem(label=label.format(id=i + 1),
                                sensitive=sensitive)
            menu.append(item)
            if has_submenus and (i + 1) % 2 == 0:
                item.set_submenu(self.create_menu(2))
        return menu

    def _init_widgets(self):
        preview_label = Gtk.Label(_("Preview:"))
        self.attach(preview_label, 1, 1, 3, 1)
        self.bg = Gtk.Grid(row_spacing=WIDGET_SPACING, column_spacing=6)
        self.attach_next_to(self.bg, preview_label,
                            Gtk.PositionType.BOTTOM, 1, 1)

        self._init_widgets_gtk()
        self.gtk_preview.set_margin_bottom(WIDGET_SPACING)
        self.bg.attach(self.gtk_preview, 1, 3, 1, 1)

        if self.icons_preview:
            self.icons_preview.destroy()
        self.icons_preview = IconThemePreview()
        self.bg.attach_next_to(
            self.icons_preview, self.gtk_preview,
            Gtk.PositionType.BOTTOM, 1, 1
        )

        if self.terminal_preview:
            self.terminal_preview.destroy()
        self.terminal_preview = TerminalThemePreview()
        self.terminal_preview.set_margin_bottom(WIDGET_SPACING)
        self.bg.attach_next_to(
            self.terminal_preview, self.icons_preview,
            Gtk.PositionType.BOTTOM, 1, 1
        )
        self.bg.set_margin_bottom(WIDGET_SPACING)

    def _init_widgets_gtk(self):
        self.gtk_preview = Gtk.Grid(row_spacing=6, column_spacing=6)

        self.headerbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(False)
        self.headerbar_title = Gtk.Label(_("Headerbar"))
        self.headerbar.props.custom_title = self.headerbar_title
        self.headerbar_button = Gtk.Button(label="   %s   " % _("Button"))
        self.headerbar.pack_end(self.headerbar_button)

        self.menubar = Gtk.MenuBar()
        self.menuitem1 = Gtk.MenuItem(label=_('File'))
        self.menuitem1.set_submenu(self.create_menu(3, True))
        self.menubar.append(self.menuitem1)
        self.menuitem2 = Gtk.MenuItem(label=_('Edit'))
        self.menuitem2.set_submenu(self.create_menu(6, True))
        self.menubar.append(self.menuitem2)

        self.headerbox.pack_start(self.headerbar, True, True, 0)
        self.headerbox.pack_start(self.menubar, True, True, 0)

        self.label = Gtk.Label(_("This is a label."))
        self.sel_label = Gtk.Label(_("Selected item."))
        self.entry = Gtk.Entry(text=_("Text entry."))

        self.button = Gtk.Button(label=_("Click-click"))
        self.button.connect("style-updated", self._queue_resize)

        self.gtk_preview.attach(self.headerbox, 1, 1, 5, 2)
        self.gtk_preview.attach(self.label, 3, 3, 1, 1)
        self.gtk_preview.attach_next_to(self.sel_label, self.label,
                                        Gtk.PositionType.BOTTOM, 1, 1)
        self.gtk_preview.attach_next_to(self.entry, self.sel_label,
                                        Gtk.PositionType.BOTTOM, 1, 1)
        self.gtk_preview.attach_next_to(self.button, self.entry,
                                        Gtk.PositionType.BOTTOM, 1, 1)

    def get_menu_widgets(self, shell):
        """ gets a menu shell (menu or menubar) and all its children """

        children = [shell]
        for child in shell:
            children.append(child)
            submenu = child.get_submenu()
            if submenu:
                children.extend(self.get_menu_widgets(submenu))
        return children

    def get_theme_css_provider(self, colorscheme, theme_plugin):
        css_name = "theme{}.css".format(
            '20' if Gtk.get_minor_version() >= 20 else ''
        )
        css_dir = theme_plugin.gtk_preview_css_dir
        css_path = os.path.join(css_dir, css_name)
        css_provider = self.css_providers_theme.get(css_path)
        if css_provider:
            return css_provider
        css_provider = Gtk.CssProvider()
        try:
            css_provider.load_from_path(css_path)
        except GLib.Error as e:
            print(e)
        self.css_providers_theme[css_path] = css_provider
        return css_provider

    def override_css_style(self, colorscheme, theme_plugin):
        new_theme_plugin_name = colorscheme["THEME_STYLE"]
        if new_theme_plugin_name == self.theme_plugin_name:
            return
        if self.theme_plugin_name:
            for child in self.get_children():
                self.remove(child)
                child.destroy()
            self._init_widgets()
        self.theme_plugin_name = new_theme_plugin_name
        base_theme_css_provider = self.get_theme_css_provider(colorscheme, theme_plugin)

        def apply_css(widget):
            widget_style_context = widget.get_style_context()
            Gtk.StyleContext.add_provider(
                widget_style_context,
                self.css_provider_reset_external_styles,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            Gtk.StyleContext.add_provider(
                widget_style_context,
                base_theme_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            if isinstance(widget, Gtk.Container):
                widget.forall(apply_css)
        apply_css(self)

        Gtk.StyleContext.add_provider(
            self.headerbar.get_style_context(),
            self.css_provider_headerbar_border,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.show_all()

    def _queue_resize(self, *args):
        # print(args)
        self.queue_resize()
