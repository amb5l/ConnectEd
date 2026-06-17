from __future__ import annotations

from typing import Self, TypeAlias

from PyQt6.QtCore    import Qt, QEvent, QPoint
from PyQt6.QtGui     import QEnterEvent, QMouseEvent, QWheelEvent, QCursor

from .....app import logger, settings, window

from .defs import DrawingViewMouseButtonState as MouseButtonState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingView
    MixinSelf: TypeAlias = Self | DrawingView
else:
    MixinSelf = Self


qmb = Qt.MouseButton
qkm = Qt.KeyboardModifier


class DrawingViewMouseMixin:
    def enterEvent(self : MixinSelf, _event : QEnterEvent) -> None:
        v = self.mapFromGlobal(QCursor.pos())
        s = self.mapToScene(v)
        self.mouse.current.setPL(v, s)
        window().statusBar().xy.setText(
            str(int(round(s.x()))) + "," + str(int(round(s.y())))
        )

    def leaveEvent(self : MixinSelf, _ : QEvent) -> None:
        rect = self.viewport().rect()
        v = QPoint(rect.width() // 2, rect.height() // 2)
        s = self.mapToScene(v)
        self.mouse.current.setPL(v, s)
        window().statusBar().xy.setText("-,-")

    def mouseMoveEvent(self : MixinSelf, event : QMouseEvent) -> None:
        v = event.pos()
        s = self.mapToScene(v)
        m = self._getModifiers(event)
        self.mouse.current.setPL(v, s)
        self.mouse.current.modifiers = m
        window().statusBar().xy.setText(
            str(int(round(s.x()))) + "," + str(int(round(s.y())))
        )
        match self.mouse.left.state:
            case MouseButtonState.Pressed:
                d = self._distance(self.mouse.left.press.physical, event.pos())
                if d >= settings().get("prefs/mouse/drag"):
                    self.mouse.left.state = MouseButtonState.Dragging
                    self.state.mouseLeftDragBegin(
                        self.mouse.left.press.physical,
                        self.mouse.left.press.logical,
                        self.mouse.left.press.modifiers
                    )
                    return
            case MouseButtonState.Dragging:
                self.state.mouseLeftDragCont(
                    self.mouse.current.physical,
                    self.mouse.current.logical,
                    self.mouse.current.modifiers
                )
                return
        match self.mouse.middle.state:
            case MouseButtonState.Pressed:
                d = self._distance(self.mouse.middle.press.physical, event.pos())
                if d >= settings().get("prefs/mouse/drag"):
                    self.mouse.middle.state = MouseButtonState.Dragging
                    self.state.mouseMiddleDragBegin(
                        self.mouse.middle.press.physical,
                        self.mouse.middle.press.logical,
                        self.mouse.middle.press.modifiers
                    )
                    return
            case MouseButtonState.Dragging:
                self.state.mouseMiddleDragCont(
                    self.mouse.current.physical,
                    self.mouse.current.logical,
                    self.mouse.current.modifiers
                )
                return
        self.state.mouseMove(
            self.mouse.current.physical,
            self.mouse.current.logical,
            self.mouse.current.modifiers
        )

    def mousePressEvent(self : MixinSelf, event : QMouseEvent) -> None:
        v = event.pos()
        s = self.mapToScene(v)
        m = self._getModifiers(event)
        if event.buttons() & qmb.LeftButton:
            self.mouse.left.press.setPL(v, s)
            self.mouse.left.press.modifiers = m
            self.mouse.left.state = MouseButtonState.Pressed
        if event.buttons() & qmb.MiddleButton:
            self.mouse.middle.press.setPL(v, s)
            self.mouse.middle.press.modifiers = m
            self.mouse.middle.state = MouseButtonState.Pressed

    def mouseReleaseEvent(self : MixinSelf, event : QMouseEvent) -> None:
        v = event.pos()
        s = self.mapToScene(v)
        m = self._getModifiers(event)
        if event.button() & qmb.LeftButton:
            self.mouse.left.release.setPL(v, s)
            self.mouse.left.release.modifiers = m
            match self.mouse.left.state:
                case MouseButtonState.Pressed:
                    self.state.mouseLeftClick(
                        self.mouse.left.release.physical,
                        self.mouse.left.release.logical,
                        self.mouse.left.release.modifiers
                    )
                    self.mouse.left.state = MouseButtonState.Idle
                case MouseButtonState.Dragging:
                    self.state.mouseLeftDragEnd(
                        self.mouse.left.release.physical,
                        self.mouse.left.release.logical,
                        self.mouse.left.release.modifiers
                    )
                    self.mouse.left.state = MouseButtonState.Idle
                case _:
                    logger().warning("Mouse left button released when idle")
        if event.button() & qmb.MiddleButton:
            self.mouse.middle.release.setPL(v, s)
            self.mouse.middle.release.modifiers = m
            match self.mouse.middle.state:
                case MouseButtonState.Pressed:
                    self.state.mouseMiddleClick(
                        self.mouse.middle.release.physical,
                        self.mouse.middle.release.logical,
                        self.mouse.middle.release.modifiers
                    )
                    self.mouse.middle.state = MouseButtonState.Idle
                case MouseButtonState.Dragging:
                    self.state.mouseMiddleDragEnd(
                        self.mouse.middle.release.physical,
                        self.mouse.middle.release.logical,
                        self.mouse.middle.release.modifiers
                    )
                    self.mouse.middle.state = MouseButtonState.Idle
                case _:
                    logger().warning("Mouse middle button released when idle")

    def mouseDoubleClickEvent(self : MixinSelf, event : QMouseEvent) -> None:
        v = event.pos()
        s = self.mapToScene(v)
        m = self._getModifiers(event)
        if event.button() & qmb.LeftButton:
            self.mouse.left.state = MouseButtonState.Idle
            self.state.mouseLeftDoubleClick(v, s, m)

    def wheelEvent(self : MixinSelf, event : QWheelEvent) -> None:
        v = event.position().toPoint()
        s = self.mapToScene(v)
        self.mouse.current.setPL(v, s)
        self.mouse.current.modifiers = self._getModifiers(event)
        n = event.angleDelta().y() / settings().get("prefs/mouse/wheel")
        match self.mouse.current.modifiers:
            case qkm.NoModifier:      # pan up/down
                self.ui.viewPanUp(n) if n >= 0 else self.ui.viewPanDown(-n)
            case qkm.ShiftModifier:   # pan left/right
                self.ui.viewPanLeft(n) if n >= 0 else self.ui.viewPanRight(-n)
            case qkm.ControlModifier: # zoom in/out
                self.ui.viewZoomIn(n) if n >= 0 else self.ui.viewZoomOut(-n)
