""" This file is licensed under GPLv3, see https://www.gnu.org/licenses/ """

# pylint: disable=invalid-name,protected-access,pointless-statement

from vulture.whitelist_utils import Whitelist  # pylint: disable=import-error,no-name-in-module


whitelist = Whitelist()

# typehints
whitelist.typing.List
whitelist.typing.Iterable
whitelist.typing.Optional
whitelist.theme_model.ThemeModelValue
whitelist.plugin_api.ColorScheme

# stdlib
whitelist.Thread.daemon

# gtk
whitelist.props.gtk_color_palette
whitelist.props.custom_title
whitelist.Gtk.Application.do_activate
whitelist.Gtk.Application.do_command_line
whitelist.Gtk.Dialog.do_response

# plugin api
whitelist.OomoxPlugin.enabled_keys_gtk
whitelist.OomoxPlugin.enabled_keys_options
whitelist.OomoxPlugin.enabled_keys_icons
whitelist.OomoxPlugin.enabled_keys_extra
whitelist.OomoxPlugin.theme_model_gtk
whitelist.OomoxPlugin.theme_model_options
whitelist.OomoxPlugin.theme_model_icons
whitelist.OomoxPlugin.theme_model_extra
whitelist.ExportDialog.show_text


# to fix ?
whitelist.preview_icons.IconsNames.HOME
whitelist.preview_icons.IconsNames.DESKTOP
whitelist.preview_icons.IconsNames.FILE_MANAGER
whitelist.terminal.ProgressBar.message
whitelist.OomoxPlugin.haishoku
whitelist.OomoxPlugin.colorthief

# to be used later
whitelist.i18n._n

# to be used later ??
whitelist.ColorDiff.sat
