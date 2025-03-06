from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui  import QMouseEvent, QWheelEvent, QCursor

from ....core import logger, settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing

class DrawingEventsMouseMixin:
    """
    Mixin class that handles mouse events for Drawing widgets,
    and forwards simplified calls to the Drawing widget's mouse API.

    This class forwards mouse events to the Drawing widget's mouse API.
    """

    def enterEvent(self : 'Drawing', event : QEvent) -> None:#
        self.mouse.setPos(self.mapFromGlobal(QCursor.pos()))
        self._panStatusBar()

    def leaveEvent(self : 'Drawing', event : QEvent) -> None:
        self.mouse.setPos(QPoint(self.width() // 2, self.height() // 2))
        self.main_window.status_bar.xy.setText('-,-')

    def mouseMoveEvent(self : 'Drawing', event : QMouseEvent) -> None:
        self.mouse.current.set(event.pos())
        self.main_window.status_bar.xy.setText(
            str(int(self.mouse.current.logical.x())) + ',' +
            str(int(self.mouse.current.logical.y()))
        )
        match self.mouse.left.state:
            case self.MouseButtonState.Pressed:
                d = self._distance(self.mouse.left.press.physical, event.pos())
                if d >= settings.prefs.mouse.drag:
                    self.mouse.left.state = self.MouseButtonState.Dragging
                    self.mouseLeftDragBegin()
                    return
            case self.MouseButtonState.Dragging:
                self.mouseLeftDragContinue()
                return
        match self.mouse.middle.state:
            case self.MouseButtonState.Pressed:
                d = self._distance(self.mouse.middle.press.physical, event.pos())
                if d >= settings.prefs.mouse.drag:
                    self.mouse.middle.state = self.MouseButtonState.Dragging
                    self.mouseMiddleDragBegin()
                    return
            case self.MouseButtonState.Dragging:
                self.mouseMiddleDragContinue()
                return
        self.mouseMove()

    def mousePressEvent(self : 'Drawing', event : QMouseEvent) -> None:
        print('mousePressEvent')
        modifiers = self._getModifiers(event)
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.mouse.left.setPress(event.pos(), modifiers)
            self.mouse.left.state = self.MouseButtonState.Pressed
        if event.buttons() & Qt.MouseButton.MiddleButton:
            self.mouse.middle.setPress(event.pos(), modifiers)
            self.mouse.middle.state = self.MouseButtonState.Pressed

    def mouseReleaseEvent(self : 'Drawing', event : QMouseEvent) -> None:
        print('mouseReleaseEvent')
        if event.button() & Qt.MouseButton.LeftButton:
            self.mouse.left.setRelease(event.pos())
            match self.mouse.left.state:
                case self.MouseButtonState.Pressed:
                    self.mouseLeftClick()
                    self.mouse.left.state = self.MouseButtonState.Idle
                case self.MouseButtonState.Dragging:
                    self.mouseLeftDragEnd()
                    self.mouse.left.state = self.MouseButtonState.Idle
                case _:
                    logger.warning(f'Mouse left button released when idle')
        if event.button() & Qt.MouseButton.MiddleButton:
            self.mouse.middle.setRelease(event.pos())
            match self.mouse.middle.state:
                case self.MouseButtonState.Pressed:
                    self.mouseMiddleClick()
                    self.mouse.middle.state = self.MouseButtonState.Idle
                case self.MouseButtonState.Dragging:
                    self.mouseMiddleDragEnd()
                    self.mouse.middle.state = self.MouseButtonState.Idle
                case _:
                    logger.warning(f'Mouse middle button released when idle')

    def mouseDoubleClickEvent(self : 'Drawing', event : QMouseEvent) -> None:
        print('mouseDoubleClickEvent')
        if event.button() & Qt.MouseButton.LeftButton:
            self.mouseLeftDoubleClick(event.pos(), self._getModifiers(event))
        if event.button() & Qt.MouseButton.MiddleButton:
            self.mouseMiddleDoubleClick()

    def wheelEvent(self : 'Drawing', event : QWheelEvent) -> None:
        self.mouseWheel(
            event.angleDelta().y() / settings.prefs.mouse.wheel,
            self._getModifiers(event)
        )
