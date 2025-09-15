from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui  import QEnterEvent, QMouseEvent, QWheelEvent, QCursor

from .....app import logger, settings, window

from ...items.handle import Handle

from .defs import DrawingViewMouseButtonState as MouseButtonState

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingView


qkm = Qt.KeyboardModifier

class DrawingViewMouseMixin:
    def enterEvent(self : "DrawingView", event : QEnterEvent) -> None:
        p = self.mapFromGlobal(QCursor.pos())
        l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        window().status_bar.xy.setText(
            str(int(round(l.x()))) + "," + str(int(round(l.y())))
        )

    def leaveEvent(self : "DrawingView", _ : QEvent) -> None:
        rect = self.viewport().rect()
        p = QPoint(rect.width() // 2, rect.height() // 2)
        l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        window().status_bar.xy.setText("-,-")

    def mouseMoveEvent(self : "DrawingView", event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p); m = self._getModifiers(event)
        self.mouse.current.setPL(p, l)
        self.mouse.current.modifiers = m
        window().status_bar.xy.setText(
            str(int(round(l.x()))) + "," + str(int(round(l.y())))
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

    def mousePressEvent(self : "DrawingView", event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p); m = self._getModifiers(event)
        if (event.buttons() & Qt.MouseButton.RightButton) \
        or (event.buttons() & Qt.MouseButton.LeftButton and m == qkm.NoModifier):
            items = self._itemsAt(l)
            if items:
                if not isinstance(items[0], Handle):
                    if not items[0].isSelected():
                        self.scene().clearSelection()
                        items[0].setSelected(True)
            else:
                self.scene().clearSelection()
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.mouse.left.press.setPL(p, l)
            self.mouse.left.press.modifiers = m
            self.mouse.left.state = MouseButtonState.Pressed
        if event.buttons() & Qt.MouseButton.MiddleButton:
            self.mouse.middle.press.setPL(p, l)
            self.mouse.middle.press.modifiers = m
            self.mouse.middle.state = MouseButtonState.Pressed

    def mouseReleaseEvent(self : "DrawingView", event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p); m = self._getModifiers(event)
        if event.button() & Qt.MouseButton.LeftButton:
            self.mouse.left.release.setPL(p, l)
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
                    logger().warning(f"Mouse left button released when idle")
        if event.button() & Qt.MouseButton.MiddleButton:
            self.mouse.middle.release.setPL(p, l)
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
                    logger().warning(f"Mouse middle button released when idle")

    def wheelEvent(self : "DrawingView", event : QWheelEvent) -> None:
        p = event.position().toPoint(); l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        self.mouse.current.modifiers = self._getModifiers(event)
        n = event.angleDelta().y() / settings().get("prefs/mouse/wheel")
        match self.mouse.current.modifiers:
            case qkm.NoModifier:      # pan up/down
                self.viewPanUp(n) if n >= 0 else self.viewPanDown(-n)
            case qkm.ShiftModifier:   # pan left/right
                self.viewPanLeft(n) if n >= 0 else self.viewPanRight(-n)
            case qkm.ControlModifier: # zoom in/out
                self.viewZoomIn(n) if n >= 0 else self.viewZoomOut(-n)
