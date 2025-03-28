"""Private classes for the widgets."""

__all__ = [
    'Action'
]

from typing import Optional, Any

from PyQt6.QtCore import QObject
from PyQt6.QtGui  import QAction, QKeySequence


class Action(QAction):
    def __init__(
        self      : 'Action',
        parent    : QObject,
        text      : str,
        tooltip   : Optional[str] = None,
        shortcut  : Optional[QKeySequence | str] = None,
        checkable : bool = False,
        checked   : bool = False,
        data      : Optional[Any] = None
    ) -> None:
        super().__init__(parent)
        self.setText(text)
        if tooltip is not None:
            self.setToolTip(tooltip)
        if shortcut is not None:
            self.setShortcut(shortcut)
        self.setCheckable(checkable)
        if checkable:
            self.setChecked(checked)
        if data is not None:
            self.setData(data)
