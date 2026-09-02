from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from .theme_file import ThemeValueT

MAX_HISTORY_DEPTH: Final[int] = 50


class ColorHistoryStack:

    def __init__(self, max_depth: int = MAX_HISTORY_DEPTH) -> None:
        self.max_depth: int = max_depth
        self._undo_stack: list[str] = []
        self._redo_stack: list[str] = []

    def push(self, new_value: str, current_value: str | None = None) -> None:
        """Push a new value onto the undo stack and clear redo stack."""
        if current_value and (not self._undo_stack or self._undo_stack[-1] != current_value):
            self._undo_stack.append(current_value)
        elif self._undo_stack and self._undo_stack[-1] == new_value:
            return

        self._redo_stack.clear()
        if len(self._undo_stack) >= self.max_depth:
            self._undo_stack.pop(0)

    def record_change(self, old_value: str, new_value: str) -> None:
        """Record an explicit state transition from old_value to new_value."""
        if old_value == new_value:
            return
        if not self._undo_stack or self._undo_stack[-1] != old_value:
            self._undo_stack.append(old_value)
        self._redo_stack.clear()
        if len(self._undo_stack) > self.max_depth:
            self._undo_stack.pop(0)

    def undo(self, current_value: str) -> str | None:
        """Pop and return the previous color value from undo stack."""
        if not self._undo_stack:
            return None
        previous_value = self._undo_stack.pop()
        self._redo_stack.append(current_value)
        return previous_value

    def redo(self, current_value: str) -> str | None:
        """Pop and return the next color value from redo stack."""
        if not self._redo_stack:
            return None
        next_value = self._redo_stack.pop()
        self._undo_stack.append(current_value)
        return next_value

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()


@dataclass
class GlobalHistoryItem:
    key: str
    old_value: "ThemeValueT"
    new_value: "ThemeValueT"


class GlobalThemeHistory:

    def __init__(self, max_depth: int = MAX_HISTORY_DEPTH) -> None:
        self.max_depth: int = max_depth
        self._undo_stack: list[GlobalHistoryItem] = []
        self._redo_stack: list[GlobalHistoryItem] = []
        self.enabled: bool = True

    def push(self, key: str, old_value: "ThemeValueT", new_value: "ThemeValueT") -> None:
        if not self.enabled or old_value == new_value:
            return
        self._undo_stack.append(GlobalHistoryItem(key=key, old_value=old_value, new_value=new_value))
        self._redo_stack.clear()
        if len(self._undo_stack) > self.max_depth:
            self._undo_stack.pop(0)

    def undo(self) -> GlobalHistoryItem | None:
        if not self._undo_stack:
            return None
        item = self._undo_stack.pop()
        self._redo_stack.append(item)
        return item

    def redo(self) -> GlobalHistoryItem | None:
        if not self._redo_stack:
            return None
        item = self._redo_stack.pop()
        self._undo_stack.append(item)
        return item

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def clear(self) -> None:
        self._undo_stack.clear()
        self._redo_stack.clear()
