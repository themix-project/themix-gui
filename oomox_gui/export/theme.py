import os

from gi.repository import Gtk

from ..config import (
    gtk_theme_dir, materia_theme_dir,
)

from .common import ExportDialog
from .export_config import ExportConfig


class GtkThemeExportConfig(ExportConfig):
    name = 'gtk_theme'


class GtkThemeExportDialog(ExportDialog):

    theme_path = None

    def on_hidpi_checkbox_toggled(self, widget):
        self.export_config['gtk2_hidpi'] = widget.get_active()

    def __init__(self, window, theme_path):
        ExportDialog.__init__(self, window)
        self.theme_path = theme_path

        self.export_config = GtkThemeExportConfig({
            "gtk2_hidpi": False,
        })

        self.spinner.stop()
        self.label.set_text(_("Please choose theme export options:"))

        self.hidpi_checkbox = \
            Gtk.CheckButton.new_with_mnemonic(
                _("Generate 2x scaled (_HiDPI) assets for GTK+2")
            )
        self.hidpi_checkbox.connect(
            "toggled", self.on_hidpi_checkbox_toggled
        )
        self.hidpi_checkbox.set_active(self.export_config['gtk2_hidpi'])
        self.options_box.add(self.hidpi_checkbox)

        self.options_box.show()
        self.apply_button.show()

        self.show_all()
        self.scrolled_window.hide()

    def do_export(self, export_args):
        self.export_config.save()
        super().do_export(export_args)


class OomoxThemeExportDialog(GtkThemeExportDialog):
    timeout = 100

    def do_export(self):
        if Gtk.get_minor_version() >= 20:
            make_opts = "gtk320"
        else:
            make_opts = "gtk3"
        export_args = [
            "bash",
            os.path.join(gtk_theme_dir, "change_color.sh"),
            "--make-opts", make_opts,
            "--hidpi", str(self.export_config['gtk2_hidpi']),
            self.theme_path,
        ]
        super().do_export(export_args)


class MateriaThemeExportDialog(GtkThemeExportDialog):
    timeout = 1000

    def do_export(self):
        export_args = [
            "bash",
            os.path.join(materia_theme_dir, "change_color.sh"),
            self.theme_path,
        ]
        super().do_export(export_args)


def export_theme(window, theme_path, colorscheme):
    if colorscheme["THEME_STYLE"] == "materia":
        MateriaThemeExportDialog(
            window=window, theme_path=theme_path
        )
    else:
        OomoxThemeExportDialog(
            window=window, theme_path=theme_path
        )
