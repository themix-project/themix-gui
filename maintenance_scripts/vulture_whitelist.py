"""Licensed under GPLv3, see https://www.gnu.org/licenses/"""

# pylint: disable=invalid-name,protected-access,pointless-statement

from vulture.whitelist_utils import Whitelist  # pylint: disable=import-error,no-name-in-module

whitelist = Whitelist()

# typehints
whitelist.typing.Any
whitelist.typing.BinaryIO
whitelist.typing.Final
whitelist.typing.IOStream
whitelist.typing.Iterable
whitelist.typing.Iterable
whitelist.typing.Literal
whitelist.typing.Mapping
whitelist.typing.ModuleType
whitelist.typing.MutableMapping
whitelist.typing.NoReturn
whitelist.typing.Optional
whitelist.typing.Pattern
whitelist.typing.Sequence
whitelist.typing.TextIO
whitelist.typing.TracebackType
whitelist.typing.Tuple
whitelist.typing.Type
whitelist.color.HexColor
whitelist.color.IntColor
whitelist.theme_model.ThemeModel
whitelist.theme_model.ThemeModelValue.filter
whitelist.theme_model.ThemeModelValue.reload_theme
whitelist.theme_model.ThemeModelValue.reload_options
whitelist.theme_file.PresetFile.default
whitelist.theme_file.ThemeT

whitelist.helpers.SortableT
whitelist.helpers.DelayedPartialReturnT
whitelist.helpers.DelayedPartialArgT

# stdlib
whitelist.Thread.daemon

# gtk
whitelist.props.gtk_color_palette
whitelist.props.custom_title
whitelist.Gtk.Application.do_activate
whitelist.Gtk.Application.do_command_line
whitelist.Gtk.Dialog.do_response

# plugin api
whitelist.AboutLink
whitelist.AboutLink.name
whitelist.AboutLink.url
whitelist.OomoxPlugin.enabled_keys_gtk
whitelist.OomoxPlugin.enabled_keys_options
whitelist.OomoxPlugin.enabled_keys_icons
whitelist.OomoxPlugin.enabled_keys_extra
whitelist.OomoxPlugin.about_text
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
whitelist.i18n.translate_many

# to be used later ??
whitelist.ColorDiff.sat
