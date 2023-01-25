import os
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Final,
)

from .config import FALLBACK_COLOR, USER_COLORS_DIR

if TYPE_CHECKING:
    from typing import Callable, Iterable, Optional, Type  # noqa: F401

    from typing_extensions import TypedDict

    from .export_common import ExportDialog
    from .preview import ThemePreview
    from .preview_icons import IconThemePreview
    from .theme_file_parser import ColorScheme
    from .theme_model import ThemeModelValue  # noqa: F401
    AboutLink = TypedDict('AboutLink', {'name': str, 'url': str})


PLUGIN_PATH_PREFIX: Final = "__plugin__"


class OomoxPlugin(metaclass=ABCMeta):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        pass

    about_text = None  # type: Optional[str]
    about_links = None  # type: Optional[list[AboutLink]]


class OomoxThemePlugin(OomoxPlugin):

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @property
    @abstractmethod
    def gtk_preview_dir(self) -> str:
        pass

    @property
    @abstractmethod
    def export_dialog(self) -> 'Type[ExportDialog]':
        pass

    enabled_keys_gtk = []  # type: list[str]
    enabled_keys_options = []  # type: list[str]
    enabled_keys_extra = []  # type: list[str]

    theme_model_gtk = []  # type: list[ThemeModelValue]
    theme_model_options = []  # type: list[ThemeModelValue]
    theme_model_extra = []  # type: list[ThemeModelValue]

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
        for key in (
                "SEL_BG", "SEL_FG", "ACCENT_BG", "TXT_BG", "BG", "FG",
        ):
            svg_template = svg_template.replace(
                f"%{key}%", str(colorscheme.get(key) or FALLBACK_COLOR)
            )
        return svg_template


class OomoxIconsPlugin(OomoxPlugin):

    enabled_keys_icons = []  # type: list[str]
    theme_model_icons = []  # type: list[ThemeModelValue]

    @property
    @abstractmethod
    def preview_svg_dir(self) -> str:
        pass

    @property
    @abstractmethod
    def export_dialog(self) -> 'Type[ExportDialog]':
        pass

    @abstractmethod
    def preview_transform_function(self, svg_template: str, colorscheme: 'ColorScheme') -> str:
        pass

    def preview_before_load_callback(
            self, preview_object: 'IconThemePreview', colorscheme: 'ColorScheme'
    ) -> None:
        pass


class OomoxExportPlugin(OomoxPlugin):

    @property
    @abstractmethod
    def export_dialog(self) -> 'Type[ExportDialog]':
        pass

    # Text to display in export menu:
    export_text = None  # type: Optional[str]

    theme_model_extra = []  # type: list[ThemeModelValue]

    shortcut = None  # type: Optional[str]


class OomoxImportPlugin(OomoxPlugin):

    is_async = False

    @abstractmethod
    def read_colorscheme_from_path(self, preset_path: str) -> 'ColorScheme':
        pass

    # Text to display in import menu:
    import_text = None  # type: Optional[str]

    # Text to name section of user presets imported with the plugin:
    user_presets_display_name = None  # type: Optional[str]

    # supported file extensions for filechooser dialog
    file_extensions = []  # type: Iterable[str]

    plugin_theme_dir = None  # type: Optional[str]

    theme_model_import = []  # type: list[ThemeModelValue]

    @property
    def user_theme_dir(self) -> str:
        return os.path.abspath(
            os.path.join(USER_COLORS_DIR, PLUGIN_PATH_PREFIX + self.name)
        )

    shortcut = None  # type: Optional[str]


class OomoxImportPluginAsync(OomoxImportPlugin):

    is_async = True

    @abstractmethod
    def read_colorscheme_from_path(  # type: ignore[override] #  pylint: disable=arguments-differ
            self, preset_path: str, callback: 'Callable[[ColorScheme,], None]'
    ) -> None:
        pass
