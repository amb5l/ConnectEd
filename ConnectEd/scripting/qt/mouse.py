"""QTest mouse delivery for GUI scripting."""

from typing import Self

from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QGraphicsView, QWidget

from .core import CoreMixin


class MouseMixin:
    def mousePress(
        self       : Self,
        widget     : QWidget,
        pos        : QPoint,
        button     : Qt.MouseButton = Qt.MouseButton.LeftButton,
        modifiers  : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier,
    ) -> None:
        if not isinstance(self, CoreMixin):
            raise TypeError("Bad host")
        target = self._mouseWidget(widget)
        QTest.mousePress(target, button, modifiers, pos)  # pyright: ignore[reportCallIssue, reportArgumentType]
        self.processEvents()

    def mouseMove(
        self       : Self,
        widget     : QWidget,
        pos        : QPoint,
        button     : Qt.MouseButton = Qt.MouseButton.LeftButton,
        modifiers  : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier,
    ) -> None:
        if not isinstance(self, CoreMixin):
            raise TypeError("Bad host")
        target = self._mouseWidget(widget)
        QTest.mouseMove(target, pos)  # pyright: ignore[reportCallIssue, reportArgumentType]
        self.processEvents()

    def mouseRelease(
        self       : Self,
        widget     : QWidget,
        pos        : QPoint,
        button     : Qt.MouseButton = Qt.MouseButton.LeftButton,
        modifiers  : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier,
    ) -> None:
        if not isinstance(self, CoreMixin):
            raise TypeError("Bad host")
        target = self._mouseWidget(widget)
        QTest.mouseRelease(target, button, modifiers, pos)  # pyright: ignore[reportCallIssue, reportArgumentType]
        self.processEvents()

    def mouseClick(
        self       : Self,
        widget     : QWidget,
        pos        : QPoint,
        button     : Qt.MouseButton = Qt.MouseButton.LeftButton,
        modifiers  : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier,
    ) -> None:
        if not isinstance(self, CoreMixin):
            raise TypeError("Bad host")
        target = self._mouseWidget(widget)
        QTest.mouseClick(target, button, modifiers, pos)  # pyright: ignore[reportCallIssue, reportArgumentType]
        self.processEvents()

    def mouseDrag(
        self       : Self,
        widget     : QWidget,
        pos1       : QPoint,
        pos2       : QPoint | None = None,
        button     : Qt.MouseButton = Qt.MouseButton.LeftButton,
        modifiers  : Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier,
    ) -> None:
        self.mousePress(widget, pos1, button, modifiers)
        if pos2 is None:
            return
        self.mouseMove(widget, pos2, button, modifiers)
        self.mouseRelease(widget, pos2, button, modifiers)

    def viewPos(self : Self, view : QGraphicsView, scene : QPointF) -> QPoint:
        return view.mapFromScene(scene)

    def scenePos(self : Self, view : QGraphicsView, view_pt : QPoint) -> QPointF:
        return view.mapToScene(view_pt)

    def _mouseWidget(self : Self, widget : QWidget) -> QWidget | None:
        if isinstance(widget, QGraphicsView):
            return widget.viewport()
        return widget
