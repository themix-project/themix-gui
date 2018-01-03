import os
import tempfile

from gi.repository import Gtk

from ..theme_file import save_colorscheme
from ..terminal import generate_terminal_colors_for_oomox

from .common import ExportDialog
from .export_config import ExportConfig


OPTION_GTK2_HIDPI = 'gtk2_hidpi'


class GtkThemeExportConfig(ExportConfig):
    name = 'gtk_theme'


class GtkThemeExportDialog(ExportDialog):

    temp_theme_path = None

    def on_hidpi_checkbox_toggled(self, widget):
        self.export_config[OPTION_GTK2_HIDPI] = widget.get_active()

    def __init__(self, window, colorscheme, theme_name):
        ExportDialog.__init__(self, window)
        self.theme_name = 'oomox-' + theme_name.split('/')[-1]
        colorscheme_copy = generate_terminal_colors_for_oomox(colorscheme)
        self.temp_theme_path = save_colorscheme(
            preset_name=theme_name,
            colorscheme=colorscheme_copy,
            path=tempfile.mkstemp()[1]
        )

        self.export_config = GtkThemeExportConfig({
            OPTION_GTK2_HIDPI: False,
        })

        self.label.set_text(_("Please choose theme export options:"))

        self.hidpi_checkbox = \
            Gtk.CheckButton.new_with_mnemonic(
                _("Generate 2x scaled (_HiDPI) assets for GTK+2")
            )
        self.hidpi_checkbox.connect(
            "toggled", self.on_hidpi_checkbox_toggled
        )
        self.hidpi_checkbox.set_active(
            self.export_config[OPTION_GTK2_HIDPI]
        )
        self.options_box.add(self.hidpi_checkbox)

        self.box.add(self.options_box)
        self.options_box.show_all()
        self.box.add(self.apply_button)
        self.apply_button.show()

    def do_export(self, export_args):
        self.export_config.save()
        super().do_export(export_args)

    def __del__(self):
        os.remove(self.temp_theme_path)
