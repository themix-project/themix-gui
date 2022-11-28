#!/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import signal
import shutil
import traceback
from typing import Callable, Any

from gi.repository import Gtk, Gio, GLib, Gdk

from .i18n import translate
from .config import USER_COLORS_DIR
from .helpers import mkdir_p
from .gtk_helpers import (
    ImageButton, ImageMenuButton,
    EntryDialog, YesNoDialog,
    ActionsEnum, ActionProperty, warn_once,
)
from .theme_file import (
    get_user_theme_path, is_user_colorscheme, is_colorscheme_exists,
    save_colorscheme, remove_colorscheme, import_colorscheme,
)
from .theme_file_parser import read_colorscheme_from_path
from .preset_list import ThemePresetList
from .colors_list import ThemeColorsList
from .preview import ThemePreview
from .terminal import generate_terminal_colors_for_oomox
from .plugin_loader import PluginLoader
from .plugin_api import PLUGIN_PATH_PREFIX
from .settings import UI_SETTINGS
from .about import show_about
from .shortcuts import show_shortcuts


from typing import TYPE_CHECKING  # pylint: disable=wrong-import-order
if TYPE_CHECKING:
    from typing import Optional  # noqa


class DoubleWindowError(RuntimeError):

    def __init__(self):
        super().__init__('App window already set')


class NoWindowError(RuntimeError):

    def __init__(self):
        super().__init__('App window not yet set')


class NewDialog(EntryDialog):

    def __init__(
            self, transient_for,
            title=translate("New Theme"),
            text=translate("Please input new theme name:"),
            entry_text=None
    ):
        super().__init__(
            transient_for=transient_for,
            title=title,
            text=text,
            entry_text=entry_text
        )


class RenameDialog(NewDialog):

    def __init__(self, transient_for, entry_text):
        super().__init__(
            transient_for=transient_for,
            title=translate("Rename Theme"),
            entry_text=entry_text
        )


class UnsavedDialog(YesNoDialog):

    def __init__(self, transient_for):
        super().__init__(
            transient_for=transient_for,
            title=translate("Unsaved Changes"),
            text=translate("There are unsaved changes.\nSave them?")
        )


class RemoveDialog(YesNoDialog):

    def __init__(self, transient_for):
        super().__init__(
            transient_for=transient_for,
            title=translate("Remove Theme"),
            text=translate(
                "Are you sure you want to delete the colorscheme?\n"
                "This can not be undone."
            )
        )


def dialog_is_yes(dialog):
    return dialog.run() in (Gtk.ResponseType.YES, Gtk.ResponseType.OK)


class AppActions(ActionsEnum):
    _target = "app"
    quit = ActionProperty(_target, "quit")


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

    def _action_tooltip(self, action, tooltip):
        action_id = action.get_id()
        accels = self.get_application().get_accels_for_action(action_id)
        if accels:
            key, mods = Gtk.accelerator_parse(accels[0])
            tooltip += f' ({Gtk.accelerator_get_label(key, mods)})'
        return tooltip

    def attach_action(self, widget, action, with_tooltip=True):
        action_id = action.get_id()
        widget.set_action_name(action_id)
        if with_tooltip:
            tooltip = self._action_tooltip(action, widget.get_tooltip_text())
            widget.set_tooltip_text(tooltip)

    def add_simple_action(self, action_name, callback):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect("activate", callback)
        self.add_action(action)
        return action


class OomoxApplicationWindow(WindowWithActions):  # pylint: disable=too-many-instance-attributes,too-many-public-methods

    colorscheme_name = None
    colorscheme_path = None
    colorscheme = None
    colorscheme_is_user = None
    theme_edited = False
    #
    plugin_theme = None
    plugin_icons = None
    #
    # actions:
    save_action = None
    rename_action = None
    remove_action = None
    #
    # widget sections:
    box = None
    headerbar = None
    theme_edit = None
    preset_list = None
    preview = None
    spinner = None
    spinner_message = None
    spinner_revealer = None

    _currently_focused_widget = None
    _inhibit_id = None

    def _unset_save_needed(self):
        self.headerbar.props.title = self.colorscheme_name
        if self._inhibit_id:
            self.application.uninhibit(self._inhibit_id)
        self.save_action.set_enabled(False)
        self.theme_edited = False

    def _set_save_needed(self):
        if not self.theme_edited:
            self.headerbar.props.title = "*" + self.colorscheme_name
        self._inhibit_id = self.application.inhibit(
            self,
            Gtk.ApplicationInhibitFlags.LOGOUT | Gtk.ApplicationInhibitFlags.SUSPEND,
            translate("There are unsaved changes.\nSave them?")
        )
        self.save_action.set_enabled(True)
        self.theme_edited = True

    def save_theme(self, name=None):
        if not name:
            name = self.colorscheme_name
        if not self.preset_list.preset_is_saveable():
            if (
                    name.startswith(PLUGIN_PATH_PREFIX)
            ) or (
                self.ask_colorscheme_exists(name)
            ):
                self.clone_theme()
                return
        new_path = save_colorscheme(name, self.colorscheme)
        self._unset_save_needed()

        old_path = self.colorscheme_path
        self.colorscheme_name = name
        self.colorscheme_path = new_path
        if old_path != new_path:
            self.reload_presets()

    def remove_theme(self, path=None):
        if not path:
            path = self.colorscheme_path
        try:
            remove_colorscheme(path)
        except FileNotFoundError:
            pass

    def import_theme_from_path(self, path, new_name):
        old_path = self.colorscheme_path
        new_path = import_colorscheme(new_name, path)
        self.colorscheme_name = new_name
        self.colorscheme_path = new_path
        if old_path != new_path:
            self.reload_presets()
        self.on_preset_selected(new_name, new_path)

    def import_themix_colors(self):
        self.ask_unsaved_changes()

        filechooser_dialog = Gtk.FileChooserNative.new(
            translate("Please choose a file with oomox colors"),
            self,
            Gtk.FileChooserAction.OPEN
        )
        filechooser_response = filechooser_dialog.run()
        if filechooser_response in (
                Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT
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
                    new_name=new_theme_name
                )
                return

    def import_from_plugin(self, plugin):
        self.ask_unsaved_changes()
        filechooser_dialog = Gtk.FileChooserNative.new(
            translate("Please choose an image file"),
            self,
            Gtk.FileChooserAction.OPEN
        )
        filechooser_response = filechooser_dialog.run()
        if filechooser_response in (
                Gtk.ResponseType.CANCEL, Gtk.ResponseType.DELETE_EVENT
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

    def clone_theme(self):
        new_theme_name = self.colorscheme_name
        if is_colorscheme_exists(get_user_theme_path(new_theme_name)):
            new_theme_name += '_'
        if new_theme_name.startswith(PLUGIN_PATH_PREFIX):
            new_theme_name = '/'.join(new_theme_name.split('/')[1:])
        dialog = NewDialog(transient_for=self, entry_text=new_theme_name)
        if not dialog_is_yes(dialog):
            return
        new_theme_name = dialog.entry_text
        if not self.ask_colorscheme_exists(new_theme_name):
            self.save_theme(new_theme_name)
        else:
            self.clone_theme()

    def rename_theme(self, entry_text=None):
        dialog = RenameDialog(
            transient_for=self,
            entry_text=entry_text or self.colorscheme_name
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

    def ask_unsaved_changes(self):
        if self.theme_edited:
            if dialog_is_yes(UnsavedDialog(transient_for=self)):
                self.save_theme()
            # else:  @TODO: remove this branch?
                # self.theme_edited = False

    def ask_colorscheme_exists(self, colorscheme_name):
        if not is_colorscheme_exists(get_user_theme_path(colorscheme_name)):
            return False
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK,
            message_format=translate("Colorscheme with such name already exists")
        )
        dialog.run()
        dialog.destroy()
        return True

    def _select_theme_plugin(self):
        theme_plugin_name = self.colorscheme['THEME_STYLE']
        self.plugin_theme = None
        for theme_plugin in PluginLoader.get_theme_plugins().values():
            if theme_plugin.name == theme_plugin_name:
                self.plugin_theme = theme_plugin

    def _select_icons_plugin(self):
        icons_plugin_name = self.colorscheme['ICONS_STYLE']
        self.plugin_icons = None
        for icons_plugin in PluginLoader.get_icons_plugins().values():
            if icons_plugin.name == icons_plugin_name:
                self.plugin_icons = icons_plugin

    def load_colorscheme(self, colorscheme):
        self.colorscheme = colorscheme
        self._select_theme_plugin()
        self._select_icons_plugin()
        self.generate_terminal_colors(callback=self._load_colorscheme_callback)

    def _load_colorscheme_callback(self):
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
                text=theme_value,
                buttons=Gtk.ButtonsType.CLOSE
            )

    @staticmethod
    def schedule_task(task, *args):
        Gdk.threads_add_idle(GLib.PRIORITY_LOW, task, *args)

    def on_preset_selected(self, selected_preset, selected_preset_path):
        self.ask_unsaved_changes()
        self.colorscheme_name = selected_preset
        self.colorscheme_path = selected_preset_path
        read_colorscheme_from_path(selected_preset_path, callback=self._on_preset_selected_callback)

    def _on_preset_selected_callback(self, colorscheme):
        self.load_colorscheme(colorscheme)
        self.colorscheme_is_user = is_user_colorscheme(self.colorscheme_path)
        self.theme_edit.open_theme(self.colorscheme)
        self._unset_save_needed()
        self.rename_action.set_enabled(self.preset_list.preset_is_saveable())
        self.remove_action.set_enabled(self.colorscheme_is_user)

    def theme_reload(self):
        self.on_preset_selected(
            self.colorscheme_name, self.colorscheme_path
        )
        return self.colorscheme

    def generate_terminal_colors(self, callback):
        def _generate_terminal_colors(colors):
            self.colorscheme.update(colors)
            callback()

        generate_terminal_colors_for_oomox(
            self.colorscheme,
            app=self, result_callback=_generate_terminal_colors,
        )

    def on_color_edited(self, colorscheme):
        self.load_colorscheme(colorscheme)
        self._set_save_needed()

    def reload_presets(self):
        self.preset_list.reload_presets(self.colorscheme_path)

    def disable(self, message=''):
        def disable_ui_callback():
            self._currently_focused_widget = self.get_focus()
            self.spinner_revealer.set_reveal_child(True)
            self.preset_list.set_sensitive(False)
            self.theme_edit.set_sensitive(False)
            Gtk.main_iteration_do(False)
            self.spinner_message.set_text(message)
            self.spinner.start()

        GLib.timeout_add(0, disable_ui_callback, priority=GLib.PRIORITY_HIGH)

    def enable(self):
        def enable_ui_callback():
            self.spinner_revealer.set_reveal_child(False)
            self.preset_list.set_sensitive(True)
            self.theme_edit.set_sensitive(True)
            self.set_focus(self._currently_focused_widget)
            self.spinner.stop()

        GLib.idle_add(enable_ui_callback, priority=GLib.PRIORITY_LOW)

    ###########################################################################
    # Signal handlers:
    ###########################################################################

    def _on_import_themix_colors(self, _action, _param=None):
        return self.import_themix_colors()

    def _on_import_plugin(self, action, _param=None):
        plugin = PluginLoader.get_import_plugins()[
            action.props.name.replace('import_plugin_', '')
        ]
        self.import_from_plugin(plugin)

    def _on_clone(self, _action, _param=None):
        return self.clone_theme()

    def _on_rename(self, _action, _param=None):
        self.rename_theme()

    def _on_remove(self, _action, _param=None):
        if not dialog_is_yes(RemoveDialog(transient_for=self)):
            return
        self.remove_theme()
        self.rename_action.set_enabled(False)
        self.remove_action.set_enabled(False)
        self.reload_presets()

    def _on_save(self, _action, _param=None):
        self.save_theme()

    def _on_export_theme(self, _action, _param=None):
        self.plugin_theme.export_dialog(
            transient_for=self,
            theme_name=self.colorscheme_name,
            colorscheme=self.colorscheme
        )

    def _on_export_icontheme(self, _action, _param=None):
        self.plugin_icons.export_dialog(
            transient_for=self,
            theme_name=self.colorscheme_name,
            colorscheme=self.colorscheme
        )

    def _on_export_plugin(self, action, _param=None):
        plugin = PluginLoader.get_export_plugins()[
            action.props.name.replace('export_plugin_', '')
        ]
        plugin.export_dialog(
            transient_for=self,
            theme_name=self.colorscheme_name,
            colorscheme=self.colorscheme
        )

    def _before_quit(self):
        self.ask_unsaved_changes()
        UI_SETTINGS.window_width, UI_SETTINGS.window_height = self.get_size()
        UI_SETTINGS.save()

    def _on_quit(self, _arg1=None, _arg2=None):
        self._before_quit()

    def close(self):  # pylint: disable=arguments-differ
        self._before_quit()
        super().close()

    def _on_show_help(self, _action, _param=None):
        # @TODO: refactor to use .set_help_overlay() ?
        show_shortcuts(self)

    def _on_show_about(self, _action, _param=None):
        show_about(self)

    def _on_pane_resize(self, _action, _param=None):
        position = self.paned_box.get_position()
        UI_SETTINGS.preset_list_width = position

    ###########################################################################
    # Init widgets:
    ###########################################################################

    def _init_headerbar(self):  # pylint: disable=too-many-locals,too-many-statements
        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)  # type: ignore[arg-type]
        self.headerbar.props.title = translate("Oo-mox GUI")  # type: ignore[attr-defined]

        # @TODO:
        # new_button = ImageButton("text-x-generic-symbolic", translate("Create New Theme"))  # noqa
        # self.headerbar.pack_start(new_button)

        import_menu = Gio.Menu()
        import_menu.append_item(Gio.MenuItem.new(
            translate("Oomox Colors File"),
            WindowActions.import_themix_colors.get_id()
        ))

        for plugin_name, plugin in PluginLoader.get_import_plugins().items():
            if plugin.import_text:
                import_menu.append_item(Gio.MenuItem.new(
                    plugin.import_text or plugin.display_name,
                    f"win.import_plugin_{plugin_name}"
                ))

        import_button = ImageMenuButton(
            label=translate("Import"), icon_name="pan-down-symbolic",
            tooltip_text=translate("Import Themes")
        )
        import_button.set_use_popover(True)
        import_button.set_menu_model(import_menu)
        self.add_action(Gio.PropertyAction(  # type: ignore[call-arg,arg-type]
            name=WindowActions.import_menu,
            object=import_button,
            property_name="active"
        ))
        self.headerbar.pack_start(import_button)  # type: ignore[arg-type]

        #

        save_button = ImageButton(
            "document-save-symbolic", translate("Save Theme")
        )
        self.attach_action(save_button, WindowActions.save)
        # self.headerbar.pack_start(save_button)

        clone_button = ImageButton(
            "document-save-as-symbolic", translate("Save as…")
        )
        self.attach_action(clone_button, WindowActions.clone)
        # self.headerbar.pack_start(clone_button)

        rename_button = ImageButton(
            # "preferences-desktop-font-symbolic", "Rename theme"
            "pda-symbolic", translate("Rename Theme…")
        )
        self.attach_action(rename_button, WindowActions.rename)
        # self.headerbar.pack_start(rename_button)

        remove_button = ImageButton(
            "edit-delete-symbolic", translate("Remove Theme…")
        )
        self.attach_action(remove_button, WindowActions.remove)

        linked_preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(
            linked_preset_box.get_style_context(), "linked"
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
            property_name="active"
        ))
        self.headerbar.pack_end(menu_button)  # type: ignore[arg-type]

        menu.append_item(Gio.MenuItem.new(
            translate("Keyboard Shortcuts"),
            WindowActions.show_help.get_id()
        ))
        menu.append_item(Gio.MenuItem.new(
            translate("About"),
            WindowActions.show_about.get_id()
        ))

        #

        export_theme_button = Gtk.Button(
            label=translate("_Export Theme…"),
            use_underline=True,
            tooltip_text=translate("Export GTK Theme")
        )
        self.attach_action(export_theme_button, WindowActions.export_theme)

        export_icons_button = Gtk.Button(
            label=translate("Export _Icons…"),
            use_underline=True,
            tooltip_text=translate("Export Icon Theme")
        )
        self.attach_action(export_icons_button, WindowActions.export_icons)

        export_menu = Gio.Menu()
        if PluginLoader.get_export_plugins():
            for plugin_name, plugin in PluginLoader.get_export_plugins().items():
                export_menu.append_item(Gio.MenuItem.new(
                    plugin.export_text or plugin.display_name,
                    f"win.export_plugin_{plugin_name}"
                ))
        export_button = ImageMenuButton(
            icon_name="pan-down-symbolic",
            tooltip_text=translate("Export Themes")
        )
        export_button.set_use_popover(True)
        export_button.set_menu_model(export_menu)
        self.add_action(Gio.PropertyAction(  # type: ignore[call-arg,arg-type]
            name=WindowActions.export_menu,
            object=export_button,
            property_name="active"
        ))

        linked_export_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(
            linked_export_box.get_style_context(), "linked"
        )
        linked_export_box.add(export_theme_button)
        linked_export_box.add(export_icons_button)
        linked_export_box.add(export_button)
        self.headerbar.pack_end(linked_export_box)  # type: ignore[arg-type]

        #

        self.set_titlebar(self.headerbar)

    def _init_status_spinner(self):
        self.spinner = Gtk.Spinner()
        self.spinner_message = Gtk.Label()
        revealer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        revealer_box.add(self.spinner)
        revealer_box.add(self.spinner_message)
        revealer_frame = Gtk.Frame()
        revealer_frame.get_style_context().add_class('app-notification')
        revealer_frame.add(revealer_box)
        self.spinner_revealer = Gtk.Revealer()
        self.spinner_revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.spinner_revealer.set_halign(Gtk.Align.CENTER)
        self.spinner_revealer.set_valign(Gtk.Align.START)
        self.spinner_revealer.add(revealer_frame)

    def _init_window(self):
        self.set_wmclass("oomox", "Oomox")
        self.set_role("Oomox-GUI")
        self.connect("delete-event", self._on_quit)
        self.set_default_size(
            width=UI_SETTINGS.window_width,
            height=UI_SETTINGS.window_height
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

    def _init_actions(self):
        self.add_simple_action(
            WindowActions.import_themix_colors, self._on_import_themix_colors
        )
        for plugin_name in PluginLoader.get_import_plugins():
            self.add_simple_action(
                f"import_plugin_{plugin_name}", self._on_import_plugin
            )
        self.add_simple_action(WindowActions.clone, self._on_clone)
        self.save_action = self.add_simple_action(WindowActions.save, self._on_save)
        self.rename_action = self.add_simple_action(WindowActions.rename, self._on_rename)
        self.remove_action = self.add_simple_action(WindowActions.remove, self._on_remove)
        self.add_simple_action(WindowActions.export_theme, self._on_export_theme)
        self.add_simple_action(WindowActions.export_icons, self._on_export_icontheme)
        self.add_simple_action(WindowActions.show_help, self._on_show_help)
        self.add_simple_action(WindowActions.show_about, self._on_show_about)
        for plugin_name in PluginLoader.get_export_plugins():
            self.add_simple_action(
                f"export_plugin_{plugin_name}", self._on_export_plugin
            )

    def _init_plugins(self):
        pass

    _window_instance: 'Optional[OomoxApplicationWindow]' = None

    @classmethod
    def set_instance(cls, window_instance):
        if cls._window_instance:
            raise DoubleWindowError()
        cls._window_instance = window_instance

    @classmethod
    def get_instance(cls):
        if not cls._window_instance:
            raise NoWindowError()
        return cls._window_instance

    def __init__(self, application):
        super().__init__(
            application=application,
            title=translate("Oo-mox GUI"),
            startup_id=application.get_application_id(),
        )
        self.application = application
        self.set_instance(self)
        self.colorscheme = {}
        mkdir_p(USER_COLORS_DIR)

        self._init_actions()
        self._init_window()
        self._init_plugins()

        self.preset_list = ThemePresetList(
            preset_select_callback=self.on_preset_selected
        )
        self.paned_box.pack1(self.preset_list, resize=False, shrink=False)

        self.theme_edit = ThemeColorsList(
            color_edited_callback=self.on_color_edited,
            theme_reload_callback=self.theme_reload,
            transient_for=self
        )
        self.paned_box.pack2(self.theme_edit, resize=True, shrink=False)

        self.box.pack_start(Gtk.Separator(), expand=False, fill=False, padding=0)
        self.preview = ThemePreview()
        self.box.pack_start(self.preview, expand=False, fill=False, padding=0)

        self.show_all()
        self.theme_edit.hide_all_rows()
        self.preview.hide()

        self.paned_box.set_position(UI_SETTINGS.preset_list_width)
        self.paned_box.connect("notify::position", self._on_pane_resize)


class OomoxGtkApplication(Gtk.Application):

    window = None

    def __init__(self):
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

    def do_startup(self):  # pylint: disable=arguments-differ

        Gtk.Application.do_startup(self)

        quit_action = Gio.SimpleAction.new(
            AppActions.quit, None
        )
        quit_action.connect("activate", self._on_quit)
        self.add_action(quit_action)

        _shortcuts = {}

        def set_accels_for_action(action, accels, action_id=None):
            action_id = action_id or action.get_id()
            for accel in accels:
                if accel in _shortcuts:
                    raise Exception(f'Shortcut "{accel}" is already set.')
                _shortcuts[accel] = action_id
            self.set_accels_for_action(action_id, accels)

        set_accels_for_action(AppActions.quit, ["<Primary>Q"])

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
        for plugin_list, plugin_action_template in (
            (PluginLoader.get_import_plugins(), "import_plugin_{}"),
            (PluginLoader.get_export_plugins(), "export_plugin_{}"),
        ):
            for plugin_name, plugin in plugin_list.items():
                if not plugin.shortcut:
                    continue
                if plugin.shortcut in _shortcuts:
                    _is_plugin_shortcut = plugin.shortcut in _plugin_shortcuts
                    error_dialog = Gtk.MessageDialog(
                        text=translate('Error while loading plugin "{plugin_name}"').format(
                            plugin_name=plugin_name
                        ),
                        secondary_text='\n'.join((
                            translate(
                                'Shortcut "{shortcut}" already assigned to {action_type} "{name}".'
                            ).format(
                                shortcut=plugin.shortcut,
                                action_type=translate('plugin') if _is_plugin_shortcut else translate('action'),
                                name=(
                                    _plugin_shortcuts[plugin.shortcut]
                                    if _is_plugin_shortcut
                                    else _shortcuts[plugin.shortcut]
                                )
                            ),
                            translate('Shortcut will be disabled for "{plugin_name}" plugin.').format(
                                plugin_name=plugin_name
                            )
                        )),
                        buttons=Gtk.ButtonsType.CLOSE
                    )
                    error_dialog.run()
                    error_dialog.destroy()
                    continue
                action_name = plugin_action_template.format(plugin_name)
                set_accels_for_action(
                    action_name,
                    [plugin.shortcut],
                    f"win.{action_name}"
                )
                _plugin_shortcuts[plugin.shortcut] = plugin_name

    def do_activate(self):  # pylint: disable=arguments-differ
        if not self.window:
            self.window = OomoxApplicationWindow(application=self)
        self.window.present()

    def do_command_line(self, _command_line):  # pylint: disable=arguments-differ
        # options = command_line.get_options_dict()
        # if options.contains("test"):
        #     print("Test argument received")
        self.activate()
        return 0

    def quit(self):  # pylint: disable=arguments-differ
        if self.window:
            self.window.close()
        else:
            super().quit()

    def _on_quit(self, _action, _param=None):
        self.quit()


def main():

    app = OomoxGtkApplication()

    def handle_sig_int(*_whatever):  # pragma: no cover
        sys.stderr.write("\n\nCanceled by user (SIGINT)\n")
        app.quit()
        sys.exit(128 + signal.SIGINT)

    def handle_sig_term(*_whatever):  # pragma: no cover
        sys.stderr.write("\n\nTerminated by SIGTERM\n")
        app.quit()
        sys.exit(128 + signal.SIGTERM)

    signal.signal(signal.SIGINT, handle_sig_int)
    signal.signal(signal.SIGTERM, handle_sig_term)
    app.run(sys.argv)


if __name__ == "__main__":
    main()
