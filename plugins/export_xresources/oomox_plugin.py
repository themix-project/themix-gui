# -*- coding: utf-8 -*-
import re

from oomox_gui.i18n import _
from oomox_gui.export_common import ExportDialog
from oomox_gui.helpers import natural_sort
from oomox_gui.plugin_api import OomoxExportPlugin
from oomox_gui.terminal import generate_xrdb_theme_from_oomox


def generate_xresources(terminal_colorscheme):
    color_keys = terminal_colorscheme.keys()
    color_regex = re.compile('color[0-9]')
    return '\n'.join([
        "*{key}:  #{value}".format(
            key=key, value=terminal_colorscheme[key]
        )
        for key in (
            sorted([
                key for key in color_keys
                if not color_regex.match(key)
            ]) +
            natural_sort([
                key for key in color_keys
                if color_regex.match(key)
            ])
        )
    ])


class XresourcesExportDialog(ExportDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            headline=_("Terminal Colorscheme"),
            height=440,
            **kwargs
        )
        self.label.set_text(_('Paste this colorscheme to your ~/.Xresources:'))
        self.scrolled_window.show_all()
        try:
            term_colorscheme = generate_xrdb_theme_from_oomox(self.colorscheme)
            xresources_theme = generate_xresources(term_colorscheme)
        except Exception as exc:
            self.set_text(exc)
            self.show_error()
        else:
            self.set_text(xresources_theme)


class Plugin(OomoxExportPlugin):

    name = 'xresources'

    display_name = _('Xresources')
    shortcut = "<Primary>X"
    export_text = _("Export _Xresources theme…")
    export_dialog = XresourcesExportDialog
