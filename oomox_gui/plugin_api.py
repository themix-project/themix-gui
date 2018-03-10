from abc import ABCMeta, abstractproperty, abstractmethod


class OomoxPlugin(object, metaclass=ABCMeta):

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def display_name(self):
        pass


class OomoxThemePlugin(OomoxPlugin):

    @abstractproperty
    def description(self):
        pass

    @abstractproperty
    def export_dialog(self):
        pass

    @abstractproperty
    def gtk_preview_css_dir(self):
        pass

    enabled_keys_gtk = []
    enabled_keys_options = []
    enabled_keys_other = []

    theme_model_gtk = []
    theme_model_options = []
    theme_model_other = []
    theme_model_extra = []

    def preview_before_load_callback(self, preview_object, colorscheme):
        pass


class OomoxIconsPlugin(OomoxPlugin):

    enabled_keys_icons = []
    theme_model_icons = []

    @abstractproperty
    def preview_svg_dir(self):
        pass

    @abstractmethod
    def preview_transform_function(self, svg_template, colorscheme):
        pass


class OomoxImportPlugin(OomoxPlugin):

    @abstractproperty
    def import_dialog(self):
        pass


class OomoxExportPlugin(OomoxPlugin):

    @abstractproperty
    def export_dialog(self):
        pass

    theme_model_extra = []


class OomoxThemeFormatPlugin(OomoxPlugin):

    @abstractproperty
    def file_extension(self):
        pass

    @abstractmethod
    def read_colorscheme_from_path(preset_path):
        pass

    theme_model_gtk = []
