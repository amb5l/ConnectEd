"""Event loop, window root, widget discovery, and input."""

from typing import Any, Self

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget


class CoreMixin:
    _window : QMainWindow

    def __init__(self : Self, window : QMainWindow) -> None:
        self._window = window

    def window(self : Self) -> QMainWindow:
        return self._window

    def processEvents(self : Self) -> None:
        QApplication.processEvents()

    def schedule(self : Self, callback : Any) -> None:
        QTimer.singleShot(0, callback)

    def click(self : Self, widget : QWidget) -> None:
        QTest.mouseClick(widget, Qt.MouseButton.LeftButton)

    def expectVisible(self : Self, widget : QWidget | None, visible : bool = True) -> None:
        assert widget is not None
        assert widget.isHidden() != visible

    def expectWindowTitle(self : Self, widget : QWidget, title : str) -> None:
        assert widget.windowTitle() == title

    def findChild(
        self   : Self,
        parent : QWidget,
        type   : type[QWidget],
        name   : str | None = None,
    ) -> QWidget | None:
        options = Qt.FindChildOption.FindChildrenRecursively
        return parent.findChild(type, name, options)  # type: ignore[arg-type]

    def findChildren(self : Self, parent : QWidget, type : type[QWidget]) -> list[QWidget]:
        options = Qt.FindChildOption.FindChildrenRecursively
        return parent.findChildren(type, options=options)  # type: ignore[arg-type]
