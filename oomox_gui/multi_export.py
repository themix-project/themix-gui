import os
from pathlib import Path
from typing import TYPE_CHECKING

from gi.repository import Gio, Gtk

from .config import BUILTIN_EXPORT_CONFIG_DIR, USER_EXPORT_CONFIG_DIR
from .export_common import DialogWithExportPath
from .gtk_helpers import (
    EntryDialog,
    ImageButton,
    ImageMenuButton,
    WindowWithActions,
    YesNoDialog,
    dialog_is_yes,
)
from .i18n import translate
from .plugin_api import OomoxExportPlugin, OomoxIconsPlugin, OomoxThemePlugin
from .plugin_loader import PluginLoader
from .settings import CommonOomoxConfig

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any, Final

    from .theme_file import ThemeT


BaseClass = WindowWithActions  # checkglobals-ignore


DEFAULT_PADDING: "Final[int]" = 8
CONFIG_FILE_PREFIX: "Final[str]" = "multi_export_"
LAST_PRESET: "Final[str]" = "last_preset"


class SaveAsDialog(EntryDialog):

    def __init__(
            self,
            transient_for: Gtk.Window,
            title: str | None = None,
            text: str | None = None,
            entry_text: str | None = None,
    ) -> None:
        title = title or translate("Save Export Layout")
        text = text or translate("Please input new export layout name:")
        super().__init__(
            transient_for=transient_for,
            title=title,
            text=text,
            entry_text=entry_text,
        )


class RemoveDialog(YesNoDialog):

    def __init__(self, transient_for: Gtk.Window) -> None:
        super().__init__(
            transient_for=transient_for,
            title=translate("Remove Export Layout"),
            text=translate(
                "Are you sure you want to delete this export layout?\n"
                "This can not be undone.",
            ),
        )


class ExportWrapper(Gtk.Box):

    def __init__(
            self,
            name: str,
            plugin: OomoxExportPlugin | OomoxThemePlugin | OomoxIconsPlugin,
            export_dialog: DialogWithExportPath,
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
            "edit-delete-symbolic", translate("Remove export target…"),
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


class MultiExportDialog(BaseClass):  # pylint: disable=too-many-instance-attributes

    added_plugins: list[ExportWrapper]
    current_preset: str
    config: CommonOomoxConfig

    def __init__(  # pylint: disable=too-many-locals,too-many-statements,too-many-arguments
            self,
            transient_for: Gtk.Window,
            colorscheme: "ThemeT",
            theme_name: str,
            *,
            width: int = 600,
            height: int = 600,
            export_layout: str | None = None,
            export_layout_path: str | None = None,
            export_callback: "Callable[[MultiExportDialog], None] | None" = None,
            readonly: bool = False,
    ) -> None:
        BaseClass.__init__(self, Gtk.WindowType.TOPLEVEL)  # type: ignore[arg-type]
        self.transient_for = transient_for
        self.readonly = readonly
        self.added_plugins = []
        self.colorscheme = colorscheme
        self.colorscheme_name = theme_name
        self.export_callback = export_callback
        self.set_default_size(width, height)

        self.meta_config = CommonOomoxConfig(
            config_dir=USER_EXPORT_CONFIG_DIR,
            config_name=f"{CONFIG_FILE_PREFIX}",
            force_reload=True,
        )

        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=DEFAULT_PADDING,
        )
        self.background = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5,
        )
        self.background.set_margin_top(DEFAULT_PADDING)
        self.background.set_margin_bottom(DEFAULT_PADDING)
        self.background.set_margin_left(DEFAULT_PADDING)
        self.background.set_margin_right(DEFAULT_PADDING)
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
            label=translate("Add export target…"),
            icon_name="pan-down-symbolic",
            tooltip_text=translate("Add targets for Multi-Export"),
        )
        add_export_target_button.set_use_popover(True)
        add_export_target_button.set_menu_model(export_menu)
        self.add_action(Gio.PropertyAction(  # type: ignore[call-arg,arg-type]
            name="win.add",
            object=add_export_target_button,
            property_name="active",
        ))

        self.options_store = Gtk.ListStore(str)
        self.load_presets()
        self.presets_dropdown = Gtk.ComboBox.new_with_model(self.options_store)
        renderer_text = Gtk.CellRendererText()
        self.presets_dropdown.pack_start(renderer_text, True)
        self.presets_dropdown.add_attribute(renderer_text, "text", 0)
        self.presets_dropdown.connect(
            "changed",
            self.on_preset_changed,
        )

        save_button = ImageButton(
            "document-save-symbolic", translate("Save current export layout"),
        )
        save_button.connect("clicked", self._on_save_all)
        save_as_button = ImageButton(
            "document-save-as-symbolic", translate("Save export layout as…"),
        )
        save_as_button.connect("clicked", self._on_save_as_preset)
        self.remove_button = ImageButton(
            "edit-delete-symbolic", translate("Remove export layout…"),
        )
        self.remove_button.connect("clicked", self._on_remove_preset)

        export_all_button = Gtk.Button(translate("Export All"))
        export_all_button.connect("clicked", self._on_export_all)

        self.box.pack_start(self.scroll, True, True, 0)
        self.box.pack_end(export_all_button, False, False, 0)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)  # type: ignore[arg-type]
        self.headerbar.props.title = translate("Multi-Export")  # type: ignore[attr-defined]
        self.headerbar.pack_start(add_export_target_button)  # type: ignore[arg-type]
        self.headerbar.pack_end(self.remove_button)  # type: ignore[arg-type]
        self.headerbar.pack_end(save_as_button)  # type: ignore[arg-type]
        self.headerbar.pack_end(save_button)  # type: ignore[arg-type]
        self.headerbar.pack_end(self.presets_dropdown)  # type: ignore[arg-type]
        self.set_titlebar(self.headerbar)

        if export_layout_path:
            self.load_preset_from_path(
                config_dir=os.path.dirname(export_layout_path),
                config_name=Path(export_layout_path).stem,
            )
        else:
            last_preset_idx = 0
            last_preset = export_layout or self.meta_config.config.get(LAST_PRESET)
            if last_preset and last_preset in self.presets:
                last_preset_idx = self.presets.index(last_preset)
            self.set_preset(last_preset_idx)

        self.show_all()

    def load_presets(self) -> None:
        self.presets = [
            "default",
        ]
        for filename in sorted(os.listdir(USER_EXPORT_CONFIG_DIR) + os.listdir(BUILTIN_EXPORT_CONFIG_DIR)):
            if filename.startswith(CONFIG_FILE_PREFIX):
                preset_name = filename.rsplit(
                    ".json", maxsplit=1,
                )[0].split(
                    CONFIG_FILE_PREFIX, maxsplit=1,
                )[1]
                if preset_name and (preset_name not in self.presets):
                    self.presets.append(preset_name)
        self.options_store.clear()
        for preset in self.presets:
            self.options_store.append([preset])

    def set_preset(self, preset_idx: int = 0) -> None:
        self.current_preset = self.presets[preset_idx]
        self.presets_dropdown.set_active(preset_idx)

    def _on_save_as_preset(self, _button: Gtk.Button) -> None:
        dialog = SaveAsDialog(transient_for=self, entry_text="")
        if not dialog_is_yes(dialog):
            return
        new_preset_name = dialog.entry_text
        self.config = CommonOomoxConfig(
            config_dir=USER_EXPORT_CONFIG_DIR,
            config_name=f"{CONFIG_FILE_PREFIX}{new_preset_name}",
            force_reload=True,
        )
        self.save_preset_layout_to_config()
        self.load_presets()
        self.set_preset(self.presets.index(new_preset_name))

    def _on_remove_preset(self, _button: Gtk.Button) -> None:
        if self.current_preset == "default":
            return
        if not dialog_is_yes(RemoveDialog(transient_for=self)):
            return
        os.unlink(
            os.path.join(
                USER_EXPORT_CONFIG_DIR,
                f"{CONFIG_FILE_PREFIX}{self.current_preset}.json",
            ),
        )
        self.load_presets()
        self.set_preset(0)

    def load_preset_from_path(self, config_dir: str, config_name: str) -> None:
        print(f":: Loading export layout {config_name}.json from {config_dir}/ ...")
        self.config = CommonOomoxConfig(
            config_dir=config_dir,
            config_name=config_name,
            force_reload=True,
        )
        if not self.config.config:
            self.config = CommonOomoxConfig(
                config_dir=config_dir,
                config_name=config_name,
                force_reload=True,
            )
        for data in self.config.config.values():
            plugin_name = data.get("name")
            plugin_config = data.get("config")
            if plugin_name and plugin_config:
                self.add_export_target(plugin_name, plugin_config)

    def on_preset_changed(self, widget: Gtk.ComboBox) -> None:
        self.remove_all_export_targets()
        preset_idx = widget.get_active()
        self.current_preset = self.presets[preset_idx]
        self.remove_button.set_sensitive(self.current_preset != "default")
        config_name = f"{CONFIG_FILE_PREFIX}{self.current_preset}"
        if os.path.exists(
            os.path.join(
                USER_EXPORT_CONFIG_DIR,
                f"{config_name}.json",
            ),
        ):
            config_dir = USER_EXPORT_CONFIG_DIR
        else:
            config_dir = BUILTIN_EXPORT_CONFIG_DIR
        self.load_preset_from_path(
            config_dir=config_dir,
            config_name=config_name,
        )

    def remove_all_export_targets(self) -> None:
        for export in self.added_plugins[:]:
            self.remove_export_target(export)

    def remove_export_target(self, export: ExportWrapper) -> None:
        self.added_plugins.remove(export)
        self.background.remove(export)

    callback_counter = 0

    def _on_export_callback(self) -> None:
        if not self.export_callback:
            return
        self.callback_counter += 1
        if self.callback_counter == len(self.added_plugins):
            self.export_callback(self)

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
            plugin=plugin.__class__(),
            export_dialog=plugin.export_dialog(
                transient_for=self,
                theme_name=self.colorscheme_name,
                colorscheme=self.colorscheme,
                plugin=plugin,
                base_class=Gtk.Box,  # type: ignore[arg-type]
                override_config=default_config,
                preview_theme=False,
                callback=self._on_export_callback,
            ),
            remove_callback=lambda _x: self.remove_export_target(export),
        )
        export.export_dialog.box.remove(export.export_dialog.apply_button)
        self.added_plugins.append(export)
        self.background.add(export)
        self.background.show_all()

    def _on_add_export_target(self, action: Gio.SimpleAction, _param: "Any" = None) -> None:
        export_plugin_name = action.props.name.replace("export_plugin_", "")  # type: ignore[attr-defined]
        self.add_export_target(export_plugin_name)

    def save_preset_layout_to_config(self) -> None:
        if self.readonly:
            return
        self.config = CommonOomoxConfig(
            config_dir=USER_EXPORT_CONFIG_DIR,
            config_name=self.config.name,
            force_reload=False,
            default_config={},
        )
        self.config.config = {}
        for idx, export in enumerate(self.added_plugins):
            export.export_dialog.remove_preset_name_from_path_config()
            self.config.config[str(idx)] = {
                "name": export.name,
                "config": export.export_dialog.export_config.config,
            }
        self.config.save()
        self.meta_config.config[LAST_PRESET] = self.current_preset
        self.meta_config.save()

    def export_all(self) -> None:
        for _idx, export in enumerate(self.added_plugins):
            print(f"  :: {export.name}...")
            export.export_dialog.do_export()

    def _on_save_all(self, _button: Gtk.Button) -> None:
        for _idx, export in enumerate(self.added_plugins):
            export.export_dialog.remove_preset_name_from_path_config()
        self.save_preset_layout_to_config()

    def _on_export_all(self, _button: Gtk.Button) -> None:
        self.export_all()
        self.save_preset_layout_to_config()
