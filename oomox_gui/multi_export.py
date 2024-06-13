from typing import TYPE_CHECKING

from gi.repository import Gio, Gtk

from .config import USER_EXPORT_CONFIG_DIR
from .export_common import ExportDialogWithOptions
from .gtk_helpers import (
    ImageButton,
    ImageMenuButton,
    WindowWithActions,
)
from .i18n import translate
from .plugin_api import OomoxExportPlugin, OomoxIconsPlugin, OomoxThemePlugin
from .plugin_loader import PluginLoader
from .settings import CommonOomoxConfig

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, Final

    from .theme_file import ThemeT


BaseClass = WindowWithActions


DEFAULT_PADDING: "Final[int]" = 8


class ExportWrapper(Gtk.Box):

    def __init__(
            self,
            name: str,
            plugin: OomoxExportPlugin | OomoxThemePlugin | OomoxIconsPlugin,
            export_dialog: ExportDialogWithOptions,
            remove_callback: "Callable[[Any], None]",
    ) -> None:
        super().__init__(  # type: ignore[misc]
            self,  # type: ignore[arg-type]
            orientation=Gtk.Orientation.VERTICAL,
            spacing=5,
        )
        self.name = name
        self.header = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=5,
        )
        self.header.set_homogeneous(False)
        self.plugin = plugin
        self.export_dialog = export_dialog
        self.set_homogeneous(False)
        self.show_all()
        self.export_dialog = export_dialog
        header_label = Gtk.Label(plugin.display_name)
        self.remove_button = ImageButton(
            "edit-delete-symbolic", translate("Remove Theme…"),
        )
        self.remove_button.connect("clicked", remove_callback)
        separator = Gtk.Separator(
            orientation=Gtk.Orientation.HORIZONTAL,  # type: ignore[call-arg]
        )
        separator.set_margin_top(4)
        separator.set_margin_bottom(DEFAULT_PADDING)
        self.header.pack_start(header_label, True, True, 0)
        self.header.pack_end(self.remove_button, False, False, DEFAULT_PADDING)
        self.add(self.header)
        header_label.show()
        self.add(self.export_dialog)  # type: ignore[arg-type]
        self.add(separator)
        separator.show()
        # self.show()


class MultiExportDialog(BaseClass):

    added_plugins: list[ExportWrapper]

    def __init__(  # pylint: disable=too-many-locals
            self,
            transient_for: Gtk.Window,
            colorscheme: "ThemeT",
            theme_name: str,
            width: int = 600,
            height: int = 600,
    ) -> None:
        BaseClass.__init__(self, Gtk.WindowType.TOPLEVEL)  # type: ignore[arg-type]
        self.transient_for = transient_for
        self.set_title(translate("Multi-Export"))
        self.added_plugins = []
        self.colorscheme = colorscheme
        self.colorscheme_name = theme_name
        self.set_default_size(width, height)

        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=DEFAULT_PADDING,
        )
        self.background = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5,
        )
        self.background.set_homogeneous(False)
        self.scroll = Gtk.ScrolledWindow(
            # expand=True,
        )
        self.scroll.add(self.background)
        # adj = self.background.get_vadjustment()
        # adj.connect(
        #     "changed",
        #     lambda adj: adj.set_value(adj.get_upper() - adj.get_page_size()),
        # )
        self.add(self.box)

        theme_plugin_name = self.colorscheme["THEME_STYLE"]
        self.plugin_theme = None
        for theme_plugin in PluginLoader.get_theme_plugins().values():
            if theme_plugin.name == theme_plugin_name:
                self.plugin_theme = theme_plugin
        icons_plugin_name = self.colorscheme["ICONS_STYLE"]
        self.plugin_icons = None
        for icons_plugin in PluginLoader.get_icons_plugins().values():
            if icons_plugin.name == icons_plugin_name:
                self.plugin_icons = icons_plugin

        self.plugins = {
            "theme": self.plugin_theme,
            "icons": self.plugin_icons,
            **{
                plugin_name: plugin
                for plugin_name, plugin
                in PluginLoader.get_export_plugins().items()
                if plugin.multi_export_supported
            },
        }

        export_menu = Gio.Menu()
        for plugin_name, export_plugin in self.plugins.items():
            if not export_plugin:
                continue
            export_menu.append_item(Gio.MenuItem.new(
                export_plugin.export_text or export_plugin.display_name,
                f"win.export_plugin_{plugin_name}",
            ))
            self.add_simple_action(
                f"export_plugin_{plugin_name}", self._on_add_export_target,
            )
        add_export_target_button = ImageMenuButton(
            label=translate("Add export target…"), icon_name="pan-down-symbolic",
            tooltip_text=translate("Add targets for Multi-Export"),
        )
        add_export_target_button.set_margin_top(DEFAULT_PADDING)
        add_export_target_button.set_margin_left(DEFAULT_PADDING)
        add_export_target_button.set_margin_right(DEFAULT_PADDING)
        add_export_target_button.set_use_popover(True)
        add_export_target_button.set_menu_model(export_menu)
        export_all_button = Gtk.Button(translate("Export All"))
        export_all_button.connect("clicked", self._on_export_all)
        export_all_button.set_margin_bottom(DEFAULT_PADDING)
        export_all_button.set_margin_left(DEFAULT_PADDING)
        export_all_button.set_margin_right(DEFAULT_PADDING)
        self.add_action(Gio.PropertyAction(  # type: ignore[call-arg,arg-type]
            name="win.add",
            object=add_export_target_button,
            property_name="active",
        ))

        self.box.pack_start(add_export_target_button, False, False, 0)
        self.box.pack_start(self.scroll, True, True, 0)
        self.box.pack_end(export_all_button, False, False, 0)

        self.show_all()

        self.config = CommonOomoxConfig(
            config_dir=USER_EXPORT_CONFIG_DIR,
            config_name="multi_export",
            force_reload=True,
        )
        for plugin_name, plugin_config in self.config.config.items():
            self.add_export_target(plugin_name, plugin_config)

    def _on_remove_export_target(self, export: ExportWrapper) -> None:
        self.added_plugins.remove(export)
        self.background.remove(export)

    def add_export_target(
            self,
            export_plugin_name: str,
            default_config: dict[str, "Any"] | None = None,
    ) -> None:
        plugin = self.plugins.get(export_plugin_name)
        if not plugin:
            return
        export = ExportWrapper(
            name=export_plugin_name,
            plugin=plugin,
            export_dialog=plugin.export_dialog(
                transient_for=self,
                theme_name=self.colorscheme_name,
                colorscheme=self.colorscheme,
                base_class=Gtk.Box,  # type: ignore[arg-type]
                override_config=default_config,
            ),
            remove_callback=lambda _x: self._on_remove_export_target(export),
        )
        export.export_dialog.box.remove(export.export_dialog.apply_button)
        self.added_plugins.append(export)
        self.background.add(export)
        self.background.show_all()

    def _on_add_export_target(self, action: Gio.SimpleAction, _param: "Any" = None) -> None:
        export_plugin_name = action.props.name.replace("export_plugin_", "")  # type: ignore[attr-defined]
        self.add_export_target(export_plugin_name)

    def _on_export_all(self, _button: Gtk.Button) -> None:
        self.config.config = {}
        for export in self.added_plugins:
            export.export_dialog.do_export()
            self.config.config[export.name] = export.export_dialog.export_config.config
        self.config.save()
