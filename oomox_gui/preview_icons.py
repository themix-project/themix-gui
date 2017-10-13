import os

from gi.repository import Gtk, Gio, GLib, GdkPixbuf

from .config import script_dir


WIDGET_SPACING = 10


class IconThemePreview(Gtk.ListBox):

    icon_user_home = None
    icon_user_desktop = None
    icon_system_file_manager = None

    def __init__(self):
        super().__init__()
        self.set_margin_left(WIDGET_SPACING)
        self.set_margin_right(WIDGET_SPACING)

        # self.bg = Gtk.Grid(row_spacing=6, column_spacing=6)
        # self.bg.set_margin_top(WIDGET_SPACING/2)
        # self.bg.set_margin_bottom(WIDGET_SPACING)

        self.set_selection_mode(Gtk.SelectionMode.NONE)
        row = Gtk.ListBoxRow()
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.add(hbox)
        for attr_name in (
            "icon_user_home",
            "icon_user_desktop",
            "icon_system_file_manager"
        ):
            setattr(self, attr_name, Gtk.Image())
            hbox.pack_start(getattr(self, attr_name), True, True, 0)
        self.add(row)
        self.show_all()

    def update_preview(self, colorscheme):
        self.load_icon_templates(colorscheme['ICONS_STYLE'])
        for source_image, target_imagebox in (
            (self.icon_source_user_home, self.icon_user_home),
            (self.icon_source_user_desktop, self.icon_user_desktop),
            (self.icon_source_system_file_manager,
             self.icon_system_file_manager),
        ):
            new_svg_image = source_image.replace(
                "LightFolderBase", colorscheme["ICONS_LIGHT_FOLDER"]
            ).replace(
                "LightBase", colorscheme["ICONS_LIGHT"]
            ).replace(
                "MediumBase", colorscheme["ICONS_MEDIUM"]
            ).replace(
                "DarkStroke", colorscheme["ICONS_DARK"]
            ).replace(
                "%ICONS_ARCHDROID%", colorscheme["ICONS_ARCHDROID"]
            ).encode('ascii')
            stream = Gio.MemoryInputStream.new_from_bytes(
                GLib.Bytes.new(new_svg_image)
            )

            # @TODO: is it possible to make it faster?
            pixbuf = GdkPixbuf.Pixbuf.new_from_stream(stream, None)

            target_imagebox.set_from_pixbuf(pixbuf)

    def load_icon_templates(self, prefix):
        for template_path, attr_name in (
            ("user-home.svg.template", "icon_source_user_home"),
            ("user-desktop.svg.template", "icon_source_user_desktop"),
            ("system-file-manager.svg.template",
             "icon_source_system_file_manager"),
        ):
            with open(
                os.path.join(
                    script_dir, 'icon_previews', prefix, template_path
                ), "rb"
            ) as f:
                setattr(self, attr_name, f.read().decode('utf-8'))
