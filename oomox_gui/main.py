#!/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import signal
import shutil
import traceback

from gi.repository import Gtk, Gio, GLib, Gdk

from .i18n import _
from .config import USER_COLORS_DIR, SCRIPT_DIR
from .helpers import mkdir_p
from .gtk_helpers import (
    ImageButton, ImageMenuButton,
    EntryDialog, YesNoDialog,
    ActionsEnum,
)
from .theme_file import (
    get_user_theme_path, is_user_colorscheme, is_colorscheme_exists,
    save_colorscheme, remove_colorscheme, import_colorscheme,
)
from .theme_file_parser import read_colorscheme_from_path
from .preset_list import ThemePresetList
from .colors_list import ThemeColorsList
from .preview import ThemePreview
from .export_common import export_terminal_theme
from .terminal import generate_terminal_colors_for_oomox
from .plugin_loader import (
    THEME_PLUGINS, ICONS_PLUGINS, IMPORT_PLUGINS, EXPORT_PLUGINS,
)
from .plugin_api import PLUGIN_PATH_PREFIX
from .settings import UI_SETTINGS


class NewDialog(EntryDialog):

    def __init__(
            self, transient_for,
            title=_("New Theme"),
            text=_("Please input new theme name:"),
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
            title=_("Rename Theme"),
            entry_text=entry_text
        )


class UnsavedDialog(YesNoDialog):

    def __init__(self, transient_for):
        super().__init__(
            transient_for=transient_for,
            title=_("Unsaved Changes"),
            text=_("There are unsaved changes.\nSave them?")
        )


class RemoveDialog(YesNoDialog):

    def __init__(self, transient_for):
        super().__init__(
            transient_for=transient_for,
            title=_("Remove Theme"),
            text=_("Are you sure you want to delete the colorscheme?\n"
                   "This can not be undone.")
        )


def dialog_is_yes(dialog):
    return dialog.run() in (Gtk.ResponseType.YES, Gtk.ResponseType.OK)


class AppActions(ActionsEnum):
    _target = "app"
    quit = "quit"


class WindowActions(ActionsEnum):
    _target = "win"
    import_menu = "import_menu"
    import_themix_colors = "import_themix_colors"
    clone = "clone"
    export_icons = "icons"
    export_theme = "theme"
    export_terminal = "terminal"
    export_menu = "export_menu"
    menu = "menu"
    remove = "remove"
    rename = "rename"
    save = "save"
    show_help = "show_help"


class WindowWithActions(Gtk.ApplicationWindow):

    def _action_tooltip(self, action, tooltip):
        action_id = action.get_id()
        accels = self.get_application().get_accels_for_action(action_id)
        if accels:
            key, mods = Gtk.accelerator_parse(accels[0])
            tooltip += ' ({})'.format(Gtk.accelerator_get_label(key, mods))
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
            _("There are unsaved changes.\nSave them?")
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
            _("Please choose a file with oomox colors"),
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
            _("Please choose an image file"),
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
            message_format=_("Colorscheme with such name already exists")
        )
        dialog.run()
        dialog.destroy()
        return True

    def _select_theme_plugin(self):
        theme_plugin_name = self.colorscheme['THEME_STYLE']
        self.plugin_theme = None
        for theme_plugin in THEME_PLUGINS.values():
            if theme_plugin.name == theme_plugin_name:
                self.plugin_theme = theme_plugin

    def _select_icons_plugin(self):
        icons_plugin_name = self.colorscheme['ICONS_STYLE']
        self.plugin_icons = None
        for icons_plugin in ICONS_PLUGINS.values():
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
            error_dialog = Gtk.MessageDialog(
                text=theme_value,
                # secondary_text='',
                buttons=Gtk.ButtonsType.CLOSE
            )
            error_dialog.run()
            error_dialog.destroy()

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

    def show_help(self):
        # @TODO: refactor to use .set_help_overlay() ?
        path = os.path.join(SCRIPT_DIR, 'shortcuts.ui')
        obj_id = "shortcuts"

        builder = Gtk.Builder.new_from_file(path)
        overlay = builder.get_object(obj_id)
        overlay.set_transient_for(self)
        overlay.set_title("Oomox Keyboard Shortcuts")
        overlay.set_wmclass("oomox", "Oomox")
        overlay.set_role("Oomox-Shortcuts")
        overlay.show()

    ###########################################################################
    # Signal handlers:
    ###########################################################################

    def _on_import_themix_colors(self, _action, _param=None):
        return self.import_themix_colors()

    def _on_import_plugin(self, action, _param=None):
        plugin = IMPORT_PLUGINS[
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

    def _on_export_terminal(self, _action, _param=None):
        export_terminal_theme(transient_for=self, colorscheme=self.colorscheme)

    def _on_export_plugin(self, action, _param=None):
        plugin = EXPORT_PLUGINS[
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
        self.show_help()

    def _on_pane_resize(self, _action, _param=None):
        position = self.paned_box.get_position()
        UI_SETTINGS.preset_list_width = position

    ###########################################################################
    # Init widgets:
    ###########################################################################

    def _init_headerbar(self):  # pylint: disable=too-many-locals,too-many-statements
        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.props.title = _("Oo-mox GUI")

        # @TODO:
        # new_button = ImageButton("text-x-generic-symbolic", _("Create New Theme"))  # noqa
        # self.headerbar.pack_start(new_button)

        import_menu = Gio.Menu()
        import_menu.append_item(Gio.MenuItem.new(
            _("Oomox Colors File"),
            WindowActions.import_themix_colors.get_id()  # pylint:disable=no-member
        ))

        for plugin_name, plugin in IMPORT_PLUGINS.items():
            if plugin.import_text:
                import_menu.append_item(Gio.MenuItem.new(
                    plugin.import_text or plugin.display_name,
                    "win.import_plugin_{}".format(plugin_name)
                ))

        import_button = ImageMenuButton(
            label=_("Import"), icon_name="pan-down-symbolic",
            tooltip_text=_("Import Themes")
        )
        import_button.set_use_popover(True)
        import_button.set_menu_model(import_menu)
        self.add_action(Gio.PropertyAction(
            name=WindowActions.import_menu,
            object=import_button,
            property_name="active"
        ))
        self.headerbar.pack_start(import_button)

        #

        save_button = ImageButton(
            "document-save-symbolic", _("Save Theme")
        )
        self.attach_action(save_button, WindowActions.save)
        # self.headerbar.pack_start(save_button)

        clone_button = ImageButton(
            "document-save-as-symbolic", _("Save as…")
        )
        self.attach_action(clone_button, WindowActions.clone)
        # self.headerbar.pack_start(clone_button)

        rename_button = ImageButton(
            # "preferences-desktop-font-symbolic", "Rename theme"
            "pda-symbolic", _("Rename Theme…")
        )
        self.attach_action(rename_button, WindowActions.rename)
        # self.headerbar.pack_start(rename_button)

        remove_button = ImageButton(
            "edit-delete-symbolic", _("Remove Theme…")
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
        self.headerbar.pack_start(linked_preset_box)
        self.headerbar.pack_start(remove_button)

        #

        menu = Gio.Menu()
        menu_button = ImageMenuButton("open-menu-symbolic")
        menu_button.set_use_popover(True)
        menu_button.set_menu_model(menu)
        self.add_action(Gio.PropertyAction(
            name=WindowActions.menu,
            object=menu_button,
            property_name="active"
        ))
        self.headerbar.pack_end(menu_button)

        show_help_menuitem = Gio.MenuItem.new(
            _("Keyboard Shortcuts"),
            WindowActions.show_help.get_id()  # pylint:disable=no-member
        )
        menu.append_item(show_help_menuitem)

        #

        export_theme_button = Gtk.Button(
            label=_("_Export Theme…"),
            use_underline=True,
            tooltip_text=_("Export GTK Theme")
        )
        self.attach_action(export_theme_button, WindowActions.export_theme)

        export_icons_button = Gtk.Button(
            label=_("Export _Icons…"),
            use_underline=True,
            tooltip_text=_("Export Icon Theme")
        )
        self.attach_action(export_icons_button, WindowActions.export_icons)

        export_menu = Gio.Menu()
        export_menu.append_item(Gio.MenuItem.new(
            _("Export _Xresources theme…"),
            WindowActions.export_terminal.get_id()  # pylint:disable=no-member
        ))
        if EXPORT_PLUGINS:
            for plugin_name, plugin in EXPORT_PLUGINS.items():
                export_menu.append_item(Gio.MenuItem.new(
                    plugin.export_text or plugin.display_name,
                    "win.export_plugin_{}".format(plugin_name)
                ))
        export_button = ImageMenuButton(
            icon_name="pan-down-symbolic",
            tooltip_text=_("Export Themes")
        )
        export_button.set_use_popover(True)
        export_button.set_menu_model(export_menu)
        self.add_action(Gio.PropertyAction(
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
        self.headerbar.pack_end(linked_export_box)

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

        self.paned_box = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paned_box.set_wide_handle(True)
        self.box.pack_start(self.paned_box, expand=True, fill=True, padding=0)

    def _init_actions(self):
        self.add_simple_action(
            WindowActions.import_themix_colors, self._on_import_themix_colors
        )
        for plugin_name in IMPORT_PLUGINS:
            self.add_simple_action(
                "import_plugin_{}".format(plugin_name), self._on_import_plugin
            )
        self.add_simple_action(WindowActions.clone, self._on_clone)
        self.save_action = self.add_simple_action(WindowActions.save, self._on_save)
        self.rename_action = self.add_simple_action(WindowActions.rename, self._on_rename)
        self.remove_action = self.add_simple_action(WindowActions.remove, self._on_remove)
        self.add_simple_action(WindowActions.export_theme, self._on_export_theme)
        self.add_simple_action(WindowActions.export_icons, self._on_export_icontheme)
        self.add_simple_action(WindowActions.export_terminal, self._on_export_terminal)
        self.add_simple_action(WindowActions.show_help, self._on_show_help)
        for plugin_name in EXPORT_PLUGINS:
            self.add_simple_action(
                "export_plugin_{}".format(plugin_name), self._on_export_plugin
            )

    def _init_plugins(self):
        for plugin in IMPORT_PLUGINS.values():
            plugin.set_app(self)

    def __init__(self, application):
        super().__init__(
            application=application,
            title=_("Oo-mox GUI"),
            startup_id=application.get_application_id(),
        )
        self.application = application
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

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="com.github.themix_project.Oomox",
            flags=(
                Gio.ApplicationFlags.HANDLES_COMMAND_LINE |
                Gio.ApplicationFlags.NON_UNIQUE
            ),
            **kwargs
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

        def set_accels_for_action(action, accels):
            self.set_accels_for_action(action.get_id(), accels)

        set_accels_for_action(AppActions.quit, ["<Primary>Q"])

        set_accels_for_action(WindowActions.import_menu, ["<Primary>M"])
        set_accels_for_action(WindowActions.clone, ["<Shift><Primary>S"])
        set_accels_for_action(WindowActions.save, ["<Primary>S"])
        set_accels_for_action(WindowActions.rename, ["F2"])
        set_accels_for_action(WindowActions.remove, ["<Primary>Delete"])
        set_accels_for_action(WindowActions.export_theme, ["<Primary>E"])
        set_accels_for_action(WindowActions.export_icons, ["<Primary>I"])
        set_accels_for_action(WindowActions.export_menu, ["<Primary>O"])
        set_accels_for_action(WindowActions.export_terminal, ["<Primary>X"])
        set_accels_for_action(WindowActions.menu, ["F10"])
        set_accels_for_action(WindowActions.show_help, ["<Primary>question"])

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
