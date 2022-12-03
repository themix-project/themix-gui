import importlib
import os
import re
import sys
from types import ModuleType
from typing import TypeVar, Iterable


def mkdir_p(path: str) -> None:
    if os.path.isdir(path):
        return
    os.makedirs(path)


def ls_r(path: str) -> list[str]:
    return [
        os.path.join(files[0], file)
        for files in os.walk(path, followlinks=True) for file in files[2]
    ]


def get_plugin_module(name: str, path: str, submodule: str | None = None) -> ModuleType:
    if sys.version_info.minor < 5:
        raise RuntimeError('Python 3.5+ is required')
    #                           i guess mypy stubs for importlib are incomplete:
    spec = importlib.util.spec_from_file_location(name, path)  # type: ignore[attr-defined]
    module = importlib.util.module_from_spec(spec)  # type: ignore[attr-defined]
    spec.loader.exec_module(module)
    if submodule:
        return getattr(module, submodule)  # type: ignore[no-any-return]
    return module  # type: ignore[no-any-return]


SortableT = TypeVar('SortableT', bound=str)


def natural_sort(list_to_sort: list[SortableT]) -> Iterable[SortableT]:
    def convert(text: str) -> str | int:
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key: str) -> tuple[str | int, ...]:
        return tuple(convert(c) for c in re.split('([0-9]+)', key))

    return sorted(list_to_sort, key=alphanum_key)
