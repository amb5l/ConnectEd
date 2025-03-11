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
                m = self.mouse.left.press.modifiers
                if m == Qt.KeyboardModifier.NoModifier:
                    self.scene.clearSelection()
                self._selectPoint(
                    self.mouse.current.logical,
                    m == Qt.KeyboardModifier.ControlModifier
                )
            case self.State.ViewCenter:
                self._center(self.mouse.left.release.logical)
                self.state = self.State.Idle
            case self.State.ViewZoomWindow1:
                self.marquis.begin(self.mouse.left.press.physical)
                self.state = self.State.ViewZoomWindow2
            case self.State.ViewZoomWindow2:
                self.marquis.end(self.mouse.left.release.physical)
                self._zoomRect(self.marquis.rect())
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
            case self.State.Idle:
                m = self.mouse.left.press.modifiers
                if m == Qt.KeyboardModifier.NoModifier:
                    self.scene.clearSelection()
                self.marquis.begin(self.mouse.left.press.physical)
                self.state = self.State.SelectRectangle2
            case self.State.ViewZoomWindow1:
                self.marquis.begin(self.mouse.left.press.physical)
                self.state = self.State.ViewZoomWindow2
            case self.State.PlaceRectangle1:
                self._addWIP(Rectangle(
                    self._snap(self.mouse.left.press.logical)
                ))
                self.state = self.State.PlaceRectangle2

    def mouseLeftDragContinue(self : 'Drawing') -> None:
        match self.state:
            case self.State.SelectRectangle2:
                self.marquis.resize(self.mouse.current.physical)
            case self.State.ViewPan2:
                pass
            case self.State.ViewZoomWindow2:
                self.marquis.resize(self.mouse.current.physical)
            case self.State.PlaceRectangle2:
                self.wip.setPoint2(
                    self._snap(self.mouse.current.logical)
                )

    def mouseLeftDragEnd(self : 'Drawing') -> None:
        match self.state:
            case self.State.SelectRectangle2:
                m = self.mouse.left.press.modifiers
                self.marquis.end(self.mouse.left.release.physical)
                self._selectRect(
                    self.marquis.rect(),
                    m == Qt.KeyboardModifier.ControlModifier
                )
                self.state = self.State.Idle
            case self.State.ViewZoomWindow2:
                self.marquis.end(self.mouse.left.release.physical)
                self._zoomRect(self.marquis.rect())
                self.state = self.State.Idle
            case self.State.PlaceRectangle2:
                self.wip.setPoint2(
                    self._snap(self.mouse.left.release.logical)
                )
                self._completeWIP()
                self.state = self.State.Idle

    def mouseLeftDoubleClick(self : 'Drawing') -> None:
        pass

    def mouseMiddleClick(self : 'Drawing') -> None:
        pass

    def mouseMiddleDragBegin(self : 'Drawing') -> None:
        if self.state == self.State.Idle:
            match self.mouse.middle.press.modifiers:
                case Qt.KeyboardModifier.NoModifier:
                    self.pan_prev = self.mouse.current.physical
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    self.state = self.State.ViewPan2
                case Qt.KeyboardModifier.ControlModifier:
                    self.marquis.begin(self.mouse.middle.press.physical)
                    self.state = self.State.ViewZoomWindow2

    def mouseMiddleDragContinue(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.pan_prev
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.pan_prev = self.mouse.current.physical
            case self.State.ViewZoomWindow2:
                self.marquis.resize(self.mouse.current.physical)

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
                self.marquis.end(self.mouse.middle.release.physical)
                self._zoomRect(self.marquis.rect())
                self.state = self.State.Idle

    def mouseMiddleDoubleClick(self : 'Drawing') -> None:
        pass

    def mouseMove(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewZoomWindow2:
                self.marquis.resize(self.mouse.current.physical)
            case self.State.PlaceRectangle2:
                self.wip.setPoint2(
                    self._snap(self.mouse.current.logical)
                )

    def mouseWheel(self : 'Drawing', n: int, modifiers: Qt.KeyboardModifier) -> None:
        match modifiers:
            case Qt.KeyboardModifier.NoModifier:      # pan up/down
                self.viewPanUp(n) if n >= 0 else self.viewPanDown(-n)
            case Qt.KeyboardModifier.ShiftModifier:   # pan left/right
                self.viewPanLeft(n) if n >= 0 else self.viewPanRight(-n)
            case Qt.KeyboardModifier.ControlModifier: # zoom in/out
                self.viewZoomIn(n) if n >= 0 else self.viewZoomOut(-n)
