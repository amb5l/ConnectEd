"""Main-window shell widgets (docks, etc.)."""

from typing import Self

from PyQt6.QtWidgets import QDockWidget

from .core import CoreMixin


class ShellMixin:
    def dock(self : Self, title : str) -> QDockWidget | None:
        if not isinstance(self, CoreMixin):
            raise TypeError("Bad host")
        for dock in self._window.findChildren(QDockWidget):
            if dock.windowTitle() == title:
                    return dock
        return None
