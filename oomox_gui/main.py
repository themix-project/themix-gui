#!/bin/env python3
import sys
import signal

from gi.repository import Gtk, Gio

from .i18n import _
from .config import USER_COLORS_DIR
from .helpers import mkdir_p
from .gtk_helpers import (
    ImageButton, ImageMenuButton,
    EntryDialog, YesNoDialog,
    ActionsEnum,
)
from .theme_file import (
    get_user_theme_path, is_user_colorscheme, is_colorscheme_exists,
    save_colorscheme, remove_colorscheme,
)
from .theme_file_parse import read_colorscheme_from_path
from .presets_list import ThemePresetsList
from .colors_list import ThemeColorsList
from .preview import ThemePreview
from .export_common import export_terminal_theme
from .terminal import generate_terminal_colors_for_oomox
from .plugin_loader import THEME_PLUGINS, ICONS_PLUGINS, EXPORT_PLUGINS


class NewDialog(EntryDialog):

    def __init__(
            self, transient_for,
            title=_("New theme"),
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
            title=_("Rename theme"),
            entry_text=entry_text
        )


class UnsavedDialog(YesNoDialog):

    def __init__(self, transient_for):
        super().__init__(
            transient_for=transient_for,
            title=_("Unsaved changes"),
            text=_("There are unsaved changes.\nSave them?")
        )


class RemoveDialog(YesNoDialog):

    def __init__(self, transient_for):
        super().__init__(
            transient_for=transient_for,
            title=_("Remove theme"),
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
    clone = "clone"
    export_icons = "icons"
    export_theme = "theme"
    export_terminal = "terminal"
    menu = "menu"
    remove = "remove"
    rename = "rename"
    save = "save"


class WindowWithActions(Gtk.ApplicationWindow):

    def action_tooltip(self, action_enum, tooltip):
        action_id = action_enum.get_id()
        accels = self.get_application().get_accels_for_action(action_id)
        if accels:
            key, mods = Gtk.accelerator_parse(accels[0])
            tooltip += ' ({})'.format(Gtk.accelerator_get_label(key, mods))
        return tooltip

    def attach_action(self, widget, action_enum, with_tooltip=True):
        action_id = action_enum.get_id()
        widget.set_action_name(action_id)
        if with_tooltip:
            tooltip = self.action_tooltip(action_enum, widget.get_tooltip_text())
            widget.set_tooltip_text(tooltip)

    def add_simple_action_by_name(self, action_name, callback):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect("activate", callback)
        self.add_action(action)
        return action

    def add_simple_action(self, action_enum, callback):
        return self.add_simple_action_by_name(action_enum.name, callback)


class OomoxApplicationWindow(WindowWithActions):  # pylint: disable=too-many-instance-attributes

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
    presets_list = None
    preview = None

    def save_theme(self, name=None):
        if not name:
            name = self.colorscheme_name
        if not is_user_colorscheme(self.colorscheme_path):
            if self.check_colorscheme_exists(name):
                self.clone_theme()
                return
        new_path = save_colorscheme(name, self.colorscheme)
        self.theme_edited = False
        old_path = self.colorscheme_path
        self.colorscheme_name = name
        self.colorscheme_path = new_path
        if old_path != new_path:
            self.reload_presets()
        self.save_action.set_enabled(False)
        self.headerbar.props.title = self.colorscheme_name

    def remove_theme(self, name=None):
        if not name:
            name = self.colorscheme_name
        try:
            remove_colorscheme(name)
        except FileNotFoundError:
            pass

    def clone_theme(self):
        dialog = NewDialog(transient_for=self)
        if not dialog_is_yes(dialog):
            return
        new_theme_name = dialog.entry_text
        if not self.check_colorscheme_exists(new_theme_name):
            self.save_theme(new_theme_name)
            self.reload_presets()
        else:
            self.clone_theme()

    def rename_theme(self):
        dialog = RenameDialog(transient_for=self, entry_text=self.colorscheme_name)
        if not dialog_is_yes(dialog):
            return
        new_theme_name = dialog.entry_text
        if not self.check_colorscheme_exists(new_theme_name):
            old_theme_name = self.colorscheme_name
            self.save_theme(new_theme_name)
            self.remove_theme(old_theme_name)
            self.reload_presets()

    def check_unsaved_changes(self):
        if self.theme_edited:
            if dialog_is_yes(UnsavedDialog(transient_for=self)):
                self.save_theme()

    def check_colorscheme_exists(self, colorscheme_name):
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

    def select_theme_plugin(self):
        theme_plugin_name = self.colorscheme['THEME_STYLE']
        self.plugin_theme = None
        for theme_plugin in THEME_PLUGINS.values():
            if theme_plugin.name == theme_plugin_name:
                self.plugin_theme = theme_plugin

    def select_icons_plugin(self):
        icons_plugin_name = self.colorscheme['ICONS_STYLE']
        self.plugin_icons = None
        for icons_plugin in ICONS_PLUGINS.values():
            if icons_plugin.name == icons_plugin_name:
                self.plugin_icons = icons_plugin

    def load_colorscheme(self, colorscheme):
        self.colorscheme = colorscheme
        self.select_theme_plugin()
        self.select_icons_plugin()
        self.generate_terminal_colors()
        try:
            self.preview.update_preview(
                colorscheme=self.colorscheme,
                theme_plugin=self.plugin_theme,
                icons_plugin=self.plugin_icons,
            )
        except Exception as exc:
            import traceback
            print()
            print("ERROR: Can't show theme preview:")
            print(exc)
            traceback.print_exc()
            print()

    def on_preset_selected(self, selected_preset, selected_preset_path):
        self.check_unsaved_changes()
        self.colorscheme_name = selected_preset
        self.colorscheme_path = selected_preset_path
        self.load_colorscheme(read_colorscheme_from_path(selected_preset_path))
        self.colorscheme_is_user = is_user_colorscheme(self.colorscheme_path)
        self.theme_edit.open_theme(self.colorscheme)
        self.theme_edited = False
        self.save_action.set_enabled(False)
        self.rename_action.set_enabled(self.colorscheme_is_user)
        self.remove_action.set_enabled(self.colorscheme_is_user)
        self.headerbar.props.title = selected_preset

    def theme_reload(self):
        self.on_preset_selected(
            self.colorscheme_name, self.colorscheme_path
        )
        return self.colorscheme

    def generate_terminal_colors(self):
        self.colorscheme.update(generate_terminal_colors_for_oomox(self.colorscheme))

    def on_color_edited(self, colorscheme):
        self.generate_terminal_colors()
        self.load_colorscheme(colorscheme)
        if not self.theme_edited:
            self.headerbar.props.title = "*" + self.colorscheme_name
            self.save_action.set_enabled(True)
        self.theme_edited = True

    def reload_presets(self):
        self.presets_list.load_presets()
        self.presets_list.focus_preset_by_filepath(self.colorscheme_path)

    ###########################################################################
    # Signal handlers:
    ###########################################################################

    def _on_clone(self, _action, _param=None):
        return self.clone_theme()

    def _on_rename(self, _action, _param=None):
        self.rename_theme()

    def _on_remove(self, _action, _param=None):
        if not dialog_is_yes(RemoveDialog(transient_for=self)):
            return
        self.remove_theme()
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

    def _on_quit(self, _arg1, _arg2):
        self.check_unsaved_changes()

    ###########################################################################
    # Init widgets:
    ###########################################################################

    def _init_headerbar(self):
        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.props.title = _("Oo-mox GUI")

        # @TODO:
        # new_button = ImageButton("text-x-generic-symbolic", _("Create new theme"))  # noqa
        # self.headerbar.pack_start(new_button)

        clone_button = ImageButton(
            "edit-copy-symbolic", _("Clone current theme")
        )
        self.attach_action(clone_button, WindowActions.clone)
        self.headerbar.pack_start(clone_button)

        save_button = ImageButton(
            "document-save-symbolic", _("Save theme")
        )
        self.attach_action(save_button, WindowActions.save)
        self.headerbar.pack_start(save_button)

        rename_button = ImageButton(
            # "preferences-desktop-font-symbolic", "Rename theme"
            "pda-symbolic", _("Rename theme")
        )
        self.attach_action(rename_button, WindowActions.rename)
        self.headerbar.pack_start(rename_button)

        remove_button = ImageButton(
            "edit-delete-symbolic", _("Remove theme")
        )
        self.attach_action(remove_button, WindowActions.remove)
        self.headerbar.pack_start(remove_button)

        #

        if EXPORT_PLUGINS:
            menu = Gio.Menu()
            for plugin_name, plugin in EXPORT_PLUGINS.items():
                menu.append_item(Gio.MenuItem.new(
                    plugin.display_name,
                    "win.export_plugin_{}".format(plugin_name)
                ))

            menu_button = ImageMenuButton("open-menu-symbolic")
            menu_button.set_use_popover(True)
            menu_button.set_menu_model(menu)
            self.add_action(Gio.PropertyAction(
                name=WindowActions.get_name(WindowActions.menu),
                object=menu_button,
                property_name="active"
            ))
            self.headerbar.pack_end(menu_button)

        export_terminal_button = Gtk.Button(
            label=_("Export _terminal"),
            use_underline=True,
            tooltip_text=_("Export terminal theme")
        )
        self.attach_action(export_terminal_button, WindowActions.export_terminal)
        self.headerbar.pack_end(export_terminal_button)

        export_icons_button = Gtk.Button(label=_("Export _icons"),
                                         use_underline=True,
                                         tooltip_text=_("Export icon theme"))
        self.attach_action(export_icons_button, WindowActions.export_icons)
        self.headerbar.pack_end(export_icons_button)

        export_button = Gtk.Button(label=_("_Export theme"),
                                   use_underline=True,
                                   tooltip_text=_("Export GTK theme"))
        self.attach_action(export_button, WindowActions.export_theme)
        self.headerbar.pack_end(export_button)

        self.set_titlebar(self.headerbar)

    def _init_window(self):
        self.set_wmclass("oomox", "Oomox")
        self.connect("delete-event", self._on_quit)
        self.set_default_size(500, 300)
        self.set_border_width(6)

        self._init_headerbar()

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.box)

    def _init_actions(self):
        self.add_simple_action(WindowActions.clone, self._on_clone)
        self.save_action = self.add_simple_action(WindowActions.save, self._on_save)
        self.rename_action = self.add_simple_action(WindowActions.rename, self._on_rename)
        self.remove_action = self.add_simple_action(WindowActions.remove, self._on_remove)
        self.add_simple_action(WindowActions.export_theme, self._on_export_theme)
        self.add_simple_action(WindowActions.export_icons, self._on_export_icontheme)
        self.add_simple_action(WindowActions.export_terminal, self._on_export_terminal)
        for plugin_name in EXPORT_PLUGINS:
            self.add_simple_action_by_name(
                "export_plugin_{}".format(plugin_name), self._on_export_plugin
            )

    def __init__(self, application, title=_("Oo-mox GUI")):
        super().__init__(
            application=application, title=title
        )
        self.colorscheme = {}
        mkdir_p(USER_COLORS_DIR)

        self._init_actions()
        self._init_window()

        self.presets_list = ThemePresetsList(
            preset_select_callback=self.on_preset_selected
        )
        self.box.pack_start(self.presets_list, False, False, 0)

        self.theme_edit = ThemeColorsList(
            color_edited_callback=self.on_color_edited,
            theme_reload_callback=self.theme_reload,
            transient_for=self
        )
        self.box.pack_start(self.theme_edit, True, True, 0)

        self.preview = ThemePreview()
        self.box.pack_start(self.preview, False, False, 0)

        self.show_all()


class OomoxGtkApplication(Gtk.Application):

    window = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="com.github.themix_project.Oomox",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)
        # @TODO: use oomox-gui as the only one entrypoint to all cli tools
        # self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE,
        # GLib.OptionArg.NONE, "Command line test", None)

    def do_startup(self):  # pylint: disable=arguments-differ

        def set_accels_for_action(action, accels):
            self.set_accels_for_action(action.get_id(), accels)

        Gtk.Application.do_startup(self)

        quit_action = Gio.SimpleAction.new(
            AppActions.get_name(AppActions.quit), None
        )
        quit_action.connect("activate", self._on_quit)
        self.add_action(quit_action)

        set_accels_for_action(AppActions.quit, ["<Primary>Q"])
        set_accels_for_action(WindowActions.clone, ["<Primary>D"])
        set_accels_for_action(WindowActions.save, ["<Primary>S"])
        set_accels_for_action(WindowActions.rename, ["F2"])
        set_accels_for_action(WindowActions.remove, ["<Primary>Delete"])
        set_accels_for_action(WindowActions.export_theme, ["<Primary>E"])
        set_accels_for_action(WindowActions.export_icons, ["<Primary>I"])
        set_accels_for_action(WindowActions.menu, ["F10"])

    def do_activate(self):  # pylint: disable=arguments-differ
        if not self.window:
            self.window = OomoxApplicationWindow(application=self)
        self.window.present()

    def do_command_line(self, _command_line):  # pylint: disable=arguments-differ
        # options = command_line.get_options_dict()
        # if options.contains("test"):
            # print("Test argument recieved")
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
        app.quit()
        sys.stderr.write("\n\nCanceled by user (SIGINT)\n")
        sys.exit(125)

    signal.signal(signal.SIGINT, handle_sig_int)
    app.run(sys.argv)


if __name__ == "__main__":
    main()
