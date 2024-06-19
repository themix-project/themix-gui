import importlib
import os
import re
import sys
import warnings
from types import TracebackType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from types import ModuleType
    from typing import Any, TypeVar

    SortableT = TypeVar("SortableT", bound=str)
    DelayedPartialReturnT = TypeVar("DelayedPartialReturnT")
    DelayedPartialArgT = TypeVar("DelayedPartialArgT")


def mkdir_p(path: str) -> None:
    if os.path.isdir(path):
        return
    os.makedirs(path)


def ls_r(path: str) -> list[str]:
    return [
        os.path.join(files[0], file)
        for files in os.walk(path, followlinks=True) for file in files[2]
    ]


def get_plugin_module(name: str, path: str, submodule: str | None = None) -> "ModuleType":
    #                           i guess mypy stubs for importlib are incomplete:
    spec = importlib.util.spec_from_file_location(name, path)  # type: ignore[attr-defined]
    module = importlib.util.module_from_spec(spec)  # type: ignore[attr-defined]
    spec.loader.exec_module(module)
    if submodule:
        return getattr(module, submodule)  # type: ignore[no-any-return]
    return module  # type: ignore[no-any-return]


def natural_sort(list_to_sort: "list[SortableT]") -> "Iterable[SortableT]":
    def convert(text: str) -> str | int:
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key: str) -> tuple[str | int, ...]:
        return tuple(convert(c) for c in re.split("([0-9]+)", key))

    return sorted(list_to_sort, key=alphanum_key)


def apply_chain(func: "Callable[..., Any]", *args_args: "Iterable[Iterable[Any]]") -> "Any":
    result = func
    for args in args_args:
        result = result(*args)
    return result


def call_method_from_class(
        klass: type, klass_args: "Iterable[Any]", method_name: str, method_args: "Iterable[Any]",
) -> "Any | None":
    return getattr(klass(*klass_args), method_name)(*method_args)


def delayed_partial(
        func: "Callable[..., DelayedPartialReturnT]",
        delayed_args: """Iterable[
            tuple[Callable[[DelayedPartialArgT], Any], Iterable[DelayedPartialArgT]]
        ]""",
        rest_args: "Iterable[Any]",
) -> "DelayedPartialReturnT":
    computed_args = []
    for delayed_func, args in delayed_args:
        computed_args.append(delayed_func(*args))
    all_args = computed_args + list(rest_args)
    return func(*all_args)


def log_error(info: "Any") -> None:
    sys.stderr.write(f"{info!s}\n")


class SuppressWarningsFilter:

    warn_list: list[warnings.WarningMessage]

    def __init__(self, warning_class: type, message: str) -> None:
        self.warning_class = warning_class
        self.warning_message = message
        self.warning_manager = warnings.catch_warnings(record=True)

    def __enter__(self) -> None:
        self.warn_list = self.warning_manager.__enter__()

    def __exit__(
            self,
            exc_class: type[BaseException] | None,
            exc_instance: BaseException | None,
            exc_tb: TracebackType | None,
    ) -> None:
        if exc_instance:
            raise exc_instance
        self.warning_manager.__exit__(exc_class, exc_instance, exc_tb)
        for warn in self.warn_list:
            if (
                (not sys.warnoptions)
                and (warn.category is self.warning_class)
                and (isinstance(warn.message, Warning))
                and (warn.message.args)
                and (
                    warn.message.args[0] == self.warning_message,
                )
            ):
                pass
            else:
                warnings.showwarning(
                    message=warn.message,
                    category=warn.category,
                    filename=warn.filename,
                    lineno=warn.lineno,
                )
