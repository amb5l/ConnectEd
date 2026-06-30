from __future__ import annotations

from typing import Self
from enum   import Enum, Flag, auto

from PyQt6.QtCore import Qt, QEvent, QPoint, QPointF, QLine
from PyQt6.QtGui  import QEnterEvent, QMouseEvent, QWheelEvent, QCursor

from .....app import app, logger, settings, window


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
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if app().mouseButtons() == Qt.MouseButton.NoButton:
            self._mouse_state = MouseState.IDLE
        else:
            self._mouse_state = MouseState.BAD_PRESS
        self._mouse_press_modifiers = MouseModifier.NONE
        self._mouse_press_vpos = QPoint()
        self._mouse_vpos = self.mapFromGlobal(QCursor.pos())
        self._mouse_spos = self.mapToScene(self._mouse_vpos)
        self.mouseSettingsChange()
        settings().changed.connect(self.mouseSettingsChange)

    def mouseSettingsChange(self : Self) -> None:
        self._mouse_drag_distance = settings().get("prefs/mouse/drag")
        self._mouse_wheel_step = settings().get("prefs/mouse/wheel")

    def enterEvent(self : Self, event : QEnterEvent | None) -> None:
        """Handle mouse pointer entering the viewport."""
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        vpos = self.mapFromGlobal(QCursor.pos())
        spos = self.mapToScene(vpos)
        self._mouse_vpos, self._mouse_spos = vpos, spos
        window().statusBar().xy.setText(
            str(int(round(spos.x()))) + "," + str(int(round(spos.y())))
        )

    def leaveEvent(self : Self, a0 : QEvent | None) -> None:
        """Handle mouse pointer leaving the viewport."""
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if a0 is None:
            logger().warning("No event")
            return
        viewport = self.viewport()
        if viewport is None:
            raise TypeError("No viewport")
        # simulate central mouse position
        rect = viewport.rect()
        vpos = QPoint(rect.width() // 2, rect.height() // 2)
        spos = self.mapToScene(vpos)
        self._mouse_vpos, self._mouse_spos = vpos, spos
        window().statusBar().xy.setText("-,-")

    def mouseMoveEvent(self : Self, event : QMouseEvent | None) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if event is None:
            logger().warning("No event")
            return
        self._updateMousePos(event)
        match self._mouse_state:
            case MouseState.LEFT_PRESS | MouseState.MIDDLE_PRESS:
                drag_line = QLine(self._mouse_press_vpos, self._mouse_vpos)
                drag_distance = drag_line.toLineF().length()
                if drag_distance >= self._mouse_drag_distance:
                    if self._mouse_state == MouseState.LEFT_PRESS:
                        self._mouse_state = MouseState.LEFT_DRAG
                        self.state.mouseLeftDragBegin(*self._mouseArgs())
                    elif self._mouse_state == MouseState.MIDDLE_PRESS:
                        self._mouse_state = MouseState.MIDDLE_DRAG
                        self.state.mouseMiddleDragBegin(*self._mouseArgs())
            case MouseState.LEFT_DRAG:
                self.state.mouseLeftDragCont(*self._mouseArgs())
            case MouseState.MIDDLE_DRAG:
                self.state.mouseMiddleDragCont(*self._mouseArgs())
            case _:
                self.state.mouseMove(*self._mouseArgs())

    def mousePressEvent(self : Self, event : QMouseEvent | None) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if event is None:
            logger().warning("No event")
            return
        self._updateMousePos(event)
        if self._mouse_state == MouseState.IDLE:
            self._mouse_press_vpos = self._mouse_vpos
            self._mouse_press_modifiers = MouseModifier(
                event.modifiers().value & MouseModifier.MASK.value
            )
            if event.button() & Qt.MouseButton.LeftButton:
                self._mouse_state = MouseState.LEFT_PRESS
            elif event.button() & Qt.MouseButton.MiddleButton:
                self._mouse_state = MouseState.MIDDLE_PRESS
            else:
                self._mouse_state = MouseState.BAD_PRESS

    def mouseReleaseEvent(self : Self, event : QMouseEvent | None) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if event is None:
            logger().warning("No event")
            return
        self._updateMousePos(event)
        match self._mouse_state:
            case MouseState.BAD_PRESS:
                if app().mouseButtons() == Qt.MouseButton.NoButton:
                    self._mouse_state = MouseState.IDLE
            case MouseState.LEFT_PRESS:
                self._mouse_state = MouseState.IDLE
                self.state.mouseLeftClick(*self._mouseArgs())
            case MouseState.LEFT_DRAG:
                self._mouse_state = MouseState.IDLE
                self.state.mouseLeftDragEnd(*self._mouseArgs())
            case MouseState.LEFT_PRESS2:
                self._mouse_state = MouseState.IDLE
            case MouseState.MIDDLE_PRESS:
                self._mouse_state = MouseState.IDLE
                self.state.mouseMiddleClick(*self._mouseArgs())
            case MouseState.MIDDLE_DRAG:
                self._mouse_state = MouseState.IDLE
                self.state.mouseMiddleDragEnd(*self._mouseArgs())
            case MouseState.MIDDLE_PRESS2:
                self._mouse_state = MouseState.IDLE

    def mouseDoubleClickEvent(self : Self, event : QMouseEvent | None) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if event is None:
            logger().warning("No event")
            return
        self._updateMousePos(event)
        if event.button() & Qt.MouseButton.LeftButton:
            self._mouse_state = MouseState.LEFT_PRESS2
            self.state.mouseLeftDoubleClick(*self._mouseArgs())
        elif event.button() & Qt.MouseButton.MiddleButton:
            self._mouse_state = MouseState.MIDDLE_PRESS2
            self.state.mouseMiddleDoubleClick(*self._mouseArgs())
        else:
            self._mouse_state = MouseState.BAD_PRESS

    def wheelEvent(self : Self, event : QWheelEvent | None) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        if event is None:
            logger().warning("No event")
            return
        # Wheel has no press; use current keyboard modifiers from the event.
        modifiers = MouseModifier(
            event.modifiers().value & MouseModifier.MASK.value
        )
        steps = event.angleDelta().y() / self._mouse_wheel_step
        match modifiers:
            case MouseModifier.NONE:      # pan up/down
                self.viewPanUp(steps) if steps >= 0 else self.viewPanDown(-steps)
            case MouseModifier.SHIFT:   # pan left/right
                self.viewPanLeft(steps) if steps >= 0 else self.viewPanRight(-steps)
            case MouseModifier.CTRL: # zoom in/out
                self.viewZoomIn(steps) if steps >= 0 else self.viewZoomOut(-steps)

    def _updateMousePos(
        self  : Self,
        event : QMouseEvent
    ) -> None:
        from . import DiagramView
        if not isinstance(self, DiagramView): raise TypeError("Bad host")
        self._mouse_vpos = event.pos()
        self._mouse_spos = self.mapToScene(self._mouse_vpos)

    def _mouseArgs(self : Self) -> tuple[QPoint, QPointF, MouseModifier]:
        return self._mouse_vpos, self._mouse_spos, self._mouse_press_modifiers

    def _mouseReleaseSync(self : Self):
        if app().mouseButtons() == Qt.MouseButton.NoButton:
            self._mouse_state = MouseState.IDLE
        else:
            self._mouse_state = MouseState.BAD_PRESS
