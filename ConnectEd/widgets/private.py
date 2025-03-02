"""Private classes for the widgets."""

__all__ = [
    'Action'
]

from typing import Optional

from PyQt6.QtCore import QObject
from PyQt6.QtGui  import QAction, QKeySequence


class Action(QAction):
    def __init__(
        self      : 'Action',
        parent    : QObject,
        text      : str,
        tooltip   : str,
        shortcut  : Optional[QKeySequence | str],
        checkable : bool = False,
        checked   : bool = False
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        self.setToolTip(tooltip)
        if shortcut is not None:
            self.setShortcut(shortcut)
        self.setCheckable(checkable)
        if checkable:
            self.setChecked(checked)
