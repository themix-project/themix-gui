import os
from abc import ABCMeta, abstractproperty, abstractmethod
from enum import Enum

from oomox_gui.config import FALLBACK_COLOR, USER_COLORS_DIR


from typing import TYPE_CHECKING  # pylint: disable=wrong-import-order
if TYPE_CHECKING:
    # pylint: disable=ungrouped-imports
    from typing import List, Dict, Any, Iterable, Optional, Union  # noqa

    from oomox_gui.export_common import ExportDialog  # noqa
    from oomox_gui.preview import ThemePreview  # noqa
    from oomox_gui.preview_icons import IconThemePreview  # noqa

    from oomox_gui.theme_model import ThemeModelValue  # noqa
    ColorScheme = Dict[str, Union[str, bool, int, float]]


PLUGIN_PATH_PREFIX = "__plugin__"


class OomoxPlugin(metaclass=ABCMeta):

    @abstractproperty
    def name(self) -> str:
        pass

    @abstractproperty
    def display_name(self) -> str:
        pass


class OomoxThemePlugin(OomoxPlugin):

    @abstractproperty
    def description(self) -> str:
        pass

    @abstractproperty
    def gtk_preview_dir(self) -> str:
        pass

    @abstractproperty
    def export_dialog(self) -> 'ExportDialog':
        pass

    enabled_keys_gtk = []  # type: List[str]
    enabled_keys_options = []  # type: List[str]
    enabled_keys_extra = []  # type: List[str]

    theme_model_gtk = []  # type: List[ThemeModelValue]
    theme_model_options = []  # type: List[ThemeModelValue]
    theme_model_extra = []  # type: List[ThemeModelValue]

    def preview_before_load_callback(
            self, preview_object: 'ThemePreview', colorscheme: 'ColorScheme'
    ) -> None:
        pass

    class PreviewImageboxesNames(Enum):
        CHECKBOX = 'checkbox-checked'

    preview_sizes = {
        PreviewImageboxesNames.CHECKBOX.name: 16,
    }

    def preview_transform_function(self, svg_template: str, colorscheme: 'ColorScheme') -> str:
        # pylint: disable=no-self-use
        for key in (
                "SEL_BG", "ACCENT_BG", "TXT_BG", "BG", "FG",
        ):
            svg_template = svg_template.replace(
                "%{}%".format(key), str(colorscheme.get(key) or FALLBACK_COLOR)
            )
        return svg_template


class OomoxIconsPlugin(OomoxPlugin):

    enabled_keys_icons = []  # type: List[str]
    theme_model_icons = []  # type: List[ThemeModelValue]

    @abstractproperty
    def preview_svg_dir(self) -> str:
        pass

    @abstractproperty
    def export_dialog(self) -> 'ExportDialog':
        pass

    @abstractmethod
    def preview_transform_function(self, svg_template: str, colorscheme: 'ColorScheme') -> str:
        pass

    def preview_before_load_callback(
            self, preview_object: 'IconThemePreview', colorscheme: 'ColorScheme'
    ) -> None:
        pass


class OomoxExportPlugin(OomoxPlugin):

    @abstractproperty
    def export_dialog(self) -> 'ExportDialog':
        pass

    # Text to display in export menu:
    export_text = None  # type: Optional[str]

    theme_model_extra = []  # type: List[ThemeModelValue]


class OomoxImportPlugin(OomoxPlugin):

    @abstractmethod
    def read_colorscheme_from_path(self, preset_path: str) -> 'ColorScheme':
        pass

    # Text to display in import menu:
    import_text = None  # type: Optional[str]

    # supported file extensions for filechooser dialog
    file_extensions = []  # type: Iterable[str]

    plugin_theme_dir = None  # type: Optional[str]

    theme_model_import = []  # type: List[ThemeModelValue]

    @property
    def user_theme_dir(self) -> str:
        return os.path.abspath(
            os.path.join(USER_COLORS_DIR, PLUGIN_PATH_PREFIX + self.name)
        )
