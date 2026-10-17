from gi.repository import Gtk

from .gtk_helpers import CenterLabel
from .i18n import translate
from .multi_export import DEFAULT_PADDING
from .settings import UISettings


class WelcomeDialog(Gtk.Dialog):

    def __init__(self, transient_for: Gtk.Window) -> None:
        super().__init__(
            title=translate("Welcome to Themix"),
            transient_for=transient_for,
            flags=0,
        )
        self.set_default_size(400, 200)

        box = self.get_content_area()
        box.set_spacing(DEFAULT_PADDING)

        intro_label = CenterLabel(
            label=translate("Are you new to Themix? Online documentation is available!"),
        )
        box.add(intro_label)

        links = (
            (translate("How to contribute your theme"),
             ("https://github.com/themix-project/themix-gui/wiki/"
              "How-to-contribute-your-theme-from-Github-website")),
            (translate("How to import and export Base16 themes"),
             ("https://github.com/themix-project/themix-gui/wiki/"
              "How-to-import-and-export-Base16-themes-in-Themix-Oomox")),
        )
        for label_text, url in links:
            link_button = Gtk.LinkButton.new_with_label(url, label_text)
            box.add(link_button)

        self.dont_show_checkbox = Gtk.CheckButton.new_with_label(
            translate("Don't show this dialog at startup."),
        )
        self.dont_show_checkbox.set_active(True)  # type: ignore[attr-defined]
        box.add(self.dont_show_checkbox)

        self.add_button(translate("_OK"), Gtk.ResponseType.OK)

        self.show_all()

    def do_response(self, _response: Gtk.ResponseType) -> None:  # pylint: disable=arguments-differ
        UISettings().show_welcome_dialog = not self.dont_show_checkbox.get_active()  # type: ignore[attr-defined]
        self.destroy()
