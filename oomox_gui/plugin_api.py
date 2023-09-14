import os
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, ClassVar

from .config import FALLBACK_COLOR, USER_COLORS_DIR

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from typing import Final

    from typing_extensions import TypedDict

    from .export_common import ExportDialog
    from .preview import ThemePreview
    from .preview_icons import IconThemePreview
    from .theme_file import ThemeT
    from .theme_model import ThemeModelValue

    class AboutLink(TypedDict):
        name: str
        url: str


PLUGIN_PATH_PREFIX: "Final" = "__plugin__"


class OomoxPlugin(metaclass=ABCMeta):

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        pass

    about_text: str | None = None
    about_links: ClassVar["list[AboutLink] | None"] = None


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
    def export_dialog(self) -> "type[ExportDialog]":
        pass

    enabled_keys_gtk: ClassVar[list[str]] = []
    enabled_keys_options: ClassVar[list[str]] = []
    enabled_keys_extra: ClassVar[list[str]] = []

    theme_model_gtk: ClassVar["list[ThemeModelValue]"] = []
    theme_model_options: ClassVar["list[ThemeModelValue]"] = []
    theme_model_extra: ClassVar["list[ThemeModelValue]"] = []

    def preview_before_load_callback(
            self, preview_object: "ThemePreview", colorscheme: "ThemeT",
    ) -> None:
        pass

    class PreviewImageboxesNames(Enum):
        CHECKBOX = "checkbox-checked"

    preview_sizes: ClassVar[dict[str, int]] = {
        PreviewImageboxesNames.CHECKBOX.name: 16,
    }

    def preview_transform_function(
            self,  # noqa: PLR6301
            svg_template: str,
            colorscheme: "ThemeT",
    ) -> str:
        for key in (
                "SEL_BG", "SEL_FG", "ACCENT_BG", "TXT_BG", "BG", "FG",
        ):
            svg_template = svg_template.replace(
                f"%{key}%", str(colorscheme.get(key) or FALLBACK_COLOR),
            )
        return svg_template


class OomoxIconsPlugin(OomoxPlugin):

    enabled_keys_icons: ClassVar[list[str]] = []
    theme_model_icons: ClassVar["list[ThemeModelValue]"] = []

    @property
    @abstractmethod
    def preview_svg_dir(self) -> str:
        pass

    @property
    @abstractmethod
    def export_dialog(self) -> "type[ExportDialog]":
        pass

    @abstractmethod
    def preview_transform_function(self, svg_template: str, colorscheme: "ThemeT") -> str:
        pass

    def preview_before_load_callback(
            self, preview_object: "IconThemePreview", colorscheme: "ThemeT",
    ) -> None:
        pass


class OomoxExportPlugin(OomoxPlugin):

    @property
    @abstractmethod
    def export_dialog(self) -> "type[ExportDialog]":
        pass

    # Text to display in export menu:
    export_text: str | None = None

    theme_model_extra: ClassVar["list[ThemeModelValue]"] = []

    shortcut: str | None = None


class OomoxImportPlugin(OomoxPlugin):

    is_async = False

    @abstractmethod
    def read_colorscheme_from_path(self, preset_path: str) -> "ThemeT":
        pass

    # Text to display in import menu:
    import_text: str | None = None

    # Text to name section of user presets imported with the plugin:
    user_presets_display_name: str | None = None

    # supported file extensions for filechooser dialog
    file_extensions: ClassVar["Iterable[str]"] = []

    plugin_theme_dir: str | None = None

    theme_model_import: ClassVar["list[ThemeModelValue]"] = []

    @property
    def user_theme_dir(self) -> str:
        return os.path.abspath(
            os.path.join(USER_COLORS_DIR, PLUGIN_PATH_PREFIX + self.name),
        )

    shortcut: str | None = None


class OomoxImportPluginAsync(OomoxImportPlugin):

    is_async = True

    @abstractmethod
    def read_colorscheme_from_path(  # type: ignore[override] #  pylint: disable=arguments-differ
            self, preset_path: str, callback: "Callable[[ThemeT,], None]",
    ) -> None:
        pass
