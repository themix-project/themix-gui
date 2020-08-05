import os

from gi.repository import Gtk, GLib

from .theme_model import THEME_MODEL
from .color import (
    convert_theme_color_to_gdk, mix_theme_colors, mix_gdk_colors, hex_lightness,
)
from .gtk_helpers import ScaledImage
from .preview_terminal import TerminalThemePreview
from .preview_icons import IconThemePreview
from .config import FALLBACK_COLOR
from .i18n import _


WIDGET_SPACING = 10


class CssProviders():
    theme = None
    gradient = None
    border = None
    headerbar_border = None
    wm_border = None
    caret = None
    reset_style = None

    def __init__(self):
        self.theme = {}
        self.gradient = {}
        self.border = {}
        self.headerbar_border = Gtk.CssProvider()
        self.headerbar_border.load_from_data((
            """
            headerbar {
                border: none;
                border-radius: 0;
            }
            """
        ).encode('ascii'))
        self.wm_border = Gtk.CssProvider()
        self.caret = Gtk.CssProvider()
        self.reset_style = Gtk.CssProvider()
        self.reset_style.load_from_data((
            """
            * {
                box-shadow:none;
                border: none;
            }
            """
        ).encode('ascii'))


class PreviewHeaderbar(Gtk.HeaderBar):

    title = None
    button = None

    def __init__(self):
        super().__init__()
        self.set_show_close_button(False)
        self.title = Gtk.Label(label=_("Headerbar"))
        self.props.custom_title = self.title
        self.button = Gtk.Button(label="   %s   " % _("Button"))
        self.pack_end(self.button)


class PreviewWidgets(Gtk.Box):

    # gtk preview widgets:
    headerbar = None
    menubar = None
    label = None
    sel_label = None
    entry = None
    preview_imageboxes = None
    preview_imageboxes_templates = None
    button = None

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.grid = Gtk.Grid(row_spacing=6, column_spacing=6)
        self.grid.set_margin_top(WIDGET_SPACING // 2)
        self.grid.set_halign(Gtk.Align.CENTER)

        headerbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.headerbar = PreviewHeaderbar()

        self.menubar = Gtk.MenuBar()
        menuitem1 = Gtk.MenuItem(label=_('File'))
        menuitem1.set_submenu(self.create_menu(3, True))
        self.menubar.append(menuitem1)
        menuitem2 = Gtk.MenuItem(label=_('Edit'))
        menuitem2.set_submenu(self.create_menu(6, True))
        self.menubar.append(menuitem2)

        headerbox.pack_start(self.headerbar, True, True, 0)
        headerbox.pack_start(self.menubar, True, True, 0)

        self.label = Gtk.Label(label=_("This is a label"))
        self.sel_label = Gtk.Label(label=_("Selected item"))
        self.entry = Gtk.Entry(text=_("Text entry"))
        self.button = Gtk.Button(label=_("Button"))

        self.preview_imageboxes = {}
        self.preview_imageboxes_templates = {}
        self.preview_imageboxes['CHECKBOX'] = ScaledImage(width=16)

        fake_checkbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        fake_checkbox.pack_start(self.preview_imageboxes['CHECKBOX'], False, False, 0)
        fake_checkbox.pack_start(self.label, False, False, 0)
        fake_checkbox.set_margin_left(WIDGET_SPACING // 2)

        self.grid.set_margin_left(WIDGET_SPACING)
        self.grid.set_margin_right(WIDGET_SPACING)
        self.grid.attach(fake_checkbox, 3, 3, 1, 1)
        self.grid.attach_next_to(
            self.sel_label, fake_checkbox, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(
            self.entry, self.sel_label, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.grid.attach_next_to(
            self.button, self.entry, Gtk.PositionType.BOTTOM, 1, 1
        )
        self.pack_start(headerbox, True, True, 0)
        self.pack_start(self.grid, True, True, 0)

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

    def load_imageboxes_templates(self, theme_plugin):
        for icon in theme_plugin.PreviewImageboxesNames:
            template_path = "{}.svg.template".format(icon.value)
            with open(
                    os.path.join(
                        theme_plugin.gtk_preview_dir, template_path
                    ), "rb"
            ) as file_object:
                self.preview_imageboxes_templates[icon.name] = file_object.read().decode('utf-8')

    def update_preview_imageboxes(self, colorscheme, theme_plugin):
        transform_function = theme_plugin.preview_transform_function
        self.load_imageboxes_templates(theme_plugin)
        for icon in theme_plugin.PreviewImageboxesNames:
            new_svg_image = transform_function(
                self.preview_imageboxes_templates[icon.name],
                colorscheme
            ).encode('ascii')
            self.preview_imageboxes[icon.name].set_from_bytes(
                new_svg_image, width=theme_plugin.preview_sizes[icon.name]
            )


def _get_menu_widgets(shell):
    """ gets a menu shell (menu or menubar) and all its children """
    children = [shell]
    for child in shell:
        children.append(child)
        submenu = child.get_submenu()
        if submenu:
            children.extend(_get_menu_widgets(submenu))
    return children


class ThemePreview(Gtk.Grid):

    BG = 'bg'  # pylint: disable=invalid-name
    FG = 'fg'  # pylint: disable=invalid-name

    WM_BORDER_WIDTH = 2

    theme_plugin_name = None
    css_providers = None

    # widget sections:
    background = None
    gtk_preview = None
    icons_preview = None
    terminal_preview = None

    def __init__(self):
        super().__init__(row_spacing=6, column_spacing=6)
        self.set_border_width(10)
        self.css_providers = CssProviders()
        self.init_widgets()

    def init_widgets(self):
        self.gtk_preview = PreviewWidgets()
        self.background = Gtk.Grid(row_spacing=WIDGET_SPACING, column_spacing=6)
        self.attach(self.background, 1, 1, 3, 1)

        self.gtk_preview.set_margin_bottom(WIDGET_SPACING)
        self.background.attach(self.gtk_preview, 1, 3, 1, 1)

        if self.icons_preview:
            self.icons_preview.destroy()
        self.icons_preview = IconThemePreview()
        self.background.attach_next_to(
            self.icons_preview, self.gtk_preview,
            Gtk.PositionType.BOTTOM, 1, 1
        )

        if self.terminal_preview:
            self.terminal_preview.destroy()
        self.terminal_preview = TerminalThemePreview()
        self.terminal_preview.set_margin_bottom(WIDGET_SPACING)
        self.background.attach_next_to(
            self.terminal_preview, self.icons_preview,
            Gtk.PositionType.BOTTOM, 1, 1
        )
        self.background.set_margin_bottom(WIDGET_SPACING)

        self.gtk_preview.button.connect("style-updated", self._queue_resize)

    def override_widget_color(self, widget, value, color, state=Gtk.StateType.NORMAL):
        if value == self.BG:
            return widget.override_background_color(state, color)
        if value == self.FG:
            return widget.override_color(state, color)
        raise NotImplementedError()

    def update_preview_carets(self, colorscheme):
        self.css_providers.caret.load_from_data((
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
            self.gtk_preview.entry.get_style_context(),
            self.css_providers.caret,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def update_preview_gradients(self, colorscheme):
        gradient = colorscheme['GRADIENT']
        if gradient == 0:
            self.reset_gradients()
            return
        for widget, color_key in zip(
                [
                    self.gtk_preview.button,
                    self.gtk_preview.headerbar.button,
                    self.gtk_preview.entry,
                    self.gtk_preview.headerbar,
                ],
                [
                    "BTN_BG",
                    "HDR_BTN_BG",
                    "TXT_BG",
                    "HDR_BG"
                ]
        ):
            color = colorscheme[color_key]
            css_provider_gradient = self.css_providers.gradient.get(color_key)
            if not css_provider_gradient:
                css_provider_gradient = \
                        self.css_providers.gradient[color_key] = \
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
                    amount1=1 + gradient / 2,
                    amount2=1 - gradient / 2,
                )
            ).encode('ascii'))
            Gtk.StyleContext.add_provider(
                widget.get_style_context(),
                css_provider_gradient,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def reset_gradients(self):
        css_provider_gradient = self.css_providers.gradient.get("reset")
        if not css_provider_gradient:
            css_provider_gradient = \
                    self.css_providers.gradient["reset"] = \
                    Gtk.CssProvider()
            css_provider_gradient.load_from_data((
                """
                * {
                    background-image: none;
                }
                """
            ).encode('ascii'))
        for widget in [
                self.gtk_preview.button,
                self.gtk_preview.headerbar.button,
                self.gtk_preview.entry,
                self.gtk_preview.headerbar,
        ]:
            Gtk.StyleContext.add_provider(
                widget.get_style_context(),
                css_provider_gradient,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def update_preview_borders(self, colorscheme):
        for widget_name, widget, fg, bg, ratio in (  # pylint: disable=invalid-name
                (
                    'button',
                    self.gtk_preview.button,
                    colorscheme['BTN_FG'],
                    colorscheme['BTN_BG'],
                    0.22
                ), (
                    'headerbar_button',
                    self.gtk_preview.headerbar.button,
                    colorscheme['HDR_BTN_FG'],
                    colorscheme['HDR_BTN_BG'],
                    0.22
                ), (
                    'entry',
                    self.gtk_preview.entry,
                    colorscheme['TXT_BG'],
                    colorscheme['TXT_FG'],
                    0.8 * (0.7 + (
                        0 if hex_lightness(colorscheme['TXT_BG']) > 0.66 else (
                            0.1 if hex_lightness(colorscheme['TXT_BG']) > 0.33 else 0.3
                        )
                    ))
                ),
        ):
            border_color = mix_theme_colors(fg, bg, ratio)
            css_provider_border_color = self.css_providers.border.get(widget_name)
            if not css_provider_border_color:
                css_provider_border_color = \
                    self.css_providers.border[widget_name] = \
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

        converted = {
            theme_value['key']: convert_theme_color_to_gdk(
                colorscheme[theme_value['key']]
            )
            for section in THEME_MODEL.values()
            for theme_value in section if (
                theme_value['type'] == 'color' and
                not theme_value['key'].startswith('TERMINAL_')
            )
        }

        def mix(color1, color2, amount):
            return mix_gdk_colors(converted[color2], converted[color1], amount)

        self.override_widget_color(self.background, self.BG, converted["BG"])
        self.override_widget_color(self.gtk_preview.label, self.FG, converted["FG"])
        self.override_widget_color(self.gtk_preview.sel_label, self.FG, converted["SEL_FG"])
        self.override_widget_color(self.gtk_preview.sel_label, self.BG, converted["SEL_BG"])
        self.override_widget_color(self.gtk_preview.entry, self.FG, converted["TXT_FG"])
        self.override_widget_color(self.gtk_preview.entry, self.BG, converted["TXT_BG"])
        self.override_widget_color(
            self.gtk_preview.entry, self.FG, converted["SEL_FG"],
            state=Gtk.StateFlags.SELECTED
        )
        self.override_widget_color(
            self.gtk_preview.entry, self.BG, converted["SEL_BG"],
            state=Gtk.StateFlags.SELECTED
        )
        self.override_widget_color(self.gtk_preview.button, self.FG, converted["BTN_FG"])
        self.override_widget_color(self.gtk_preview.button, self.BG, converted["BTN_BG"])
        for item in self.gtk_preview.menubar.get_children():
            self.override_widget_color(item, self.FG, converted["HDR_FG"])
            self.override_widget_color(
                item, self.BG, mix("HDR_BG", "HDR_FG", 0.21),
                state=Gtk.StateFlags.PRELIGHT
            )
            for widget in _get_menu_widgets(item.get_submenu()):
                if isinstance(widget, Gtk.MenuShell):
                    self.override_widget_color(widget, self.BG, converted["HDR_BG"])
                    self.override_widget_color(widget, self.FG, converted["HDR_FG"])
                else:
                    if not widget.get_sensitive():  # :disabled
                        color = mix("HDR_FG", "HDR_BG", 0.5)
                    else:
                        color = converted["HDR_FG"]
                    self.override_widget_color(widget, self.FG, color)
                self.override_widget_color(
                    widget, self.BG, converted["SEL_BG"],
                    state=Gtk.StateFlags.PRELIGHT
                )
                self.override_widget_color(
                    widget, self.FG, converted["SEL_FG"],
                    state=Gtk.StateFlags.PRELIGHT
                )
        self.override_widget_color(self.gtk_preview.menubar, self.BG, converted["HDR_BG"])
        self.override_widget_color(self.gtk_preview.headerbar, self.BG, converted["HDR_BG"])
        self.override_widget_color(self.gtk_preview.headerbar.title, self.FG, converted["HDR_FG"])
        self.override_widget_color(
            self.gtk_preview.headerbar.button, self.FG,
            converted["HDR_BTN_FG"]
        )
        self.override_widget_color(
            self.gtk_preview.headerbar.button, self.BG,
            converted["HDR_BTN_BG"]
        )

        self.override_widget_color(
            self.icons_preview, self.BG,
            converted["TXT_BG"]
        )

        self.css_providers.wm_border.load_from_data("""
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
            self.background.get_style_context(),
            self.css_providers.wm_border,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def update_preview(self, colorscheme, theme_plugin, icons_plugin):
        colorscheme_with_fallbacks = {}
        for section in THEME_MODEL.values():
            for theme_value in section:
                if 'key' not in theme_value:
                    continue
                result = colorscheme.get(theme_value['key'])
                if not result and theme_value['type'] == 'color':
                    result = FALLBACK_COLOR
                colorscheme_with_fallbacks[theme_value['key']] = result

        if not theme_plugin:
            self.gtk_preview.hide()
        else:
            theme_plugin.preview_before_load_callback(self, colorscheme_with_fallbacks)

            self.override_css_style(colorscheme_with_fallbacks, theme_plugin)
            self.update_preview_colors(colorscheme_with_fallbacks)
            self.update_preview_borders(colorscheme_with_fallbacks)
            self.update_preview_carets(colorscheme_with_fallbacks)
            self.update_preview_gradients(colorscheme_with_fallbacks)
            self.gtk_preview.update_preview_imageboxes(colorscheme_with_fallbacks, theme_plugin)
            self.gtk_preview.show()

        if not icons_plugin:
            self.icons_preview.hide()
        else:
            self.icons_preview.update_preview(colorscheme_with_fallbacks, icons_plugin)
            self.icons_preview.show()

        self.terminal_preview.update_preview(colorscheme_with_fallbacks)

    def get_theme_css_provider(self, theme_plugin):
        css_dir = theme_plugin.gtk_preview_dir

        css_name = "theme{}.css".format(
            '20' if Gtk.get_minor_version() >= 20 else ''
        )
        css_path = os.path.join(css_dir, css_name)
        if not os.path.exists(css_path):
            css_path = os.path.join(css_dir, "theme.css")

        css_provider = self.css_providers.theme.get(css_path)
        if css_provider:
            return css_provider
        css_provider = Gtk.CssProvider()
        try:
            css_provider.load_from_path(css_path)
        except GLib.Error as exc:  # pylint: disable=catching-non-exception
            print(exc)
        self.css_providers.theme[css_path] = css_provider
        return css_provider

    def override_css_style(self, colorscheme, theme_plugin):
        new_theme_plugin_name = colorscheme["THEME_STYLE"]
        if new_theme_plugin_name == self.theme_plugin_name:
            return
        if self.theme_plugin_name:
            for child in self.get_children():
                self.remove(child)
                child.destroy()
            self.init_widgets()
        self.theme_plugin_name = new_theme_plugin_name
        base_theme_css_provider = self.get_theme_css_provider(theme_plugin)

        def apply_css(widget):
            widget_style_context = widget.get_style_context()
            Gtk.StyleContext.add_provider(
                widget_style_context,
                self.css_providers.reset_style,
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
            self.gtk_preview.headerbar.get_style_context(),
            self.css_providers.headerbar_border,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.show_all()

    def _queue_resize(self, *_args):
        # print(args)
        self.queue_resize()
