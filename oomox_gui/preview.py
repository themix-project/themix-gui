import os
from typing import TYPE_CHECKING

from gi.repository import GLib, Gtk

from .color import (
    MAX_LIGHTNESS,
    convert_theme_color_to_gdk,
    hex_lightness,
    mix_gdk_colors,
    mix_theme_colors,
)
from .config import DEFAULT_ENCODING, FALLBACK_COLOR
from .gtk_helpers import ScaledImage
from .i18n import translate
from .preview_icons import IconThemePreview
from .preview_terminal import TerminalThemePreview
from .theme_model import get_theme_model

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any, Final

    from gi.repository import Gdk

    from .plugin_api import OomoxIconsPlugin, OomoxThemePlugin
    from .theme_file import ThemeT


WIDGET_SPACING: "Final" = 10
GTK_320_POSTFIX = 20


class CssProviders:
    theme: dict[str, Gtk.CssProvider]
    border: dict[str, Gtk.CssProvider]
    gradient: dict[str, Gtk.CssProvider]
    headerbar_border: Gtk.CssProvider
    wm_border: Gtk.CssProvider
    caret: Gtk.CssProvider
    reset_style: Gtk.CssProvider

    def __init__(self) -> None:
        self.theme = {}
        self.border = {}
        self.gradient = {}
        self.headerbar_border = Gtk.CssProvider()
        self.headerbar_border.load_from_data((
            """
            headerbar {
                border: none;
                border-radius: 0;
            }
            """
        ).encode("ascii"))
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
        ).encode("ascii"))


class PreviewHeaderbar(Gtk.HeaderBar):

    title: Gtk.Label
    button: Gtk.Button

    def __init__(self) -> None:
        super().__init__()
        self.set_show_close_button(False)  # type: ignore[arg-type]
        self.title = Gtk.Label(label=translate("Headerbar"))
        self.props.custom_title = self.title  # type: ignore[attr-defined]
        self.button = Gtk.Button(label=f'   {translate("Button")}   ')
        self.pack_end(self.button)  # type: ignore[arg-type]


class PreviewWidgets(Gtk.Box):

    # gtk preview widgets:
    headerbar: PreviewHeaderbar
    menubar: Gtk.MenuBar
    label: Gtk.Label
    sel_label: Gtk.Label
    entry: Gtk.Entry
    preview_imageboxes: dict[str, ScaledImage]
    preview_imageboxes_templates: dict[str, str]
    button: Gtk.Button

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.grid = Gtk.Grid(row_spacing=6, column_spacing=6)
        self.grid.set_margin_top(WIDGET_SPACING // 2)
        self.grid.set_halign(Gtk.Align.CENTER)

        headerbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.headerbar = PreviewHeaderbar()

        self.menubar = Gtk.MenuBar()
        menuitem1 = Gtk.MenuItem(label=translate("File"))
        menuitem1.set_submenu(self.create_menu(3, True))
        self.menubar.append(menuitem1)  # type: ignore[attr-defined]
        menuitem2 = Gtk.MenuItem(label=translate("Edit"))
        menuitem2.set_submenu(self.create_menu(6, True))
        self.menubar.append(menuitem2)  # type: ignore[attr-defined]

        headerbox.pack_start(self.headerbar, True, True, 0)
        headerbox.pack_start(self.menubar, True, True, 0)  # type: ignore[arg-type]

        self.label = Gtk.Label(label=translate("This is a label"))
        self.sel_label = Gtk.Label(label=translate("Selected item"))
        self.entry = Gtk.Entry(text=translate("Text entry"))  # type: ignore[call-arg]
        self.button = Gtk.Button(label=translate("Button"))

        self.preview_imageboxes = {}
        self.preview_imageboxes_templates = {}
        self.preview_imageboxes["CHECKBOX"] = ScaledImage(width=16)

        fake_checkbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        fake_checkbox.pack_start(self.preview_imageboxes["CHECKBOX"], False, False, 0)
        fake_checkbox.pack_start(self.label, False, False, 0)
        fake_checkbox.set_margin_left(WIDGET_SPACING // 2)

        self.grid.set_margin_left(WIDGET_SPACING)
        self.grid.set_margin_right(WIDGET_SPACING)
        self.grid.attach(fake_checkbox, 3, 3, 1, 1)
        self.grid.attach_next_to(
            self.sel_label, fake_checkbox, Gtk.PositionType.BOTTOM, 1, 1,
        )
        self.grid.attach_next_to(
            self.entry, self.sel_label, Gtk.PositionType.BOTTOM, 1, 1,
        )
        self.grid.attach_next_to(
            self.button, self.entry, Gtk.PositionType.BOTTOM, 1, 1,
        )
        self.pack_start(headerbox, True, True, 0)
        self.pack_start(self.grid, True, True, 0)

    def create_menu(self, n_items: int, has_submenus: bool = False) -> Gtk.Menu:
        menu = Gtk.Menu()
        for i in range(n_items):
            sensitive = (i + 1) % 3 != 0
            label = translate("Item {id}") if sensitive else translate("Insensitive Item {id}")
            item = Gtk.MenuItem(  # type: ignore[call-arg]
                label=label.format(id=i + 1),
                sensitive=sensitive,
            )
            menu.append(item)
            if has_submenus and (i + 1) % 2 == 0:
                item.set_submenu(self.create_menu(2))
        return menu

    def load_imageboxes_templates(self, theme_plugin: "OomoxThemePlugin") -> None:
        for icon in theme_plugin.PreviewImageboxesNames:
            template_path = f"{icon.value}.svg.template"
            with open(
                    os.path.join(
                        theme_plugin.gtk_preview_dir, template_path,
                    ), "rb",
            ) as file_object:
                self.preview_imageboxes_templates[icon.name] = \
                    file_object.read().decode(DEFAULT_ENCODING)

    def update_preview_imageboxes(
            self, colorscheme: "ThemeT", theme_plugin: "OomoxThemePlugin",
    ) -> None:
        transform_function = theme_plugin.preview_transform_function
        self.load_imageboxes_templates(theme_plugin)
        for icon in theme_plugin.PreviewImageboxesNames:
            new_svg_image = transform_function(
                self.preview_imageboxes_templates[icon.name],
                colorscheme,
            ).encode("ascii")
            self.preview_imageboxes[icon.name].set_from_bytes(
                new_svg_image, width=theme_plugin.preview_sizes[icon.name],
            )


def _get_menu_widgets(shell: Gtk.MenuShell) -> "Sequence[Gtk.Menu | Gtk.MenuShell]":
    """Gets a menu shell (menu or menubar) and all its children."""
    children = [shell]
    for child in shell:  # type: ignore[attr-defined]
        children.append(child)
        submenu = child.get_submenu()
        if submenu:
            children.extend(_get_menu_widgets(submenu))
    return children


class ThemePreview(Gtk.Grid):

    BG = "bg"  # pylint: disable=invalid-name
    FG = "fg"  # pylint: disable=invalid-name

    WM_BORDER_WIDTH: int = 2

    theme_plugin_name: str | None = None
    css_providers: CssProviders

    # widget sections:
    background: Gtk.Grid
    gtk_preview: PreviewWidgets
    icons_preview: IconThemePreview | None = None
    terminal_preview: TerminalThemePreview | None = None

    def __init__(self) -> None:
        super().__init__(row_spacing=6, column_spacing=6)
        self.set_border_width(10)
        self.css_providers = CssProviders()
        self.init_widgets()

    def init_widgets(self) -> None:
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
            Gtk.PositionType.BOTTOM, 1, 1,
        )

        if self.terminal_preview:
            self.terminal_preview.destroy()
        self.terminal_preview = TerminalThemePreview()
        self.terminal_preview.set_margin_bottom(WIDGET_SPACING)
        self.background.attach_next_to(
            self.terminal_preview, self.icons_preview,
            Gtk.PositionType.BOTTOM, 1, 1,
        )
        self.background.set_margin_bottom(WIDGET_SPACING)

        self.gtk_preview.button.connect("style-updated", self._queue_resize)

    def override_widget_color(
            self,
            widget: Gtk.Widget,
            value: str,
            color: "Gdk.RGBA",
            state: Gtk.StateFlags = Gtk.StateFlags.NORMAL,
    ) -> None:
        if value == self.BG:
            widget.override_background_color(state, color)  # type: ignore[arg-type]
            return
        if value == self.FG:
            widget.override_color(state, color)  # type: ignore[arg-type]
            return
        raise NotImplementedError

    def update_preview_carets(self, colorscheme: "ThemeT") -> None:
        self.css_providers.caret.load_from_data((
            (Gtk.get_minor_version() >= GTK_320_POSTFIX and """
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
                primary_caret_color=colorscheme["CARET1_FG"],
                secondary_caret_color=colorscheme["CARET2_FG"],
                caret_aspect_ratio=colorscheme["CARET_SIZE"],
            )
        ).encode("ascii"))
        Gtk.StyleContext.add_provider(
            self.gtk_preview.entry.get_style_context(),
            self.css_providers.caret,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def update_preview_gradients(self, colorscheme: "ThemeT") -> None:
        gradient: float = colorscheme["GRADIENT"]  # type: ignore[assignment]
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
                    "HDR_BG",
                ],
                strict=True,
        ):
            color = colorscheme[color_key]
            css_provider_gradient = self.css_providers.gradient.get(color_key)
            if not css_provider_gradient:
                css_provider_gradient = \
                    self.css_providers.gradient[color_key] = \
                    Gtk.CssProvider()
            css_provider_gradient.load_from_data((
                f"""
                * {{
                    background-image: linear-gradient(to bottom,
                        shade(#{color}, {1 + gradient / 2}),
                        shade(#{color}, {1 - gradient / 2})
                    );
                }}
                """
            ).encode("ascii"))
            Gtk.StyleContext.add_provider(
                widget.get_style_context(),
                css_provider_gradient,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def reset_gradients(self) -> None:
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
            ).encode("ascii"))
        for widget in [
                self.gtk_preview.button,
                self.gtk_preview.headerbar.button,
                self.gtk_preview.entry,
                self.gtk_preview.headerbar,
        ]:
            Gtk.StyleContext.add_provider(
                widget.get_style_context(),
                css_provider_gradient,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def update_preview_borders(self, colorscheme: "ThemeT") -> None:
        for widget_name, widget, fg, bg, ratio in (  # pylint: disable=invalid-name
                (
                    "button",
                    self.gtk_preview.button,
                    colorscheme["BTN_FG"],
                    colorscheme["BTN_BG"],
                    0.22,
                ), (
                    "headerbar_button",
                    self.gtk_preview.headerbar.button,
                    colorscheme["HDR_BTN_FG"],
                    colorscheme["HDR_BTN_BG"],
                    0.22,
                ), (
                    "entry",
                    self.gtk_preview.entry,
                    colorscheme["TXT_BG"],
                    colorscheme["TXT_FG"],
                    0.8 * (0.7 + (
                        0
                        if hex_lightness(
                            colorscheme["TXT_BG"],  # type: ignore[arg-type]
                        ) > (MAX_LIGHTNESS * 2 / 3) else (
                            0.1
                            if hex_lightness(
                                colorscheme["TXT_BG"],  # type: ignore[arg-type]
                            ) > (MAX_LIGHTNESS / 3) else
                            0.3
                        )
                    )),
                ),
        ):
            border_color = mix_theme_colors(fg, bg, ratio)  # type: ignore[arg-type]
            css_provider_border_color = self.css_providers.border.get(widget_name)
            if not css_provider_border_color:
                css_provider_border_color = \
                    self.css_providers.border[widget_name] = \
                    Gtk.CssProvider()
            css_provider_border_color.load_from_data(
                f"""
                * {{
                    border-color: #{border_color};
                    border-radius: {colorscheme["ROUNDNESS"]}px;
                }}
                """.encode("ascii"),
            )
            Gtk.StyleContext.add_provider(
                widget.get_style_context(),
                css_provider_border_color,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def update_preview_colors(self, colorscheme: "ThemeT") -> None:

        converted = {
            theme_value["key"]: convert_theme_color_to_gdk(
                colorscheme[theme_value["key"]],  # type: ignore[arg-type]
            )
            for section in get_theme_model().values()
            for theme_value in section if (
                theme_value["type"] == "color" and
                not theme_value["key"].startswith("TERMINAL_")
            )
        }

        def mix(color_id1: str, color_id2: str, amount: float) -> "Gdk.RGBA":
            return mix_gdk_colors(converted[color_id2], converted[color_id1], amount)

        self.override_widget_color(self.background, self.BG, converted["BG"])
        self.override_widget_color(self.gtk_preview.label, self.FG, converted["FG"])
        self.override_widget_color(self.gtk_preview.sel_label, self.FG, converted["SEL_FG"])
        self.override_widget_color(self.gtk_preview.sel_label, self.BG, converted["SEL_BG"])
        self.override_widget_color(self.gtk_preview.entry, self.FG, converted["TXT_FG"])
        self.override_widget_color(self.gtk_preview.entry, self.BG, converted["TXT_BG"])
        self.override_widget_color(
            self.gtk_preview.entry, self.FG, converted["SEL_FG"],
            state=Gtk.StateFlags.SELECTED,
        )
        self.override_widget_color(
            self.gtk_preview.entry, self.BG, converted["SEL_BG"],
            state=Gtk.StateFlags.SELECTED,
        )
        self.override_widget_color(self.gtk_preview.button, self.FG, converted["BTN_FG"])
        self.override_widget_color(self.gtk_preview.button, self.BG, converted["BTN_BG"])
        for item in self.gtk_preview.menubar.get_children():  # type: ignore[attr-defined]
            self.override_widget_color(item, self.FG, converted["HDR_FG"])
            self.override_widget_color(
                item, self.BG, mix("HDR_BG", "HDR_FG", 0.21),
                state=Gtk.StateFlags.PRELIGHT,
            )
            for widget in _get_menu_widgets(item.get_submenu()):
                if isinstance(widget, Gtk.MenuShell):
                    self.override_widget_color(widget, self.BG, converted["HDR_BG"])
                    self.override_widget_color(widget, self.FG, converted["HDR_FG"])
                else:
                    color = mix("HDR_FG", "HDR_BG", 0.5) if not widget.get_sensitive() else converted["HDR_FG"]
                    self.override_widget_color(widget, self.FG, color)
                self.override_widget_color(
                    widget, self.BG, converted["SEL_BG"],
                    state=Gtk.StateFlags.PRELIGHT,
                )
                self.override_widget_color(
                    widget, self.FG, converted["SEL_FG"],
                    state=Gtk.StateFlags.PRELIGHT,
                )
        self.override_widget_color(
            self.gtk_preview.menubar, self.BG, converted["HDR_BG"],  # type: ignore[arg-type]
        )
        self.override_widget_color(self.gtk_preview.headerbar, self.BG, converted["HDR_BG"])
        self.override_widget_color(self.gtk_preview.headerbar.title, self.FG, converted["HDR_FG"])
        self.override_widget_color(
            self.gtk_preview.headerbar.button, self.FG,
            converted["HDR_BTN_FG"],
        )
        self.override_widget_color(
            self.gtk_preview.headerbar.button, self.BG,
            converted["HDR_BTN_BG"],
        )

        if self.icons_preview:
            self.override_widget_color(
                self.icons_preview, self.BG,
                converted["TXT_BG"],
            )

        self.css_providers.wm_border.load_from_data(
            f"""
                * {{
                    border-color: #{colorscheme['WM_BORDER_FOCUS']};
                    /*border-radius: {colorscheme['ROUNDNESS']}px;*/
                    border-width: {self.WM_BORDER_WIDTH}px;
                    border-style: solid;
                }}
            """.encode("ascii"),
        )
        Gtk.StyleContext.add_provider(
            self.background.get_style_context(),
            self.css_providers.wm_border,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def update_preview(
            self,
            colorscheme: "ThemeT",
            theme_plugin: "OomoxThemePlugin | None",
            icons_plugin: "OomoxIconsPlugin | None",
    ) -> None:
        colorscheme_with_fallbacks: "ThemeT" = {}
        for section in get_theme_model().values():
            for theme_value in section:
                if "key" not in theme_value:
                    continue
                result = colorscheme.get(theme_value["key"])
                if not result and theme_value["type"] == "color":
                    result = FALLBACK_COLOR
                colorscheme_with_fallbacks[theme_value["key"]] = result  # type: ignore[assignment]

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

        if not self.icons_preview:
            no_icon_preview = "Icon preview widget failed to load"
            raise RuntimeError(no_icon_preview)
        if not icons_plugin:
            self.icons_preview.hide()
        else:
            self.icons_preview.update_preview(colorscheme_with_fallbacks, icons_plugin)
            self.icons_preview.show()

        if not self.terminal_preview:
            no_terminal_preview = "Terminal preview widget failed to load"
            raise RuntimeError(no_terminal_preview)
        self.terminal_preview.update_preview(colorscheme_with_fallbacks)

    def get_theme_css_provider(self, theme_plugin: "OomoxThemePlugin") -> Gtk.CssProvider:
        css_dir = theme_plugin.gtk_preview_dir

        _css_postfix = f"{GTK_320_POSTFIX}" if Gtk.get_minor_version() >= GTK_320_POSTFIX else ""
        css_name = f"theme{_css_postfix}.css"
        css_path = os.path.join(css_dir, css_name)
        if not os.path.exists(css_path):
            css_path = os.path.join(css_dir, "theme.css")

        css_provider = self.css_providers.theme.get(css_path)
        if css_provider:
            return css_provider
        css_provider = Gtk.CssProvider()
        try:
            css_provider.load_from_path(css_path)  # type: ignore[arg-type]
        except GLib.Error as exc:
            print(exc)
        self.css_providers.theme[css_path] = css_provider
        return css_provider

    def override_css_style(self, colorscheme: "ThemeT", theme_plugin: "OomoxThemePlugin") -> None:
        new_theme_plugin_name: str = colorscheme["THEME_STYLE"]  # type: ignore[assignment]
        if new_theme_plugin_name == self.theme_plugin_name:
            return
        if self.theme_plugin_name:
            for child in self.get_children():
                self.remove(child)
                child.destroy()
            self.init_widgets()
        self.theme_plugin_name = new_theme_plugin_name
        base_theme_css_provider = self.get_theme_css_provider(theme_plugin)

        def apply_css(widget: Gtk.Widget) -> None:
            widget_style_context = widget.get_style_context()
            Gtk.StyleContext.add_provider(
                widget_style_context,
                self.css_providers.reset_style,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
            Gtk.StyleContext.add_provider(
                widget_style_context,
                base_theme_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
            if isinstance(widget, Gtk.Container):
                widget.forall(apply_css)  # type: ignore[arg-type]
        apply_css(self)

        Gtk.StyleContext.add_provider(
            self.gtk_preview.headerbar.get_style_context(),
            self.css_providers.headerbar_border,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self.show_all()

    def _queue_resize(self, *_args: "Any") -> None:
        # print(args)
        self.queue_resize()
