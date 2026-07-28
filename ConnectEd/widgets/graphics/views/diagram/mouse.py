from __future__ import annotations

from typing import Self
from enum   import Enum, Flag, auto

from PyQt6.QtCore import Qt, QEvent, QPoint, QPointF, QLine
from PyQt6.QtGui  import QEnterEvent, QMouseEvent, QWheelEvent, QCursor

from .....app import app, logger, settings, window


from .host import asDiagramView


class MouseState(Enum):
    IDLE          = auto()
    LEFT_PRESS    = auto()
    LEFT_DRAG     = auto()
    LEFT_PRESS2   = auto()
    MIDDLE_PRESS  = auto()
    MIDDLE_DRAG   = auto()
    MIDDLE_PRESS2 = auto()
    BAD_PRESS     = auto()


class MouseButton(Flag):
    LEFT   = Qt.MouseButton.LeftButton.value
    MIDDLE = Qt.MouseButton.MiddleButton.value
    MASK   = LEFT | MIDDLE


class MouseModifier(Flag):
    NONE  = Qt.KeyboardModifier.NoModifier.value
    SHIFT = Qt.KeyboardModifier.ShiftModifier.value
    CTRL  = Qt.KeyboardModifier.ControlModifier.value
    ALT   = Qt.KeyboardModifier.AltModifier.value
    MASK  = SHIFT | CTRL | ALT


class DiagramViewMouseMixin:
    _mouse_state           : MouseState
    _mouse_press_modifiers : MouseModifier
    _mouse_press_vpos      : QPoint         # mouse press view position
    _mouse_vpos            : QPoint         # mouse current view position
    _mouse_spos            : QPointF        # mouse current scene position
    _mouse_drag_distance   : float          # from settings
    _mouse_wheel_step      : float          # from settings

    def initMouse(self : Self) -> None:
        host = asDiagramView(self)
        if app().mouseButtons() == Qt.MouseButton.NoButton:
            host._mouse_state = MouseState.IDLE
        else:
            host._mouse_state = MouseState.BAD_PRESS
        host._mouse_press_modifiers = MouseModifier.NONE
        host._mouse_press_vpos = QPoint()
        host._mouse_vpos = host.mapFromGlobal(QCursor.pos())
        host._mouse_spos = host.mapToScene(host._mouse_vpos)
        host.mouseSettingsChange()
        settings().changed.connect(host.mouseSettingsChange)

    def mouseSettingsChange(self : Self) -> None:
        self._mouse_drag_distance = settings().get("prefs/mouse/drag")
        self._mouse_wheel_step = settings().get("prefs/mouse/wheel")

    def enterEvent(self : Self, event : QEnterEvent | None) -> None:
        """Handle mouse pointer entering the viewport."""
        host = asDiagramView(self)
        vpos = host.mapFromGlobal(QCursor.pos())
        spos = host.mapToScene(vpos)
        host._mouse_vpos, host._mouse_spos = vpos, spos
        window().statusBar().xy.setText(
            str(int(round(spos.x()))) + "," + str(int(round(spos.y())))
        )

    def leaveEvent(self : Self, a0 : QEvent | None) -> None:
        """Handle mouse pointer leaving the viewport."""
        host = asDiagramView(self)
        if a0 is None:
            logger().warning("No event")
            return
        if (viewport := host.viewport()) is None:
            raise TypeError("No viewport")
        # simulate central mouse position
        rect = viewport.rect()
        vpos = QPoint(rect.width() // 2, rect.height() // 2)
        spos = host.mapToScene(vpos)
        host._mouse_vpos, host._mouse_spos = vpos, spos
        window().statusBar().xy.setText("-,-")

    def mouseMoveEvent(self : Self, event : QMouseEvent | None) -> None:
        host = asDiagramView(self)
        if event is None:
            logger().warning("No event")
            return
        host._updateMousePos(event)
        match host._mouse_state:
            case MouseState.LEFT_PRESS | MouseState.MIDDLE_PRESS:
                drag_line = QLine(host._mouse_press_vpos, host._mouse_vpos)
                drag_distance = drag_line.toLineF().length()
                if drag_distance >= host._mouse_drag_distance:
                    if host._mouse_state == MouseState.LEFT_PRESS:
                        host._mouse_state = MouseState.LEFT_DRAG
                        host.state.mouseLeftDragBegin(*host._mouseArgs())
                    elif host._mouse_state == MouseState.MIDDLE_PRESS:
                        host._mouse_state = MouseState.MIDDLE_DRAG
                        host.state.mouseMiddleDragBegin(*host._mouseArgs())
            case MouseState.LEFT_DRAG:
                host.state.mouseLeftDragCont(*host._mouseArgs())
            case MouseState.MIDDLE_DRAG:
                host.state.mouseMiddleDragCont(*host._mouseArgs())
            case _:
                host.state.mouseMove(*host._mouseArgs())

    def mousePressEvent(self : Self, event : QMouseEvent | None) -> None:
        host = asDiagramView(self)
        if event is None:
            logger().warning("No event")
            return
        host._updateMousePos(event)
        if host._mouse_state == MouseState.IDLE:
            host._mouse_press_vpos = host._mouse_vpos
            host._mouse_press_modifiers = MouseModifier(
                event.modifiers().value & MouseModifier.MASK.value
            )
            if event.button() & Qt.MouseButton.LeftButton:
                host._mouse_state = MouseState.LEFT_PRESS
            elif event.button() & Qt.MouseButton.MiddleButton:
                host._mouse_state = MouseState.MIDDLE_PRESS
            else:
                host._mouse_state = MouseState.BAD_PRESS

    def mouseReleaseEvent(self : Self, event : QMouseEvent | None) -> None:
        host = asDiagramView(self)
        if event is None:
            logger().warning("No event")
            return
        host._updateMousePos(event)
        match host._mouse_state:
            case MouseState.BAD_PRESS:
                if app().mouseButtons() == Qt.MouseButton.NoButton:
                    host._mouse_state = MouseState.IDLE
            case MouseState.LEFT_PRESS:
                host._mouse_state = MouseState.IDLE
                host.state.mouseLeftClick(*host._mouseArgs())
            case MouseState.LEFT_DRAG:
                host._mouse_state = MouseState.IDLE
                host.state.mouseLeftDragEnd(*host._mouseArgs())
            case MouseState.LEFT_PRESS2:
                host._mouse_state = MouseState.IDLE
            case MouseState.MIDDLE_PRESS:
                host._mouse_state = MouseState.IDLE
                host.state.mouseMiddleClick(*host._mouseArgs())
            case MouseState.MIDDLE_DRAG:
                host._mouse_state = MouseState.IDLE
                host.state.mouseMiddleDragEnd(*host._mouseArgs())
            case MouseState.MIDDLE_PRESS2:
                host._mouse_state = MouseState.IDLE

    def mouseDoubleClickEvent(self : Self, event : QMouseEvent | None) -> None:
        host = asDiagramView(self)
        if event is None:
            logger().warning("No event")
            return
        host._updateMousePos(event)
        if event.button() & Qt.MouseButton.LeftButton:
            host._mouse_state = MouseState.LEFT_PRESS2
            host.state.mouseLeftDoubleClick(*host._mouseArgs())
        elif event.button() & Qt.MouseButton.MiddleButton:
            host._mouse_state = MouseState.MIDDLE_PRESS2
            host.state.mouseMiddleDoubleClick(*host._mouseArgs())
        else:
            host._mouse_state = MouseState.BAD_PRESS

    def wheelEvent(self : Self, event : QWheelEvent | None) -> None:
        host = asDiagramView(self)
        if event is None:
            logger().warning("No event")
            return
        # Wheel has no press; use current keyboard modifiers from the event.
        modifiers = MouseModifier(
            event.modifiers().value & MouseModifier.MASK.value
        )
        steps = event.angleDelta().y() / host._mouse_wheel_step
        match modifiers:
            case MouseModifier.NONE:      # pan up/down
                host.viewPanUp(steps) if steps >= 0 else host.viewPanDown(-steps)
            case MouseModifier.SHIFT:   # pan left/right
                host.viewPanLeft(steps) if steps >= 0 else host.viewPanRight(-steps)
            case MouseModifier.CTRL: # zoom in/out
                host.viewZoomIn(steps) if steps >= 0 else host.viewZoomOut(-steps)

    def _updateMousePos(
        self  : Self,
        event : QMouseEvent
    ) -> None:
        host = asDiagramView(self)
        host._mouse_vpos = event.pos()
        host._mouse_spos = host.mapToScene(host._mouse_vpos)

    def _mouseArgs(self : Self) -> tuple[QPoint, QPointF, MouseModifier]:
        return self._mouse_vpos, self._mouse_spos, self._mouse_press_modifiers

    def _mouseReleaseSync(self : Self):
        if app().mouseButtons() == Qt.MouseButton.NoButton:
            self._mouse_state = MouseState.IDLE
        else:
            self._mouse_state = MouseState.BAD_PRESS
