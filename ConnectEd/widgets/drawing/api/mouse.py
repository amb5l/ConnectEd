from PyQt6.QtCore import Qt

from ...items import Rectangle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing


class DrawingApiMouseMixin:
    """Mixin class that provides mouse API for Drawing widgets."""

    def mouseLeftClick(self : 'Drawing') -> None:
        match self.state:
            case self.State.Idle:
                pass
            case self.State.ViewCenter:
                self._center(self.mouse.left.release.logical)
                self.state = self.State.Idle
            case self.State.ViewZoomWindow1:
                self.point1 = self.mouse.left.press.physical
                self.rubber_band.setGeometry(
                    self.point1.x(), self.point1.y(), 1, 1
                )
                self.rubber_band.show()
                self.scene.update()
                self.state = self.State.ViewZoomWindow2
            case self.State.ViewZoomWindow2:
                self.rubber_band.setGeometry(
                    self.point1.x(), self.point1.y(),
                    self.mouse.left.release.physical.x() - self.point1.x(),
                    self.mouse.left.release.physical.y() - self.point1.y()
                )
                self.rubber_band.hide()
                self.point1 = None
                self._zoomRect(self._rubberBandRect())
                self.state = self.State.Idle
            case self.State.PlaceRectangle1:
                self._addWIP(Rectangle(
                    self._snap(self.mouse.left.press.logical)
                ))
                self.state = self.State.PlaceRectangle2
            case self.State.PlaceRectangle2:
                self.wip.setPoint2(
                    self._snap(self.mouse.left.release.logical)
                )
                self._completeWIP()
                self.state = self.State.Idle

    def mouseLeftDragBegin(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewZoomWindow1:
                self.point1 = self.mouse.left.press.physical
                self.rubber_band.setGeometry(
                    self.point1.x(), self.point1.y(), 1, 1
                )
                self.rubber_band.show()
                self.scene.update()
                self.state = self.State.ViewZoomWindow2
            case self.State.PlaceRectangle1:
                self._addWIP(Rectangle(
                    self._snap(self.mouse.left.press.logical)
                ))
                self.state = self.State.PlaceRectangle2

    def mouseLeftDragContinue(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                pass
            case self.State.ViewZoomWindow2:
                self.rubber_band.setGeometry(
                    self.point1.x(), self.point1.y(),
                    self.mouse.current.physical.x() - self.point1.x(),
                    self.mouse.current.physical.y() - self.point1.y()
                )
                self.scene.update()
            case self.State.PlaceRectangle2:
                self.wip.setPoint2(
                    self._snap(self.mouse.current.logical)
                )
                self.scene.update()

    def mouseLeftDragEnd(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewZoomWindow2:
                self.rubber_band.setGeometry(
                    self.point1.x(), self.point1.y(),
                    self.mouse.left.release.physical.x() - self.point1.x(),
                    self.mouse.left.release.physical.y() - self.point1.y()
                )
                self.rubber_band.hide()
                self.point1 = None
                self._zoomRect(self._rubberBandRect())
                self.state = self.State.Idle
            case self.State.PlaceRectangle2:
                self.wip.setPoint2(
                    self._snap(self.mouse.left.release.logical)
                )
                self._completeWIP()
                self.state = self.State.Idle
                self.scene.update()

    def mouseLeftDoubleClick(self : 'Drawing') -> None:
        pass

    def mouseMiddleClick(self : 'Drawing') -> None:
        self._center(self.mouse.middle.press.logical)

    def mouseMiddleDragBegin(self : 'Drawing') -> None:
        if self.state == self.State.Idle:
            match self.mouse.middle.press.modifiers:
                case Qt.KeyboardModifier.NoModifier:
                    self.pan_prev = self.mouse.current.physical
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    self.state = self.State.ViewPan2
                case Qt.KeyboardModifier.ControlModifier:
                    self.point1 = self.mouse.middle.press.physical
                    self.rubber_band.setGeometry(
                        self.point1.x(), self.point1.y(), 1, 1
                    )
                    self.rubber_band.show()
                    self.scene.update()
                    self.state = self.State.ViewZoomWindow2

    def mouseMiddleDragContinue(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.pan_prev
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.pan_prev = self.mouse.current.physical
            case self.State.ViewZoomWindow2:
                self.rubber_band.setGeometry(
                    self.point1.x(), self.point1.y(),
                    self.mouse.current.physical.x() - self.point1.x(),
                    self.mouse.current.physical.y() - self.point1.y()
                )
                self.scene.update()

    def mouseMiddleDragEnd(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.pan_prev
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.pan_prev = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.state = self.State.Idle
            case self.State.ViewZoomWindow2:
                self.rubber_band.setGeometry(
                    self.point1.x(), self.point1.y(),
                    self.mouse.middle.release.physical.x() - self.point1.x(),
                    self.mouse.middle.release.physical.y() - self.point1.y()
                )
                self.rubber_band.hide()
                self.point1 = None
                self._zoomRect(self._rubberBandRect())
                self.state = self.State.Idle

    def mouseMiddleDoubleClick(self : 'Drawing') -> None:
        pass

    def mouseMove(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewZoomWindow2:
                self.rubber_band.setGeometry(
                    self.point1.x(), self.point1.y(),
                    self.mouse.current.physical.x() - self.point1.x(),
                    self.mouse.current.physical.y() - self.point1.y()
                )
                self.scene.update()
            case self.State.PlaceRectangle2:
                self.wip.setPoint2(
                    self._snap(self.mouse.current.logical)
                )
                self.scene.update()

    def mouseWheel(self : 'Drawing', n: int, modifiers: Qt.KeyboardModifier) -> None:
        match modifiers:
            case Qt.KeyboardModifier.NoModifier:      # pan up/down
                self.viewPanUp(n) if n >= 0 else self.viewPanDown(-n)
            case Qt.KeyboardModifier.ShiftModifier:   # pan left/right
                self.viewPanLeft(n) if n >= 0 else self.viewPanRight(-n)
            case Qt.KeyboardModifier.ControlModifier: # zoom in/out
                self.viewZoomIn(n) if n >= 0 else self.viewZoomOut(-n)
