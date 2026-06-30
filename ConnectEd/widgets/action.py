"""Private classes for the widgets."""

from ..core.check import checked

from typing import Self, Any

from PyQt6.QtCore import QObject
from PyQt6.QtGui  import QAction, QKeySequence


ShortcutType = QKeySequence | QKeySequence.StandardKey | str


class Action(QAction):
    @checked
    def __init__(
        self      : Self,
        parent    : QObject,
        text      : str | None = None,
        tooltip   : str | None = None,
        shortcut  : ShortcutType | None = None,
        checkable : bool = False,
        checked   : bool = False,
        data      : Any = None
    ) -> None:
        super().__init__(parent)
        if text is not None:
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
