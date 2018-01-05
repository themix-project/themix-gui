from gi.repository import Gtk

from .common import FileBasedExportDialog
from .export_config import ExportConfig


OPTION_GTK2_HIDPI = 'gtk2_hidpi'


class GtkThemeExportConfig(ExportConfig):
    name = 'gtk_theme'


class GtkThemeExportDialog(FileBasedExportDialog):

    def on_hidpi_checkbox_toggled(self, widget):
        self.export_config[OPTION_GTK2_HIDPI] = widget.get_active()

    def __init__(self, transient_for, colorscheme, theme_name, **kwargs):
        super().__init__(
            transient_for=transient_for, colorscheme=colorscheme, theme_name=theme_name,
            **kwargs
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

    def do_export(self):
        self.export_config.save()
        super().do_export()
