from abc import ABCMeta, abstractproperty


class OomoxPlugin(object, metaclass=ABCMeta):

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def display_name(self):
        pass


class OomoxImportPlugin(OomoxPlugin):
    pass


class OomoxThemePlugin(OomoxPlugin):

    @abstractproperty
    def description(self):
        pass

    @abstractproperty
    def export_dialog(self):
        pass

    theme_model_gtk = []
    theme_model_options = []
    theme_model_other = []

    def preview_before_load_callback(self, preview_object, colorscheme):
        pass


class OomoxIconsPlugin(OomoxPlugin):
    pass


class OomoxExportPlugin(OomoxPlugin):
    pass
