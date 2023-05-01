#!/bin/env python3
import contextlib
import os
import shutil
import signal
import sys
import traceback
from typing import TYPE_CHECKING

from gi.repository import Gdk, Gio, GLib, Gtk

from .about import show_about
from .colors_list import ThemeColorsList
from .config import USER_COLORS_DIR
from .gtk_helpers import (
    ActionProperty,
    ActionsEnum,
    EntryDialog,
    ImageButton,
    ImageMenuButton,
    YesNoDialog,
    warn_once,
)
from .helpers import log_error, mkdir_p
from .i18n import translate
from .plugin_api import PLUGIN_PATH_PREFIX
from .plugin_loader import PluginLoader
from .preset_list import ThemePresetList
from .preview import ThemePreview
from .settings import UISettings
from .shortcuts import show_shortcuts
from .terminal import generate_terminal_colors_for_oomox
from .theme_file import (
    get_user_theme_path,
    import_colorscheme,
    is_colorscheme_exists,
    is_user_colorscheme,
    remove_colorscheme,
    save_colorscheme,
)
from .theme_file_parser import read_colorscheme_from_path

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence
    from typing import Any

    from .plugin_api import (
        OomoxExportPlugin,
        OomoxIconsPlugin,
        OomoxImportPlugin,
        OomoxThemePlugin,
    )
    from .theme_file import ThemeT


class DoubleWindowError(RuntimeError):

    def __init__(self) -> None:
        super().__init__("App window already set")


class NoWindowError(RuntimeError):

    def __init__(self) -> None:
        super().__init__("App window not yet set")


class NewDialog(EntryDialog):

    def __init__(
            self,
            transient_for: Gtk.Window,
            title: str | None = None,
            text: str | None = None,
            entry_text: str | None = None,
    ) -> None:
        title = title or translate("New Theme")
        text = text or translate("Please input new theme name:")
        super().__init__(
            transient_for=transient_for,
            title=title,
            text=text,
            entry_text=entry_text,
        )


class RenameDialog(NewDialog):

    def __init__(self, transient_for: Gtk.Window, entry_text: str) -> None:
        super().__init__(
            transient_for=transient_for,
            title=translate("Rename Theme"),
            entry_text=entry_text,
        )


class UnsavedDialog(YesNoDialog):

    def __init__(self, transient_for: Gtk.Window) -> None:
        super().__init__(
            transient_for=transient_for,
            title=translate("Unsaved Changes"),
            text=translate("There are unsaved changes.\nSave them?"),
        )


class RemoveDialog(YesNoDialog):

    def __init__(self, transient_for: Gtk.Window) -> None:
        super().__init__(
            transient_for=transient_for,
            title=translate("Remove Theme"),
            text=translate(
                "Are you sure you want to delete the colorscheme?\n"
                "This can not be undone.",
            ),
        )


def dialog_is_yes(dialog: Gtk.Dialog) -> bool:
    return dialog.run() in (Gtk.ResponseType.YES, Gtk.ResponseType.OK)


class AppActions(ActionsEnum):
    _target = "app"
    quit_action = ActionProperty(_target, "quit")


class WindowActions(ActionsEnum):
    _target = "win"
    import_menu = ActionProperty(_target, "import_menu")
    import_themix_colors = ActionProperty(_target, "import_themix_colors")
    clone = ActionProperty(_target, "clone")
    export_icons = ActionProperty(_target, "icons")
    export_theme = ActionProperty(_target, "theme")
    export_menu = ActionProperty(_target, "export_menu")
    menu = ActionProperty(_target, "menu")
    remove = ActionProperty(_target, "remove")
    rename = ActionProperty(_target, "rename")
    save = ActionProperty(_target, "save")
    show_help = ActionProperty(_target, "show_help")
    show_about = ActionProperty(_target, "show_about")


class WindowWithActions(Gtk.ApplicationWindow):

    def _action_tooltip(self, action: ActionProperty, tooltip: str) -> str:
        action_id = action.get_id()
        app = self.get_application()
        if not app:
            no_app_error = "Application instance didn't initialized."
            raise RuntimeError(no_app_error)
        accels = app.get_accels_for_action(action_id)
        if accels:
            key, mods = Gtk.accelerator_parse(accels[0])
            tooltip += f" ({Gtk.accelerator_get_label(key, mods)})"
        return tooltip

    def attach_action(
            self, widget: Gtk.Widget, action: ActionProperty, with_tooltip: bool = True,
    ) -> None:
        action_id = action.get_id()
        widget.set_action_name(action_id)  # type: ignore[attr-defined]
        if with_tooltip:
            tooltip = self._action_tooltip(action, widget.get_tooltip_text() or "")
            widget.set_tooltip_text(tooltip)

    def add_simple_action(
            self, action_name: str, callback: "Callable[..., Any]",
    ) -> Gio.SimpleAction:
        action = Gio.SimpleAction.new(action_name, None)
        action.connect("activate", callback)
        self.add_action(action)
        return action


class OomoxApplicationWindow(WindowWithActions):  # pylint: disable=too-many-instance-attributes,too-many-public-methods  # noqa: E501

    colorscheme_name: str
    colorscheme_path: str
    colorscheme: "ThemeT"
    colorscheme_is_user: bool
    theme_edited: bool = False
    #
    plugin_theme: "OomoxThemePlugin | None" = None
    plugin_icons: "OomoxIconsPlugin | None" = None
    #
    # actions:
    action_save: Gio.SimpleAction
    action_rename: Gio.SimpleAction
    action_remove: Gio.SimpleAction
    #
    # widget sections:
    box: Gtk.Box
    headerbar: Gtk.HeaderBar
    theme_edit: ThemeColorsList
    preset_list: ThemePresetList
    preview: ThemePreview
    spinner: Gtk.Spinner
    spinner_message: Gtk.Label
    spinner_revealer: Gtk.Revealer
    paned_box: Gtk.Paned

    _currently_focused_widget = Gtk.Widget | None
    _inhibit_id: int | None = None

    def _unset_save_needed(self) -> None:
        self.headerbar.props.title = self.colorscheme_name  # type: ignore[attr-defined]
        if self._inhibit_id:
            self.application.uninhibit(self._inhibit_id)
        self.action_save.set_enabled(False)
        self.theme_edited = False

    def _set_save_needed(self) -> None:
        if not self.theme_edited:
            self.headerbar.props.title = "*" + self.colorscheme_name  # type: ignore[attr-defined]
        self._inhibit_id = self.application.inhibit(
            self,
            (
                Gtk.ApplicationInhibitFlags.LOGOUT |
                Gtk.ApplicationInhibitFlags.SUSPEND
            ),
            translate("There are unsaved changes.\nSave them?"),
        )
        self.action_save.set_enabled(True)
        self.theme_edited = True

    def save_theme(self, name: str | None = None) -> None:
        if not name:
            name = self.colorscheme_name
        if not self.preset_list.preset_is_saveable() and ((
                name.startswith(PLUGIN_PATH_PREFIX)
        ) or (
            self.ask_colorscheme_exists(name)
        )):
            self.clone_theme()
            return
        new_path = save_colorscheme(name, self.colorscheme)
        self._unset_save_needed()

        old_path = self.colorscheme_path
        self.colorscheme_name = name
        self.colorscheme_path = new_path
        if old_path != new_path:
            self.reload_presets()

    def remove_theme(self, path: str | None = None) -> None:
        if not path:
            path = self.colorscheme_path
        with contextlib.suppress(FileNotFoundError):
            remove_colorscheme(path)

    def import_theme_from_path(self, path: str, new_name: str) -> None:
        old_path = self.colorscheme_path
        new_path = import_colorscheme(new_name, path)
        self.colorscheme_name = new_name
        self.colorscheme_path = new_path
        if old_path != new_path:
            self.reload_presets()
        self.on_preset_selected(new_name, new_path)

    def import_themix_colors(self) -> None:
        self.ask_unsaved_changes()

        filechooser_dialog = Gtk.FileChooserNative.new(
            translate("Please choose a file with oomox colors"),  # type: ignore[arg-type]
            self,  # type: ignore[arg-type]
            Gtk.FileChooserAction.OPEN,  # type: ignore[arg-type]
        )
        filechooser_response = filechooser_dialog.run()
        if filechooser_response in (
                Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT,
        ):
            filechooser_dialog.destroy()
            return
        import_theme_path = filechooser_dialog.get_filename()
        filechooser_dialog.destroy()
        import_theme_name = os.path.basename(import_theme_path)

        while True:
            dialog = RenameDialog(transient_for=self, entry_text=import_theme_name)
            if not dialog_is_yes(dialog):
                return
            new_theme_name = dialog.entry_text
            if not self.ask_colorscheme_exists(new_theme_name):
                self.import_theme_from_path(
                    path=import_theme_path,
                    new_name=new_theme_name,
                )
                return

    def import_from_plugin(self, plugin: "OomoxImportPlugin") -> None:
        self.ask_unsaved_changes()
        filechooser_dialog = Gtk.FileChooserNative.new(
            translate("Please choose an image file"),  # type: ignore[arg-type]
            self,  # type: ignore[arg-type]
            Gtk.FileChooserAction.OPEN,  # type: ignore[arg-type]
        )
        filechooser_response = filechooser_dialog.run()
        if filechooser_response in (
                Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT,
        ):
            filechooser_dialog.destroy()
            return
        import_theme_path = filechooser_dialog.get_filename()
        filechooser_dialog.destroy()
        import_theme_name = os.path.basename(import_theme_path)

        new_theme_path = os.path.join(plugin.user_theme_dir, import_theme_name)
        dest_dir = os.path.dirname(new_theme_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        shutil.copy(import_theme_path, new_theme_path)
        self.colorscheme_path = new_theme_path
        self.reload_presets()

    def clone_theme(self) -> None:
        new_theme_name = self.colorscheme_name
        if is_colorscheme_exists(get_user_theme_path(new_theme_name)):
            new_theme_name += "_"
        if new_theme_name.startswith(PLUGIN_PATH_PREFIX):
            new_theme_name = "/".join(new_theme_name.split("/")[1:])
        dialog = NewDialog(transient_for=self, entry_text=new_theme_name)
        if not dialog_is_yes(dialog):
            return
        new_theme_name = dialog.entry_text
        if not self.ask_colorscheme_exists(new_theme_name):
            self.save_theme(new_theme_name)
        else:
            self.clone_theme()

    def rename_theme(self, entry_text: str | None = None) -> None:
        dialog = RenameDialog(
            transient_for=self,
            entry_text=entry_text or self.colorscheme_name,
        )
        if not dialog_is_yes(dialog):
            return
        new_theme_name = dialog.entry_text
        if not self.ask_colorscheme_exists(new_theme_name):
            old_theme_path = self.colorscheme_path
            self.save_theme(new_theme_name)
            self.remove_theme(old_theme_path)
            self.reload_presets()
        else:
            self.rename_theme(entry_text=new_theme_name)

    def ask_unsaved_changes(self) -> None:
        if self.theme_edited and dialog_is_yes(UnsavedDialog(transient_for=self)):
            self.save_theme()

    def ask_colorscheme_exists(self, colorscheme_name: str) -> bool:
        if not is_colorscheme_exists(get_user_theme_path(colorscheme_name)):
            return False
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            message_format=translate("Colorscheme with such name already exists"),
        )
        dialog.run()
        dialog.destroy()
        return True

    def _select_theme_plugin(self) -> None:
        theme_plugin_name = self.colorscheme["THEME_STYLE"]
        self.plugin_theme = None
        for theme_plugin in PluginLoader.get_theme_plugins().values():
            if theme_plugin.name == theme_plugin_name:
                self.plugin_theme = theme_plugin

    def _select_icons_plugin(self) -> None:
        icons_plugin_name = self.colorscheme["ICONS_STYLE"]
        self.plugin_icons = None
        for icons_plugin in PluginLoader.get_icons_plugins().values():
            if icons_plugin.name == icons_plugin_name:
                self.plugin_icons = icons_plugin

    def load_colorscheme(self, colorscheme: "ThemeT") -> None:
        self.colorscheme = colorscheme
        self._select_theme_plugin()
        self._select_icons_plugin()
        self.generate_terminal_colors(callback=self._load_colorscheme_callback)

    def _load_colorscheme_callback(self) -> None:
        try:
            self.preview.update_preview(
                colorscheme=self.colorscheme,
                theme_plugin=self.plugin_theme,
                icons_plugin=self.plugin_icons,
            )
        except Exception as exc:
            print()
            print("ERROR: Can't show theme preview:")
            print(exc)
            traceback.print_exc()
            print()
        else:
            self.preview.show()
        for theme_value in self.colorscheme.values():
            if not isinstance(theme_value, Exception):
                continue
            warn_once(
                text=str(theme_value),
                buttons=Gtk.ButtonsType.CLOSE,
            )

    @staticmethod
    def schedule_task(task: "Callable[..., None]", *args: "Any") -> None:
        Gdk.threads_add_idle(GLib.PRIORITY_LOW, task, *args)

    def on_preset_selected(
            self,
            selected_preset_name: str,
            selected_preset_path: str,
    ) -> None:
        self.ask_unsaved_changes()
        self.colorscheme_name = selected_preset_name
        self.colorscheme_path = selected_preset_path
        read_colorscheme_from_path(selected_preset_path, callback=self._on_preset_selected_callback)

    def _on_preset_selected_callback(self, colorscheme: "ThemeT") -> None:
        self.load_colorscheme(colorscheme)
        self.colorscheme_is_user = is_user_colorscheme(self.colorscheme_path)
        self.theme_edit.open_theme(self.colorscheme)
        self._unset_save_needed()
        self.action_rename.set_enabled(self.preset_list.preset_is_saveable())
        self.action_remove.set_enabled(self.colorscheme_is_user)

    def theme_reload(self) -> "ThemeT":
        self.on_preset_selected(
            self.colorscheme_name, self.colorscheme_path,
        )
        return self.colorscheme

    def generate_terminal_colors(self, callback: "Callable[[], None]") -> None:
        def _generate_terminal_colors(colors: "ThemeT") -> None:
            self.colorscheme.update(colors)
            callback()

        generate_terminal_colors_for_oomox(
            self.colorscheme,
            app=self,
            result_callback=_generate_terminal_colors,
        )

    def on_color_edited(self, colorscheme: "ThemeT") -> None:
        self.load_colorscheme(colorscheme)
        self._set_save_needed()

    def reload_presets(self) -> None:
        self.preset_list.reload_presets(self.colorscheme_path)

    def disable(self, message: str = "") -> None:
        def disable_ui_callback() -> None:
            self._currently_focused_widget = self.get_focus()
            self.spinner_revealer.set_reveal_child(True)
            self.preset_list.set_sensitive(False)
            self.theme_edit.set_sensitive(False)
            Gtk.main_iteration_do(False)
            self.spinner_message.set_text(message)
            self.spinner.start()

        GLib.timeout_add(
            0,
            disable_ui_callback,  # type: ignore[misc, call-arg, arg-type]
            priority=GLib.PRIORITY_HIGH,
        )

    def enable(self) -> None:
        def enable_ui_callback() -> None:
            self.spinner_revealer.set_reveal_child(False)
            self.preset_list.set_sensitive(True)
            self.theme_edit.set_sensitive(True)
            self.set_focus(self._currently_focused_widget)  # type: ignore[arg-type]
            self.spinner.stop()

        GLib.idle_add(enable_ui_callback, priority=GLib.PRIORITY_LOW)

    ###########################################################################
    # Signal handlers:
    ###########################################################################

    def _on_import_themix_colors(self, _action: Gio.SimpleAction, _param: "Any" = None) -> None:
        return self.import_themix_colors()

    def _on_import_plugin(self, action: Gio.SimpleAction, _param: "Any" = None) -> None:
        plugin = PluginLoader.get_import_plugins()[
            action.props.name.replace("import_plugin_", "")  # type: ignore[attr-defined]
        ]
        self.import_from_plugin(plugin)

    def _on_clone(self, _action: Gio.SimpleAction, _param: "Any" = None) -> None:
        self.clone_theme()

    def _on_rename(self, _action: Gio.SimpleAction, _param: "Any" = None) -> None:
        self.rename_theme()

    def _on_remove(self, _action: Gio.SimpleAction, _param: "Any" = None) -> None:
        if not dialog_is_yes(RemoveDialog(transient_for=self)):
            return
        self.remove_theme()
        self.action_rename.set_enabled(False)
        self.action_remove.set_enabled(False)
        self.reload_presets()

    def _on_save(self, _action: Gio.SimpleAction, _param: "Any" = None) -> None:
        self.save_theme()

    def _on_export_theme(self, _action: Gio.SimpleAction, _param: "Any" = None) -> None:
        if not self.plugin_theme:
            no_theme_plugin_error = "No Theme plugin selected"
            raise RuntimeError(no_theme_plugin_error)
        self.plugin_theme.export_dialog(
            transient_for=self,
            theme_name=self.colorscheme_name,
            colorscheme=self.colorscheme,
        )

    def _on_export_icontheme(self, _action: Gio.SimpleAction, _param: "Any" = None) -> None:
        if not self.plugin_icons:
            no_icon_plugin_error = "No Icons plugin selected"
            raise RuntimeError(no_icon_plugin_error)
        self.plugin_icons.export_dialog(
            transient_for=self,
            theme_name=self.colorscheme_name,
            colorscheme=self.colorscheme,
        )

    def _on_export_plugin(self, action: Gio.SimpleAction, _param: "Any" = None) -> None:
        plugin = PluginLoader.get_export_plugins()[
            action.props.name.replace("export_plugin_", "")  # type: ignore[attr-defined]
        ]
        plugin.export_dialog(
            transient_for=self,
            theme_name=self.colorscheme_name,
            colorscheme=self.colorscheme,
        )

    def _before_quit(self) -> None:
        self.ask_unsaved_changes()
        self.ui_settings.window_width, self.ui_settings.window_height = self.get_size()
        self.ui_settings.save()

    def _on_quit(self, _arg1: "Any" = None, _arg2: "Any" = None) -> None:
        self._before_quit()

    def close(self) -> None:  # pylint: disable=arguments-differ
        self._before_quit()
        super().close()

    def _on_show_help(self, _action: "Any", _param: "Any" = None) -> None:
        # @TODO: refactor to use .set_help_overlay() ?
        show_shortcuts(self)

    def _on_show_about(self, _action: "Any", _param: "Any" = None) -> None:
        show_about(self)

    def _on_pane_resize(self, _action: "Any", _param: "Any" = None) -> None:
        position = self.paned_box.get_position()
        self.ui_settings.preset_list_width = position

    ###########################################################################
    # Init widgets:
    ###########################################################################

    def _init_headerbar(self) -> None:  # pylint: disable=too-many-locals,too-many-statements
        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)  # type: ignore[arg-type]
        self.headerbar.props.title = translate("Oo-mox GUI")  # type: ignore[attr-defined]

        # @TODO:
        # new_button = ImageButton("text-x-generic-symbolic", translate("Create New Theme"))
        # self.headerbar.pack_start(new_button)

        import_menu = Gio.Menu()
        import_menu.append_item(Gio.MenuItem.new(
            translate("Oomox Colors File"),
            WindowActions.import_themix_colors.get_id(),
        ))

        for plugin_name, import_plugin in PluginLoader.get_import_plugins().items():
            if import_plugin.import_text:
                import_menu.append_item(Gio.MenuItem.new(
                    import_plugin.import_text or import_plugin.display_name,
                    f"win.import_plugin_{plugin_name}",
                ))

        import_button = ImageMenuButton(
            label=translate("Import"), icon_name="pan-down-symbolic",
            tooltip_text=translate("Import Themes"),
        )
        import_button.set_use_popover(True)
        import_button.set_menu_model(import_menu)
        self.add_action(Gio.PropertyAction(  # type: ignore[call-arg,arg-type]
            name=WindowActions.import_menu,
            object=import_button,
            property_name="active",
        ))
        self.headerbar.pack_start(import_button)  # type: ignore[arg-type]

        #

        save_button = ImageButton(
            "document-save-symbolic", translate("Save Theme"),
        )
        self.attach_action(save_button, WindowActions.save)
        # self.headerbar.pack_start(save_button)

        clone_button = ImageButton(
            "document-save-as-symbolic", translate("Save as…"),
        )
        self.attach_action(clone_button, WindowActions.clone)
        # self.headerbar.pack_start(clone_button)

        rename_button = ImageButton(
            # "preferences-desktop-font-symbolic", "Rename theme"
            "pda-symbolic", translate("Rename Theme…"),
        )
        self.attach_action(rename_button, WindowActions.rename)
        # self.headerbar.pack_start(rename_button)

        remove_button = ImageButton(
            "edit-delete-symbolic", translate("Remove Theme…"),
        )
        self.attach_action(remove_button, WindowActions.remove)

        linked_preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(
            linked_preset_box.get_style_context(), "linked",
        )
        linked_preset_box.add(save_button)
        linked_preset_box.add(clone_button)
        linked_preset_box.add(rename_button)
        # linked_preset_box.add(remove_button)
        self.headerbar.pack_start(linked_preset_box)  # type: ignore[arg-type]
        self.headerbar.pack_start(remove_button)  # type: ignore[arg-type]

        #

        menu = Gio.Menu()
        menu_button = ImageMenuButton("open-menu-symbolic")
        menu_button.set_use_popover(True)
        menu_button.set_menu_model(menu)
        self.add_action(Gio.PropertyAction(  # type: ignore[call-arg,arg-type]
            name=WindowActions.menu,
            object=menu_button,
            property_name="active",
        ))
        self.headerbar.pack_end(menu_button)  # type: ignore[arg-type]

        menu.append_item(Gio.MenuItem.new(
            translate("Keyboard Shortcuts"),
            WindowActions.show_help.get_id(),
        ))
        menu.append_item(Gio.MenuItem.new(
            translate("About"),
            WindowActions.show_about.get_id(),
        ))

        #

        export_theme_button = Gtk.Button(
            label=translate("_Export Theme…"),
            use_underline=True,
            tooltip_text=translate("Export GTK Theme"),
        )
        self.attach_action(export_theme_button, WindowActions.export_theme)

        export_icons_button = Gtk.Button(
            label=translate("Export _Icons…"),
            use_underline=True,
            tooltip_text=translate("Export Icon Theme"),
        )
        self.attach_action(export_icons_button, WindowActions.export_icons)

        export_menu = Gio.Menu()
        if PluginLoader.get_export_plugins():
            for plugin_name, export_plugin in PluginLoader.get_export_plugins().items():
                export_menu.append_item(Gio.MenuItem.new(
                    export_plugin.export_text or export_plugin.display_name,
                    f"win.export_plugin_{plugin_name}",
                ))
        export_button = ImageMenuButton(
            icon_name="pan-down-symbolic",
            tooltip_text=translate("Export Themes"),
        )
        export_button.set_use_popover(True)
        export_button.set_menu_model(export_menu)
        self.add_action(Gio.PropertyAction(  # type: ignore[call-arg,arg-type]
            name=WindowActions.export_menu,
            object=export_button,
            property_name="active",
        ))

        linked_export_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(
            linked_export_box.get_style_context(), "linked",
        )
        linked_export_box.add(export_theme_button)
        linked_export_box.add(export_icons_button)
        linked_export_box.add(export_button)
        self.headerbar.pack_end(linked_export_box)  # type: ignore[arg-type]

        #

        self.set_titlebar(self.headerbar)

    def _init_status_spinner(self) -> None:
        self.spinner = Gtk.Spinner()
        self.spinner_message = Gtk.Label()
        revealer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        revealer_box.add(self.spinner)
        revealer_box.add(self.spinner_message)
        revealer_frame = Gtk.Frame()
        revealer_frame.get_style_context().add_class("app-notification")
        revealer_frame.add(revealer_box)
        self.spinner_revealer = Gtk.Revealer()
        self.spinner_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.spinner_revealer.set_halign(Gtk.Align.CENTER)
        self.spinner_revealer.set_valign(Gtk.Align.START)
        self.spinner_revealer.add(revealer_frame)

    def _init_window(self) -> None:
        self.set_wmclass("oomox", "Oomox")
        self.set_role("Oomox-GUI")
        self.connect("delete-event", self._on_quit)
        self.set_default_size(
            width=self.ui_settings.window_width,
            height=self.ui_settings.window_height,
        )

        self._init_headerbar()
        self._init_status_spinner()

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        overlay = Gtk.Overlay()
        overlay.add(self.box)
        overlay.add_overlay(self.spinner_revealer)
        self.add(overlay)
        # self.add(self.box)

        self.paned_box = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)  # type: ignore[call-arg]
        self.paned_box.set_wide_handle(True)
        self.box.pack_start(self.paned_box, expand=True, fill=True, padding=0)

    def _init_actions(self) -> None:
        self.add_simple_action(
            WindowActions.import_themix_colors, self._on_import_themix_colors,
        )
        for plugin_name in PluginLoader.get_import_plugins():
            self.add_simple_action(
                f"import_plugin_{plugin_name}", self._on_import_plugin,
            )
        self.add_simple_action(WindowActions.clone, self._on_clone)
        self.action_save = self.add_simple_action(WindowActions.save, self._on_save)
        self.action_rename = self.add_simple_action(WindowActions.rename, self._on_rename)
        self.action_remove = self.add_simple_action(WindowActions.remove, self._on_remove)
        self.add_simple_action(WindowActions.export_theme, self._on_export_theme)
        self.add_simple_action(WindowActions.export_icons, self._on_export_icontheme)
        self.add_simple_action(WindowActions.show_help, self._on_show_help)
        self.add_simple_action(WindowActions.show_about, self._on_show_about)
        for plugin_name in PluginLoader.get_export_plugins():
            self.add_simple_action(
                f"export_plugin_{plugin_name}", self._on_export_plugin,
            )

    def _init_plugins(self) -> None:
        # @TODO: ?
        pass

    _window_instance: "OomoxApplicationWindow | None" = None

    @classmethod
    def set_instance(cls, window_instance: "OomoxApplicationWindow") -> None:
        if cls._window_instance:
            raise DoubleWindowError
        cls._window_instance = window_instance

    @classmethod
    def get_instance(cls) -> "OomoxApplicationWindow":
        if not cls._window_instance:
            raise NoWindowError
        return cls._window_instance

    def __init__(self, application: "OomoxGtkApplication") -> None:
        super().__init__(
            application=application,
            title=translate("Themix GUI"),
            startup_id=application.get_application_id(),
        )
        self.application = application
        self.set_instance(self)
        self.colorscheme = {}
        mkdir_p(USER_COLORS_DIR)
        self.ui_settings = UISettings()

        self._init_actions()
        self._init_window()
        self._init_plugins()

        self.preset_list = ThemePresetList(
            preset_select_callback=self.on_preset_selected,
        )
        self.paned_box.pack1(self.preset_list, resize=False, shrink=False)

        self.theme_edit = ThemeColorsList(
            color_edited_callback=self.on_color_edited,
            theme_reload_callback=self.theme_reload,
            transient_for=self,
        )
        self.paned_box.pack2(self.theme_edit, resize=True, shrink=False)

        self.box.pack_start(Gtk.Separator(), expand=False, fill=False, padding=0)
        self.preview = ThemePreview()
        self.box.pack_start(self.preview, expand=False, fill=False, padding=0)

        self.show_all()
        self.theme_edit.hide_all_rows()
        self.preview.hide()

        self.paned_box.set_position(self.ui_settings.preset_list_width)
        self.paned_box.connect("notify::position", self._on_pane_resize)


class OomoxGtkApplication(Gtk.Application):

    window: OomoxApplicationWindow | None = None

    def __init__(self) -> None:
        super().__init__(
            application_id="com.github.themix_project.Oomox",
            flags=(
                Gio.ApplicationFlags.HANDLES_COMMAND_LINE |
                Gio.ApplicationFlags.NON_UNIQUE
            ),
        )
        # @TODO: use oomox-gui as the only one entrypoint to all cli tools
        # self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE,
        # GLib.OptionArg.NONE, "Command line test", None)

    def do_startup(self) -> None:  # pylint: disable=arguments-differ

        Gtk.Application.do_startup(self)

        quit_action = Gio.SimpleAction.new(
            AppActions.quit_action, None,
        )
        quit_action.connect("activate", self._on_quit)
        self.add_action(quit_action)

        _shortcuts = {}

        def set_accels_for_action(
                action: ActionProperty | None,
                accels: list[str],
                action_id: str | None = None,
        ) -> None:
            if not (action or action_id):
                required_props_error = "Either `action` or `action_id` should be set"
                raise TypeError(required_props_error)
            action_id = action_id or action.get_id()  # type: ignore[union-attr]
            for accel in accels:
                if accel in _shortcuts:
                    shortcut_already_set = f'Shortcut "{accel}" is already set.'
                    raise RuntimeError(shortcut_already_set)
                _shortcuts[accel] = action_id
            self.set_accels_for_action(action_id, accels)

        set_accels_for_action(AppActions.quit_action, ["<Primary>Q"])

        set_accels_for_action(WindowActions.import_menu, ["<Primary>M"])
        set_accels_for_action(WindowActions.clone, ["<Shift><Primary>S"])
        set_accels_for_action(WindowActions.save, ["<Primary>S"])
        set_accels_for_action(WindowActions.rename, ["F2"])
        set_accels_for_action(WindowActions.remove, ["<Primary>Delete"])
        set_accels_for_action(WindowActions.export_theme, ["<Primary>E"])
        set_accels_for_action(WindowActions.export_icons, ["<Primary>I"])
        set_accels_for_action(WindowActions.export_menu, ["<Primary>O"])
        set_accels_for_action(WindowActions.menu, ["F10"])
        set_accels_for_action(WindowActions.show_help, ["<Primary>question"])

        _plugin_shortcuts: dict[str, str] = {}
        import_and_export_plugins: """Sequence[
                tuple[Mapping[str, OomoxImportPlugin | OomoxExportPlugin], str]
        ]""" = (
            (PluginLoader.get_import_plugins(), "import_plugin_{}"),
            (PluginLoader.get_export_plugins(), "export_plugin_{}"),
        )
        for plugin_list, plugin_action_template in import_and_export_plugins:
            for plugin_name, plugin in plugin_list.items():
                if not plugin.shortcut:
                    continue
                if plugin.shortcut in _shortcuts:
                    _is_plugin_shortcut = plugin.shortcut in _plugin_shortcuts
                    error_dialog = Gtk.MessageDialog(
                        text=translate('Error while loading plugin "{plugin_name}"').format(
                            plugin_name=plugin_name,
                        ),
                        secondary_text="\n".join((
                            translate(
                                'Shortcut "{shortcut}" already assigned to {action_type} "{name}".',
                            ).format(
                                shortcut=plugin.shortcut,
                                action_type=translate(
                                    "plugin"
                                    if _is_plugin_shortcut else
                                    "action",
                                ),
                                name=(
                                    _plugin_shortcuts[plugin.shortcut]
                                    if _is_plugin_shortcut
                                    else _shortcuts[plugin.shortcut]
                                ),
                            ),
                            translate(
                                'Shortcut will be disabled for "{plugin_name}" plugin.',
                            ).format(
                                plugin_name=plugin_name,
                            ),
                        )),
                        buttons=Gtk.ButtonsType.CLOSE,
                    )
                    error_dialog.run()
                    error_dialog.destroy()
                    continue
                action_name = plugin_action_template.format(plugin_name)
                set_accels_for_action(
                    action=None,
                    accels=[plugin.shortcut],
                    action_id=f"win.{action_name}",
                )
                _plugin_shortcuts[plugin.shortcut] = plugin_name

    def do_activate(self) -> None:  # pylint: disable=arguments-differ
        if not self.window:
            self.window = OomoxApplicationWindow(application=self)
        self.window.present()

    def do_command_line(self, _command_line: None) -> int:  # pylint: disable=arguments-differ
        # options = command_line.get_options_dict()
        # if options.contains("test"):
        #     print("Test argument received")
        self.activate()
        return 0

    def quit(self) -> None:  # pylint: disable=arguments-differ  # noqa: A003
        if self.window:
            self.window.close()
        else:
            super().quit()

    def _on_quit(self, _action: "Any", _param: "Any | None" = None) -> None:
        self.quit()


def main() -> None:

    app = OomoxGtkApplication()

    def handle_sig_int(*_whatever: "Any") -> None:  # pragma: no cover
        log_error("\n\nCanceled by user (SIGINT)")
        app.quit()
        sys.exit(128 + signal.SIGINT)

    def handle_sig_term(*_whatever: "Any") -> None:  # pragma: no cover
        log_error("\n\nTerminated by SIGTERM")
        app.quit()
        sys.exit(128 + signal.SIGTERM)

    signal.signal(signal.SIGINT, handle_sig_int)
    signal.signal(signal.SIGTERM, handle_sig_term)
    app.run(sys.argv)


if __name__ == "__main__":
    main()
