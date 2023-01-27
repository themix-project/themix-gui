import re
from typing import TYPE_CHECKING

from oomox_gui.export_common import ExportDialog
from oomox_gui.helpers import natural_sort
from oomox_gui.i18n import translate
from oomox_gui.plugin_api import OomoxExportPlugin
from oomox_gui.terminal import generate_xrdb_theme_from_oomox

if TYPE_CHECKING:
    from typing import Any

    from oomox_gui.color import HexColor


def generate_xresources(terminal_colorscheme: "dict[str, HexColor]") -> str:
    color_keys = terminal_colorscheme.keys()
    color_regex = re.compile("color[0-9]")
    return "\n".join([
        f"*{key}:  #{terminal_colorscheme[key]}"
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

    def __init__(self, *args: "Any", **kwargs: "Any") -> None:
        super().__init__(
            *args,
            headline=translate("Terminal Colorscheme"),
            height=440,
            **kwargs,
        )
        self.label.set_text(translate("Paste this colorscheme to your ~/.Xresources:"))
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
    name = "xresources"
    display_name = translate("Xresources")
    export_text = translate("Export _Xresources theme…")
    shortcut = "<Primary>X"
    export_dialog = XresourcesExportDialog
