#!/bin/env python3
import sys
from enum import auto

import gi
gi.require_version('Gtk', '3.0')  # noqa  # pylint: disable=wrong-import-position
from gi.repository import Gtk, GObject, Gio

from .config import user_theme_dir
from .helpers import (
    mkdir_p, ActionsEnum
)
from .gtk_helpers import (
    ImageButton, ImageMenuButton,
    EntryDialog, YesNoDialog
)
from .theme_file import (
    get_user_theme_path, is_user_colorscheme, is_colorscheme_exists,
    save_colorscheme, remove_colorscheme,
)
from .theme_file_load import (
    read_colorscheme_from_path,
)
from .presets_list import ThemePresetsList
from .colors_list import ThemeColorsList
from .preview import ThemePreview
from .export import (
    export_gnome_colors_icon_theme, export_archdroid_icon_theme,
    export_spotify, export_terminal_theme
)
from .terminal import generate_terminal_colors_for_oomox
from .plugin_loader import theme_plugins


class NewDialog(EntryDialog):

    def __init__(
            self, parent,
            title=_("New theme"),
            text=_("Please input new theme name:"),
            entry_text=None
    ):
        EntryDialog.__init__(
            self, parent=parent,
            title=title, text=text, entry_text=entry_text
        )


class RenameDialog(NewDialog):

    def __init__(self, parent, entry_text):
        NewDialog.__init__(
            self, parent=parent,
            title=_("Rename theme"),
            entry_text=entry_text
        )


class UnsavedDialog(YesNoDialog):

    def __init__(self, parent):
        YesNoDialog.__init__(self, parent,
                             _("Unsaved changes"),
                             _("There are unsaved changes.\nSave them?"))


class RemoveDialog(YesNoDialog):

    def __init__(self, parent):
        YesNoDialog.__init__(
            self, parent, _("Remove theme"),
            _("Are you sure you want to delete the colorscheme?\n"
              "This can not be undone.")
        )


def dialog_is_yes(dialog):
    return dialog.run() == Gtk.ResponseType.YES


class AppActions(ActionsEnum):
    _target = 'app'
    quit = auto()


class WindowActions(ActionsEnum):
    _target = 'win'
    clone = auto()
    export_icons = auto()
    export_spotify = auto()
    export_theme = auto()
    export_terminal = auto()
    menu = auto()
    remove = auto()
    rename = auto()
    save = auto()


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

    def add_simple_action(self, action_enum, callback):
        action = Gio.SimpleAction.new(action_enum.name, None)
        action.connect("activate", callback)
        self.add_action(action)
        return action


class OomoxApplicationWindow(WindowWithActions):  # pylint: disable=too-many-instance-attributes

    colorscheme_name = None
    colorscheme_path = None
    colorscheme = None
    colorscheme_is_user = None
    theme_edited = False
    #
    plugin_theme = None
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
        if new_path != self.colorscheme_path:
            self.reload_presets(new_path)
        self.colorscheme_path = new_path
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
        dialog = NewDialog(self)
        if dialog.run() != Gtk.ResponseType.OK:
            return
        new_theme_name = dialog.entry_text
        if not self.check_colorscheme_exists(new_theme_name):
            new_path = self.save_theme(new_theme_name)
            self.reload_presets(new_path)
        else:
            self.clone_theme()

    def check_unsaved_changes(self):
        if self.theme_edited:
            if dialog_is_yes(UnsavedDialog(self)):
                self.save_theme()

    def check_colorscheme_exists(self, colorscheme_name):
        if not is_colorscheme_exists(get_user_theme_path(colorscheme_name)):
            return False
        dialog = Gtk.MessageDialog(
            self, 0, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK,
            _("Colorscheme with such name already exists")
        )
        dialog.run()
        dialog.destroy()
        return True

    def select_theme_plugin(self, theme_plugin_name):
        self.plugin_theme = None
        for theme_plugin in theme_plugins.values():
            if theme_plugin.name == theme_plugin_name:
                self.plugin_theme = theme_plugin

    def load_colorscheme(self, colorscheme):
        self.colorscheme = colorscheme
        self.select_theme_plugin(self.colorscheme['THEME_STYLE'])
        self.preview.update_preview(self.colorscheme, self.plugin_theme)

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

    def on_color_edited(self, colorscheme):
        colorscheme.update(generate_terminal_colors_for_oomox(colorscheme))
        if colorscheme['TERMINAL_THEME_MODE'] != 'manual':
            for i in range(16):
                theme_key = "TERMINAL_COLOR{}".format(i)
                if colorscheme.get(theme_key):
                    del colorscheme[theme_key]

        self.load_colorscheme(colorscheme)
        if not self.theme_edited:
            self.headerbar.props.title = "*" + self.colorscheme_name
            self.save_action.set_enabled(True)
        self.theme_edited = True

    def reload_presets(self, focus_on_path=None):
        if not focus_on_path:
            focus_on_path = self.colorscheme_path
        self.presets_list.load_presets()
        if focus_on_path:
            self.presets_list.focus_preset_by_filepath(focus_on_path)

    ###########################################################################
    # Signal handlers:
    ###########################################################################

    def on_clone(self, _action, _param=None):
        return self.clone_theme()

    def on_rename(self, _action, _param=None):
        dialog = RenameDialog(self, entry_text=self.colorscheme_name)
        if dialog.run() != Gtk.ResponseType.OK:
            return
        new_theme_name = dialog.entry_text
        if not self.check_colorscheme_exists(new_theme_name):
            self.remove_theme()
            new_path = self.save_theme(new_theme_name)
            self.reload_presets(new_path)

    def on_remove(self, _action, _param=None):
        if not dialog_is_yes(RemoveDialog(self)):
            return
        self.remove_theme()
        self.reload_presets()

    def on_save(self, _action, _param=None):
        self.save_theme()

    def on_export(self, _action, _param=None):
        export_dialog = self.plugin_theme.export_dialog
        export_dialog(
            parent=self,
            theme_name=self.colorscheme_name,
            colorscheme=self.colorscheme
        )

    def on_export_icontheme(self, _action, _param=None):
        export_dialog = export_gnome_colors_icon_theme
        if self.colorscheme['ICONS_STYLE'] == 'archdroid':
            export_dialog = export_archdroid_icon_theme
        export_dialog(
            parent=self,
            theme_name=self.colorscheme_name,
            colorscheme=self.colorscheme
        )

    def on_export_terminal(self, _action, _param=None):
        export_terminal_theme(parent=self, colorscheme=self.colorscheme)

    def on_export_spotify(self, _action, _param=None):
        export_spotify(
            parent=self,
            theme_name=self.colorscheme_name,
            colorscheme=self.colorscheme
        )

    def on_quit(self, _arg1, _arg2):
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

        menu = Gio.Menu()
        # menu.append_item(Gio.MenuItem.new(
        #     _("_Export icon theme"),
        #     WindowActions.get_id(WindowActions.export_icons)
        # ))
        menu.append_item(Gio.MenuItem.new(
            _("Apply Spotif_y theme"),
            WindowActions.get_id(WindowActions.export_spotify)
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
        self.connect("delete-event", self.on_quit)
        self.set_default_size(500, 300)
        self.set_border_width(6)

        self._init_headerbar()

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.add(self.box)

    def _init_actions(self):
        self.add_simple_action(WindowActions.clone, self.on_clone)
        self.save_action = self.add_simple_action(WindowActions.save, self.on_save)
        self.rename_action = self.add_simple_action(WindowActions.rename, self.on_rename)
        self.remove_action = self.add_simple_action(WindowActions.remove, self.on_remove)
        self.add_simple_action(WindowActions.export_theme, self.on_export)
        self.add_simple_action(WindowActions.export_icons, self.on_export_icontheme)
        self.add_simple_action(WindowActions.export_terminal, self.on_export_terminal)
        self.add_simple_action(WindowActions.export_spotify, self.on_export_spotify)

    def __init__(self, application=None, title=_("Oo-mox GUI")):
        Gtk.ApplicationWindow.__init__(  # pylint: disable=non-parent-init-called
            self, application=application, title=title
        )
        self.colorscheme = {}
        mkdir_p(user_theme_dir)

        self._init_actions()
        self._init_window()

        self.presets_list = ThemePresetsList(
            preset_select_callback=self.on_preset_selected
        )
        self.box.pack_start(self.presets_list, False, False, 0)

        self.theme_edit = ThemeColorsList(
            color_edited_callback=self.on_color_edited,
            parent=self
        )
        self.box.pack_start(self.theme_edit, True, True, 0)

        self.preview = ThemePreview()
        self.box.pack_start(self.preview, False, False, 0)

        self.show_all()


class OomoxGtkApplication(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.gtk.oomox",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)
        self.window = None
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
        quit_action.connect("activate", self.on_quit)
        self.add_action(quit_action)

        set_accels_for_action(AppActions.quit, ["<Primary>Q"])
        set_accels_for_action(WindowActions.clone, ["<Primary>D"])
        set_accels_for_action(WindowActions.save, ["<Primary>S"])
        set_accels_for_action(WindowActions.rename, ["F2"])
        set_accels_for_action(WindowActions.remove, ["<Primary>Delete"])
        set_accels_for_action(WindowActions.export_theme, ["<Primary>E"])
        set_accels_for_action(WindowActions.export_icons, ["<Primary>I"])
        set_accels_for_action(WindowActions.export_spotify, [])
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

    def on_quit(self, _action, _param=None):
        if self.window:
            self.window.close()
        else:
            self.quit()


def main():
    GObject.threads_init()
    app = OomoxGtkApplication()
    app.run(sys.argv)


if __name__ == "__main__":
    main()
