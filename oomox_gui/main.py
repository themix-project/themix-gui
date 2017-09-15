#!/bin/env python3
import sys
import gi
gi.require_version('Gtk', '3.0')  # noqa
from gi.repository import Gtk, GObject, Gio

from .config import user_theme_dir
from .helpers import (
    is_user_colorscheme, is_colorscheme_exists,
    get_user_theme_path, mkdir_p,
    read_colorscheme_from_path, save_colorscheme, remove_colorscheme,
    ImageButton, ImageMenuButton, CenterLabel
)
from .presets_list import ThemePresetsList
from .colors_list import ThemeColorsList
from .preview import ThemePreview
from .export import (
    export_theme, export_gnome_colors_icon_theme, export_archdroid_icon_theme,
    export_spotify, export_flatplat_theme
)


class NewDialog(Gtk.Dialog):

    entry = None
    input_data = ''

    def do_response(self, response):
        if response == Gtk.ResponseType.OK:
            self.input_data = self.entry.get_text()
        self.destroy()

    def __init__(self, parent,
                 title=_("New theme"),
                 text=_("Please input new theme name:")):
        Gtk.Dialog.__init__(self, title, parent, 0)

        self.set_default_size(150, 100)

        label = Gtk.Label(text)
        self.entry = Gtk.Entry()
        self.entry.set_activates_default(True)

        box = self.get_content_area()
        box.add(label)
        box.add(self.entry)

        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.add_button(_("_OK"), Gtk.ResponseType.OK)

        self.set_default_response(Gtk.ResponseType.OK)

        self.show_all()


class RenameDialog(NewDialog):

    def __init__(self, parent):
        NewDialog.__init__(self, parent, title=_("Rename theme"))


class YesNoDialog(Gtk.Dialog):

    def do_response(self, response):
        self.destroy()

    def __init__(self, parent,
                 title="",
                 text=_("Are you sure?"),
                 default_response=Gtk.ResponseType.NO):
        Gtk.Dialog.__init__(self, title, parent, 0)
        self.set_default_size(150, 100)

        label = CenterLabel(text)
        box = self.get_content_area()
        box.add(label)

        self.add_button(_("_No"), Gtk.ResponseType.NO)
        self.add_button(_("_Yes"), Gtk.ResponseType.YES)

        self.set_default_response(default_response)

        self.show_all()


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


class ActionsEnumValue(str):
    def __new__(cls, target, name):
        obj = str.__new__(cls, '.'.join([target, name]))
        obj.target = target
        obj.name = name
        return obj


class ActionsEnum(type):
    def __init__(self, *args):
        super().__init__(*args)
        self.__target__ = object.__getattribute__(self, '__name__')

    def __getattribute__(self, attribute):
        target = object.__getattribute__(self, '__target__')
        name = object.__getattribute__(self, attribute)
        return ActionsEnumValue(target=target, name=name)


class app(metaclass=ActionsEnum):
    quit = "quit"


class win(metaclass=ActionsEnum):
    clone = "clone"
    export_icons = "export-icons"
    export_spotify = "export-spotify"
    export_theme = "export-theme"
    export_terminal = "export-terminal"
    menu = "menu"
    remove = "remove"
    rename = "rename"
    save = "save"


class AppWindow(Gtk.ApplicationWindow):

    colorscheme_name = None
    colorscheme_path = None
    colorscheme = None
    colorscheme_is_user = None
    theme_edited = False
    # widget sections:
    headerbar = None
    theme_edit = None
    presets_list = None
    preview = None

    def save(self, name=None):
        if not name:
            name = self.colorscheme_name
        if not is_user_colorscheme(self.colorscheme_path):
            if self.check_colorscheme_exists(name):
                return self.clone()
        new_path = save_colorscheme(name, self.colorscheme)
        self.theme_edited = False
        if new_path != self.colorscheme_path:
            self.reload_presets(new_path)
        self.colorscheme_path = new_path
        self.save_action.set_enabled(False)
        self.headerbar.props.title = self.colorscheme_name

    def remove(self, name=None):
        if not name:
            name = self.colorscheme_name
        try:
            remove_colorscheme(name)
        except FileNotFoundError:
            pass

    def check_unsaved_changes(self):
        if self.theme_edited:
            if dialog_is_yes(UnsavedDialog(self)):
                self.save()

    def check_colorscheme_exists(self, colorscheme_name):
        if not is_colorscheme_exists(get_user_theme_path(colorscheme_name)):
            return False
        else:
            dialog = Gtk.MessageDialog(
                self, 0, Gtk.MessageType.WARNING,
                Gtk.ButtonsType.OK,
                _("Colorscheme with such name already exists")
            )
            dialog.run()
            dialog.destroy()
            return True

    def clone(self):
        dialog = NewDialog(self)
        if dialog.run() != Gtk.ResponseType.OK:
            return
        new_theme_name = dialog.input_data
        if not self.check_colorscheme_exists(new_theme_name):
            new_path = self.save(new_theme_name)
            self.reload_presets(new_path)
        else:
            return self.on_clone()

    def on_clone(self, action=None, param=None):
        return self.clone()

    def on_rename(self, action, param=None):
        dialog = RenameDialog(self)
        if dialog.run() != Gtk.ResponseType.OK:
            return
        new_theme_name = dialog.input_data
        if not self.check_colorscheme_exists(new_theme_name):
            self.remove()
            new_path = self.save(new_theme_name)
            self.reload_presets(new_path)

    def on_remove(self, action, param=None):
        if not dialog_is_yes(RemoveDialog(self)):
            return
        self.remove()
        self.reload_presets()

    def on_save(self, action, param=None):
        self.save()

    def on_export(self, action, param=None):
        # @TODO: refactor random theme itself
        if not self.colorscheme_is_user and self.colorscheme_name == 'random':
            self.theme_edited = True
        self.check_unsaved_changes()
        if self.colorscheme["THEME_STYLE"] == "flatplat":
            export_flatplat_theme(
                window=self, theme_path=self.colorscheme_path
            )
        else:
            export_theme(
                window=self, theme_path=self.colorscheme_path
            )

    def on_export_icontheme(self, action, arg=None):
        self.check_unsaved_changes()
        if self.colorscheme['ICONS_STYLE'] == 'archdroid':
            export_archdroid_icon_theme(
                window=self, theme_path=self.colorscheme_path
            )
        else:
            export_gnome_colors_icon_theme(
                window=self, theme_path=self.colorscheme_path
            )

    def on_export_terminal(self, action, arg=None):
        from .export import export_terminal_theme
        export_terminal_theme(window=self, colorscheme=self.colorscheme)

    def on_export_spotify(self, action, arg):
        self.check_unsaved_changes()
        export_spotify(window=self, theme_path=self.colorscheme_path)

    def on_preset_selected(self, selected_preset, selected_preset_path):
        self.check_unsaved_changes()
        self.colorscheme_name = selected_preset
        self.colorscheme_path = selected_preset_path
        self.colorscheme = read_colorscheme_from_path(selected_preset_path)
        self.colorscheme_is_user = is_user_colorscheme(self.colorscheme_path)
        self.theme_edit.open_theme(self.colorscheme)
        self.preview.update_preview(self.colorscheme)
        self.theme_edited = False
        self.save_action.set_enabled(False)
        self.rename_action.set_enabled(self.colorscheme_is_user)
        self.remove_action.set_enabled(self.colorscheme_is_user)
        self.headerbar.props.title = selected_preset

    def on_color_edited(self, colorscheme):
        self.colorscheme = colorscheme
        self.preview.update_preview(self.colorscheme)
        if not self.theme_edited:
            self.headerbar.props.title = "*" + self.headerbar.props.title
            self.save_action.set_enabled(True)
        self.theme_edited = True

    def on_quit(self, arg1, arg2):
        self.check_unsaved_changes()

    def action_tooltip(self, action, tooltip):
        accels = self.get_application().get_accels_for_action(action)
        if accels:
            key, mods = Gtk.accelerator_parse(accels[0])
            tooltip += ' ({})'.format(Gtk.accelerator_get_label(key, mods))
        return tooltip

    def attach_action(self, widget, action, with_tooltip=True):
        widget.set_action_name(action)
        if with_tooltip:
            tooltip = self.action_tooltip(action, widget.get_tooltip_text())
            widget.set_tooltip_text(tooltip)

    def _init_headerbar(self):
        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.props.title = _("Oo-mox GUI")

        # @TODO:
        # new_button = ImageButton("text-x-generic-symbolic", _("Create new theme"))  # noqa
        # self.headerbar.pack_start(new_button)

        clone_button = ImageButton("edit-copy-symbolic",
                                   _("Clone current theme"))
        self.attach_action(clone_button, win.clone)
        self.headerbar.pack_start(clone_button)

        save_button = ImageButton("document-save-symbolic", _("Save theme"))
        self.attach_action(save_button, win.save)
        self.headerbar.pack_start(save_button)

        rename_button = ImageButton(
            # "preferences-desktop-font-symbolic", "Rename theme"
            "pda-symbolic", _("Rename theme")
        )
        self.attach_action(rename_button, win.rename)
        self.headerbar.pack_start(rename_button)

        remove_button = ImageButton(
            "edit-delete-symbolic", _("Remove theme")
        )
        self.attach_action(remove_button, win.remove)
        self.headerbar.pack_start(remove_button)

        #

        menu = Gio.Menu()
        """
        menu.append_item(Gio.MenuItem.new(_("_Export icon theme"),
                                          win.export_icons))
        """
        menu.append_item(Gio.MenuItem.new(_("Apply Spotif_y theme"),
                                          win.export_spotify))

        menu_button = ImageMenuButton("open-menu-symbolic")
        menu_button.set_use_popover(True)
        menu_button.set_menu_model(menu)
        self.add_action(Gio.PropertyAction(name=win.menu.name,
                                           object=menu_button,
                                           property_name="active"))
        self.headerbar.pack_end(menu_button)

        export_terminal_button = Gtk.Button(
            label=_("Export _terminal"),
            use_underline=True,
            tooltip_text=_("Export terminal theme")
        )
        self.attach_action(export_terminal_button, win.export_terminal)
        self.headerbar.pack_end(export_terminal_button)

        export_icons_button = Gtk.Button(label=_("Export _icons"),
                                         use_underline=True,
                                         tooltip_text=_("Export icon theme"))
        self.attach_action(export_icons_button, win.export_icons)
        self.headerbar.pack_end(export_icons_button)

        export_button = Gtk.Button(label=_("_Export theme"),
                                   use_underline=True,
                                   tooltip_text=_("Export GTK theme"))
        self.attach_action(export_button, win.export_theme)
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
        def add_simple_action(action_id, callback):
            action = Gio.SimpleAction.new(action_id.name, None)
            action.connect("activate", callback)
            self.add_action(action)
            return action

        add_simple_action(win.clone, self.on_clone)
        self.save_action = add_simple_action(win.save, self.on_save)
        self.rename_action = add_simple_action(win.rename, self.on_rename)
        self.remove_action = add_simple_action(win.remove, self.on_remove)
        add_simple_action(win.export_theme, self.on_export)
        add_simple_action(win.export_icons, self.on_export_icontheme)
        add_simple_action(win.export_terminal, self.on_export_terminal)
        add_simple_action(win.export_spotify, self.on_export_spotify)

    def reload_presets(self, focus_on_path=None):
        if not focus_on_path:
            focus_on_path = self.colorscheme_path
        self.presets_list.load_presets()
        if focus_on_path:
            self.presets_list.focus_preset_by_filepath(focus_on_path)

    def __init__(self, application=None, title=_("Oo-mox GUI")):
        Gtk.ApplicationWindow.__init__(
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


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.example.myapp",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)
        self.window = None
        # @TODO: use oomox-gui as the only one entrypoint to all cli tools
        # self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE,
        # GLib.OptionArg.NONE, "Command line test", None)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        quit_action = Gio.SimpleAction.new(app.quit.name, None)
        quit_action.connect("activate", self.on_quit)
        self.add_action(quit_action)

        self.set_accels_for_action(app.quit, ["<Primary>Q"])

        self.set_accels_for_action(win.clone, ["<Primary>D"])
        self.set_accels_for_action(win.save, ["<Primary>S"])
        self.set_accels_for_action(win.rename, ["F2"])
        self.set_accels_for_action(win.remove, ["<Primary>Delete"])
        self.set_accels_for_action(win.export_theme, ["<Primary>E"])
        self.set_accels_for_action(win.export_icons, ["<Primary>I"])
        self.set_accels_for_action(win.export_spotify, [])
        self.set_accels_for_action(win.menu, ["F10"])

    def do_activate(self):
        if not self.window:
            self.window = AppWindow(application=self)
        self.window.present()

    def do_command_line(self, command_line):
        # options = command_line.get_options_dict()
        # if options.contains("test"):
            # print("Test argument recieved")
        self.activate()
        return 0

    def on_quit(self, action, param=None):
        if self.window:
            self.window.close()
        else:
            self.quit()


def main():
    GObject.threads_init()
    app = Application()
    app.run(sys.argv)


if __name__ == "__main__":
    main()
