from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui  import QEnterEvent, QMouseEvent, QWheelEvent, QCursor

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

    def enterEvent(self : 'Drawing', event : QEnterEvent ) -> None:
        p = self.mapFromGlobal(QCursor.pos())
        l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        self.main_window.status_bar.xy.setText(
            str(int(round(l.x()))) + ',' + str(int(round(l.y())))
        )

    def leaveEvent(self : 'Drawing', _ : QEvent) -> None:
        rect = self.viewport().rect()
        p = QPoint(rect.width() // 2, rect.height() // 2)
        l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        self.main_window.status_bar.xy.setText('-,-')

    def mouseMoveEvent(self : 'Drawing', event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        self.main_window.status_bar.xy.setText(
            str(int(round(l.x()))) + ',' + str(int(round(l.y())))
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
        p = event.pos(); l = self.mapToScene(p)
        items = self.scene.items(
            l,
            Qt.ItemSelectionMode.IntersectsItemShape,
            Qt.SortOrder.DescendingOrder,
            self.viewportTransform()
        )
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.mouse.left.press.setPL(p, l)
            self.mouse.left.press.modifiers = self._getModifiers(event)
            self.mouse.left.state = self.MouseButtonState.Pressed
        if event.buttons() & Qt.MouseButton.MiddleButton:
            self.mouse.middle.press.setPL(p, l)
            self.mouse.middle.press.modifiers = self._getModifiers(event)
            self.mouse.middle.state = self.MouseButtonState.Pressed

    def mouseReleaseEvent(self : 'Drawing', event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p)
        if event.button() & Qt.MouseButton.LeftButton:
            self.mouse.left.release.setPL(p, l)
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
            self.mouse.middle.release.setPL(p, l)
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
        p = event.pos(); l = self.mapToScene(p)
        self.mouse.left.double.setPL(p, l)
        self.mouse.left.double.modifiers = self._getModifiers(event)
        if event.button() & Qt.MouseButton.LeftButton:
            self.mouseLeftDoubleClick()
        if event.button() & Qt.MouseButton.MiddleButton:
            self.mouseMiddleDoubleClick()

    def wheelEvent(self : 'Drawing', event : QWheelEvent) -> None:
        p = event.position().toPoint(); l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        self.mouseWheel(
            event.angleDelta().y() / settings.prefs.mouse.wheel,
            self._getModifiers(event)
        )
