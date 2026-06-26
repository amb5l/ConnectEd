"""GuiDriver protocol (full scripting surface)."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Protocol, Self, runtime_checkable

from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QDockWidget, QGraphicsView, QMenu, QMenuBar, QWidget

if TYPE_CHECKING:
    from ...widgets.window import Window
    from ...widgets.window.menu_bar import MenuBar


@runtime_checkable
class GuiDriver(Protocol):
    """ConnectEd-aware GUI scripting surface."""

    # core
    def window(self : Self) -> Window:
        ...

    def processEvents(self : Self) -> None:
        ...

    def schedule(self : Self, callback : Any) -> None:
        ...

    def click(self : Self, widget : QWidget) -> None:
        ...

    def findChild(
        self   : Self,
        parent : QWidget,
        type   : type[QWidget],
        name   : str | None = None,
    ) -> QWidget | None:
        ...

    def findChildren(self : Self, parent : QWidget, type : type[QWidget]) -> list[QWidget]:
        ...

    def expectVisible(self : Self, widget : QWidget | None, visible : bool = True) -> None:
        ...

    def expectWindowTitle(self : Self, widget : QWidget, title : str) -> None:
        ...

    def menuBar(self : Self) -> MenuBar | None:
        ...

    # menus (optional Qt helpers)
    def menuTitle(self : Self, menu : QMenu) -> str:
        ...

    def actionName(self : Self, action : QAction) -> str:
        ...

    def menu(self : Self, menu_bar : QMenuBar, title : str) -> QMenu | None:
        ...

    def action(self : Self, menu : QMenu, name : str) -> QAction | None:
        ...

    # modal
    def activeModal(self : Self) -> QWidget | None:
        ...

    def modalBodyText(self : Self, modal : QWidget) -> str:
        ...

    def withModal(
        self    : Self,
        opener  : Callable[[], None],
        onModal : Callable[[], None],
    ) -> None:
        ...

    # shell
    def dock(self : Self, title : str) -> QDockWidget | None:
        ...

    def expectDock(self : Self, title : str, visible : bool = True) -> QDockWidget:
        ...

    # mouse
    def mousePress(
        self       : Self,
        widget     : QWidget,
        pos        : QPoint,
        button     : Qt.MouseButton = ...,
        modifiers  : Qt.KeyboardModifier = ...,
    ) -> None:
        ...

    def mouseMove(
        self       : Self,
        widget     : QWidget,
        pos        : QPoint,
        button     : Qt.MouseButton = ...,
        modifiers  : Qt.KeyboardModifier = ...,
    ) -> None:
        ...

    def mouseRelease(
        self       : Self,
        widget     : QWidget,
        pos        : QPoint,
        button     : Qt.MouseButton = ...,
        modifiers  : Qt.KeyboardModifier = ...,
    ) -> None:
        ...

    def mouseClick(
        self       : Self,
        widget     : QWidget,
        pos        : QPoint,
        button     : Qt.MouseButton = ...,
        modifiers  : Qt.KeyboardModifier = ...,
    ) -> None:
        ...

    def mouseDrag(
        self       : Self,
        widget     : QWidget,
        pos1       : QPoint,
        pos2       : QPoint | None = ...,
        button     : Qt.MouseButton = ...,
        modifiers  : Qt.KeyboardModifier = ...,
    ) -> None:
        ...

    def viewPos(self : Self, view : QGraphicsView, scene : QPointF) -> QPoint:
        ...

    def scenePos(self : Self, view : QGraphicsView, view_pt : QPoint) -> QPointF:
        ...
