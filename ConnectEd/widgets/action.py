"""Private classes for the widgets."""

from typing import Self, Any

from PyQt6.QtCore import QObject
from PyQt6.QtGui  import QAction, QKeySequence


class Action(QAction):
    def __init__(
        self      : Self,
        parent    : QObject,
        text      : str,
        tooltip   : str | None = None,
        shortcut  : QKeySequence | str | None = None,
        checkable : bool = False,
        checked   : bool = False,
        data      : Any = None
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
