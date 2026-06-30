from __future__ import annotations

from typing import Self, TypeAlias

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui     import QFont

from ...app import settings


class UiFontSizeMixin:
    """Mixin to handle widget UI font size."""

    # class attributes
    _SETTINGS_UI_PATH : str

    # instance attributes
    _default_font_size : int
    _current_font_size : int

    def initFontSize(self : Self) -> None:
        """Initialize the font size."""
        if not isinstance(self, QWidget):
            raise TypeError("Bad host")
        font = self.font()
        self._default_font_size = font.pointSize()
        settings_path = f"ui/{self._SETTINGS_UI_PATH}"
        self.setFontSize(settings().get(f"{settings_path}/font/size"))

    def setFontSize(self : Self, size : int) -> None:
        """Set the font size."""
        if not isinstance(self, QWidget):
            raise TypeError("Bad host")
        font = QFont()
        font.setPointSizeF(size)
        self.setFont(font)
        self._current_font_size = size
        settings_path = f"ui/{self._SETTINGS_UI_PATH}"
        settings().set(f"{settings_path}/font/size", self._current_font_size)

    def resetFontSize(self : Self) -> None:
        """Reset the font size to the default size."""
        self.setFontSize(self._default_font_size)

    def increaseFontSize(self : Self) -> None:
        """Increase the font size."""
        self.setFontSize(min(self._current_font_size + 1, 20)) # TODO: max from settings

    def decreaseFontSize(self : Self) -> None:
        """Decrease the font size."""
        self.setFontSize(max(self._current_font_size - 1, 6)) # TODO: min from settings
