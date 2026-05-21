"""Main-window shell widgets (docks, etc.)."""

from typing import Self

from PyQt6.QtWidgets import QDockWidget


class ShellMixin:
    def dock(self : Self, title : str) -> QDockWidget | None:
        for dock in self._window.findChildren(QDockWidget):
            if dock.windowTitle() == title:
                return dock
        return None

    def expectDock(self : Self, title : str, visible : bool = True) -> QDockWidget:
        dock = self.dock(title)
        assert dock is not None, f"dock {title!r} not found"
        self.expectVisible(dock, visible)
        return dock
