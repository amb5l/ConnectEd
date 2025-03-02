from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui  import QMouseEvent, QWheelEvent

from ....core import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing

class DrawingEventsMouseMixin:
    """
    Mixin class that handles mouse events for Drawing widgets.

    This class forwards mouse events to the Drawing widget's mouse API.
    """

    def enterEvent(self : 'Drawing', event : QEvent) -> None:#
        self.mouseEnter()

    def leaveEvent(self : 'Drawing', event : QEvent) -> None:
        self.mouseLeave()

    def mouseMoveEvent(self : 'Drawing', event : QMouseEvent) -> None:
        self.mouseMove(event.pos())

    def mousePressEvent(self : 'Drawing', event : QMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.mouseLeftPress(event.pos(), self._getModifiers(event))
        elif event.buttons() & Qt.MouseButton.MiddleButton:
            self.mouseMiddlePress(event.pos(), self._getModifiers(event))

    def mouseReleaseEvent(self : 'Drawing', event : QMouseEvent) -> None:
        if event.button() & Qt.MouseButton.LeftButton:
            self.mouseLeftRelease(event.pos())
        elif event.button() & Qt.MouseButton.MiddleButton:
            self.mouseMiddleRelease(event.pos())

    def mouseDoubleClickEvent(self : 'Drawing', event : QMouseEvent) -> None:
        if event.button() & Qt.MouseButton.LeftButton:
            self.mouseLeftDoubleClick(event.pos(), self._getModifiers(event))

    def wheelEvent(self : 'Drawing', event : QWheelEvent) -> None:
        self.mouseWheel(event.angleDelta().y() / settings.prefs.display.zoom.wheel, self._getModifiers(event))
