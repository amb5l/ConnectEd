from typing import Self

from PyQt6.QtGui     import QIcon
from PyQt6.QtWidgets import QToolButton, QWidget


class ToolButton(QToolButton):
    """QToolButton with visible checked state styling."""

    _STYLE = """
        QToolButton {
            border: 1px solid palette(mid);
            border-radius: 3px;
            padding: 3px;
        }
        QToolButton:checked {
            background-color: palette(highlight);
            border: 1px solid palette(dark);
        }
    """

    def __init__(
        self   : Self,
        icon   : QIcon | None   = None,
        parent : QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self.setStyleSheet(self._STYLE)
        self.setCheckable(True)
        if icon is not None:
            self.setIcon(icon)
