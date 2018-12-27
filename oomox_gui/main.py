#!/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import signal
import shutil

from gi.repository import Gtk, Gio

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
from .theme_file_parse import read_colorscheme_from_path
from .presets_list import ThemePresetsList
from .colors_list import ThemeColorsList
from .preview import ThemePreview
from .export_common import export_terminal_theme
from .terminal import generate_terminal_colors_for_oomox
from .plugin_loader import (
    THEME_PLUGINS, ICONS_PLUGINS, IMPORT_PLUGINS, EXPORT_PLUGINS,
)
from .plugin_api import PLUGIN_PATH_PREFIX


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
    menu = "menu"
    remove = "remove"
    rename = "rename"
    save = "save"
    show_help = "show_help"


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
    spinner = None

    _currently_focused_widget = None

    def save_theme(self, name=None):
        if not name:
            name = self.colorscheme_name
        if not self.presets_list.preset_is_saveable():
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

    def import_theme_from_path(self, path, new_name):
        old_path = self.colorscheme_path
        new_path = import_colorscheme(new_name, path)
        self.colorscheme_name = new_name
        self.colorscheme_path = new_path
        if old_path != new_path:
            self.reload_presets()
        self.on_preset_selected(new_name, new_path)

    def import_themix_colors(self):
        self.check_unsaved_changes()

        filechooser_dialog = Gtk.FileChooserDialog(
            _("Please choose a file with oomox colors"),
            self,
            Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK
            )
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
            if not self.check_colorscheme_exists(new_theme_name):
                self.import_theme_from_path(
                    path=import_theme_path,
                    new_name=new_theme_name
                )
                return

    def import_from_plugin(self, plugin):
        self.check_unsaved_changes()
        filechooser_dialog = Gtk.FileChooserDialog(
            _("Please choose an image file"),
            self,
            Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK
            )
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
        new_theme_name = self.colorscheme_name + '_'
        if new_theme_name.startswith(PLUGIN_PATH_PREFIX):
            new_theme_name = '/'.join(new_theme_name.split('/')[1:])
        dialog = NewDialog(transient_for=self, entry_text=new_theme_name)
        if not dialog_is_yes(dialog):
            return
        new_theme_name = dialog.entry_text
        if not self.check_colorscheme_exists(new_theme_name):
            self.save_theme(new_theme_name)
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
            else:
                self.theme_edited = False

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
        self.load_colorscheme(colorscheme)
        if not self.theme_edited:
            self.headerbar.props.title = "*" + self.colorscheme_name
            self.save_action.set_enabled(True)
        self.theme_edited = True

    def reload_presets(self):
        self.presets_list.load_presets()
        self.presets_list.focus_preset_by_filepath(self.colorscheme_path)

    def disable(self):
        self._currently_focused_widget = self.get_focus()
        self.presets_list.set_sensitive(False)
        self.theme_edit.set_sensitive(False)
        Gtk.main_iteration_do(False)
        self.spinner.start()

    def enable(self):
        self.presets_list.set_sensitive(True)
        self.theme_edit.set_sensitive(True)
        self.set_focus(self._currently_focused_widget)
        self.spinner.stop()

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

    def _on_show_help(self, _action, _param=None):
        self.show_help()

    ###########################################################################
    # Init widgets:
    ###########################################################################

    def _init_headerbar(self):  # pylint: disable=too-many-locals
        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.props.title = _("Oo-mox GUI")

        # @TODO:
        # new_button = ImageButton("text-x-generic-symbolic", _("Create New Theme"))  # noqa
        # self.headerbar.pack_start(new_button)

        import_menu = Gio.Menu()
        import_menu.append_item(Gio.MenuItem.new(
            _("Oomox Colors File"),
            "win.import_themix_colors"
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
            name=WindowActions.get_name(WindowActions.import_menu),
            object=import_button,
            property_name="active"
        ))
        self.headerbar.pack_start(import_button)

        clone_button = ImageButton(
            "edit-copy-symbolic", _("Clone Current Theme…")
        )
        self.attach_action(clone_button, WindowActions.clone)
        self.headerbar.pack_start(clone_button)

        save_button = ImageButton(
            "document-save-symbolic", _("Save Theme")
        )
        self.attach_action(save_button, WindowActions.save)
        self.headerbar.pack_start(save_button)

        rename_button = ImageButton(
            # "preferences-desktop-font-symbolic", "Rename theme"
            "pda-symbolic", _("Rename Theme…")
        )
        self.attach_action(rename_button, WindowActions.rename)
        self.headerbar.pack_start(rename_button)

        remove_button = ImageButton(
            "edit-delete-symbolic", _("Remove Theme…")
        )
        self.attach_action(remove_button, WindowActions.remove)
        self.headerbar.pack_start(remove_button)

        #

        menu = Gio.Menu()
        if EXPORT_PLUGINS:
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

        show_help_menuitem = Gio.MenuItem.new(
            _("Keyboard Shortcuts"),
            "win.show_help"
        )
        menu.append_item(show_help_menuitem)

        #

        export_terminal_button = Gtk.Button(
            label=_("Export _Terminal"),
            # label=_("Export _Terminal…"),
            use_underline=True,
            tooltip_text=_("Export Terminal Theme")
        )
        self.attach_action(export_terminal_button, WindowActions.export_terminal)
        self.headerbar.pack_end(export_terminal_button)

        export_icons_button = Gtk.Button(label=_("Export _Icons"),
                                         use_underline=True,
                                         tooltip_text=_("Export Icon Theme"))
        self.attach_action(export_icons_button, WindowActions.export_icons)
        self.headerbar.pack_end(export_icons_button)

        # export_button = Gtk.Button(label=_("_Export Theme…"),
        export_button = Gtk.Button(label=_("_Export Theme"),
                                   use_underline=True,
                                   tooltip_text=_("Export GTK Theme"))
        self.attach_action(export_button, WindowActions.export_theme)
        self.headerbar.pack_end(export_button)

        self.spinner = Gtk.Spinner()
        self.headerbar.pack_end(self.spinner)

        self.set_titlebar(self.headerbar)

    def _init_window(self):
        self.set_wmclass("oomox", "Oomox")
        self.set_role("Oomox-GUI")
        self.connect("delete-event", self._on_quit)
        self.set_default_size(width=600, height=400)
        self.set_hide_titlebar_when_maximized(False)

        self._init_headerbar()

        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(self.box)

        self.paned_box = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        self.paned_box.set_wide_handle(True)
        self.box.pack_start(self.paned_box, expand=True, fill=True, padding=0)

    def _init_actions(self):
        self.add_simple_action(WindowActions.import_themix_colors, self._on_import_themix_colors)
        for plugin_name in IMPORT_PLUGINS:
            self.add_simple_action_by_name(
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
            self.add_simple_action_by_name(
                "export_plugin_{}".format(plugin_name), self._on_export_plugin
            )

    def __init__(self, application):
        super().__init__(
            application=application,
            title=_("Oo-mox GUI"),
            startup_id=application.get_application_id(),
        )
        self.colorscheme = {}
        mkdir_p(USER_COLORS_DIR)

        self._init_actions()
        self._init_window()

        self.presets_list = ThemePresetsList(
            preset_select_callback=self.on_preset_selected
        )
        self.paned_box.pack1(self.presets_list, resize=False, shrink=False)

        self.theme_edit = ThemeColorsList(
            color_edited_callback=self.on_color_edited,
            theme_reload_callback=self.theme_reload,
            transient_for=self
        )
        self.paned_box.pack2(self.theme_edit, resize=True, shrink=False)

        self.preview = ThemePreview()
        self.box.pack_start(self.preview, expand=False, fill=False, padding=0)

        self.show_all()
        self.theme_edit.hide_all_rows()
        self.preview.hide()

        # @TODO: read saved position from the config
        # self.paned_box.set_position(600)


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

        set_accels_for_action(WindowActions.import_menu, ["<Primary>M"])
        set_accels_for_action(WindowActions.clone, ["<Primary>D"])
        set_accels_for_action(WindowActions.save, ["<Primary>S"])
        set_accels_for_action(WindowActions.rename, ["F2"])
        set_accels_for_action(WindowActions.remove, ["<Primary>Delete"])
        set_accels_for_action(WindowActions.export_theme, ["<Primary>E"])
        set_accels_for_action(WindowActions.export_icons, ["<Primary>I"])
        set_accels_for_action(WindowActions.export_terminal, ["<Primary>T"])
        set_accels_for_action(WindowActions.menu, ["F10"])
        set_accels_for_action(WindowActions.show_help, ["<Primary>question"])

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
