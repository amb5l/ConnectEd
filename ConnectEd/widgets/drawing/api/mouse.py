from PyQt6.QtCore import Qt, QRect, QPointF

from ....elements import Rectangle

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing


class DrawingApiMouseMixin:
    """Mixin class that provides mouse API for Drawing widgets."""

    def mouseLeftClick(self : 'Drawing') -> None:
        match self.state:
            case self.State.Idle:
                # TODO selection
                pass
            case self.State.ViewCenter:
                self._center(self.mouse.left.release.logical)
                self.state = self.State.Idle
            case self.State.ViewPan1:
                self.pan_prev = self.pan
                self.state = self.State.ViewPan2
            case self.State.ViewPan2:
                self.pan = self.pan_prev + QPointF((
                    self.mouse.left.prev.physical -
                    self.mouse.left.release.physical
                ) / self.zoom)
                self._panUpdate()
                self.state = self.State.Idle
            case self.State.ViewZoomWindow1:
                self.sel_rect = self.PLRect(
                    self,
                    QRect(
                        self.mouse.left.press.physical,
                        self.mouse.current.physical
                    )
                )
                self.update()
                self.state = self.State.ViewZoomWindow2
            case self.State.ViewZoomWindow2:
                self.sel_rect.setPhysical(self._normMinRect(
                    self.mouse.left.prev.physical,
                    self.mouse.left.release.physical
                ))
                self._zoomPRect(self.sel_rect.physical)
                self.sel_rect = None
                self.state = self.State.Idle
            case self.State.PlaceRectangle1:
                self.wip = [Rectangle(self.mouse.left.press.logical)]
                self.state = self.State.PlaceRectangle2
            case self.State.PlaceRectangle2:
                self.wip[0].setRect(
                    self.mouse.left.prev.logical,
                    self.mouse.left.release.logical
                )
                self.elements.append(self.wip.pop(0))
                self.update()
                self.state = self.State.Idle

    def mouseLeftDragBegin(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewZoomWindow1:
                self.sel_rect = self.PLRect(
                    self,
                    QRect(
                        self.mouse.left.press.physical,
                        self.mouse.current.physical
                    )
                )
                self.update()
                self.state = self.State.ViewZoomWindow2
            case self.State.PlaceRectangle1:
                self.wip = [Rectangle(self.mouse.left.press.logical)]
                self.state = self.State.PlaceRectangle2

    def mouseLeftDragContinue(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                pass
            case self.State.ViewZoomWindow2:
                self.sel_rect.setPhysical(self._normMinRect(
                    self.mouse.left.press.physical,
                    self.mouse.current.physical
                ))
                self.update()
            case self.State.PlaceRectangle2:
                self.wip[0].setRect(
                    self.mouse.left.press.logical,
                    self.mouse.current.logical
                )
                self.update()

    def mouseLeftDragEnd(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewZoomWindow2:
                self.sel_rect.setPhysical(self._normMinRect(
                    self.mouse.left.press.physical,
                    self.mouse.left.release.physical
                ))
                self._zoomPRect(self.sel_rect.physical)
                self.sel_rect = None
                self.state = self.State.Idle
            case self.State.PlaceRectangle2:
                self.wip[0].setRect(
                    self.mouse.left.press.logical,
                    self.mouse.left.release.logical
                )
                self.elements.append(self.wip.pop(0))
                self.update()
                self.state = self.State.Idle

    def mouseLeftDoubleClick(self : 'Drawing') -> None:
        pass

    def mouseMiddleClick(self : 'Drawing') -> None:
        self._center(self.mouse.middle.press.logical)

    def mouseMiddleDragBegin(self : 'Drawing') -> None:
        if self.state == self.State.Idle:
            match self.mouse.middle.press.modifiers:
                case Qt.KeyboardModifier.NoModifier:
                    self.pan_prev = self.pan
                    self.state = self.State.ViewPan2
                case Qt.KeyboardModifier.ControlModifier:
                    # TODO sel_rect convenience functions(s) to simplify this
                    self.sel_rect = self.PLRect(
                        self,
                        QRect(
                            self.mouse.middle.press.physical,
                            self.mouse.current.physical
                        )
                    )
                    self.update()
                    self.state = self.State.ViewZoomWindow2

    def mouseMiddleDragContinue(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                self.pan = self.pan_prev + QPointF((
                    self.mouse.middle.press.physical -
                    self.mouse.current.physical
                ) / self.zoom)
                self._panUpdate()
            case self.State.ViewZoomWindow2:
                self.sel_rect.setPhysical(self._normMinRect(
                    self.mouse.middle.press.physical,
                    self.mouse.current.physical
                ))
                self.update()

    def mouseMiddleDragEnd(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                self.pan = self.pan_prev + QPointF((
                    self.mouse.middle.press.physical -
                    self.mouse.middle.release.physical
                ) / self.zoom)
                self._panUpdate()
                self.state = self.State.Idle
            case self.State.ViewZoomWindow2:
                self.sel_rect.setPhysical(self._normMinRect(
                    self.mouse.middle.press.physical,
                    self.mouse.middle.release.physical
                ))
                self._zoomPRect(self.sel_rect.physical)
                self.sel_rect = None
                self.state = self.State.Idle

    def mouseMiddleDoubleClick(self : 'Drawing') -> None:
        pass

    def mouseMove(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                self.pan = self.pan_prev + QPointF((
                    self.mouse.left.press.physical -
                    self.mouse.current.physical
                ) / self.zoom)
                self._panUpdate()
            case self.State.ViewZoomWindow2:
                self.sel_rect.setPhysical(self._normMinRect(
                    self.mouse.left.press.physical,
                    self.mouse.current.physical
                ))
                self.update()
            case self.State.PlaceRectangle2:
                self.wip[0].setRect(
                    self.mouse.left.press.logical,
                    self.mouse.current.logical
                )
                self.update()

    def mouseWheel(self : 'Drawing', n: int, modifiers: Qt.KeyboardModifier) -> None:
        match modifiers:
            case Qt.KeyboardModifier.NoModifier:      # pan up/down
                self.viewPanUp() if n >= 0 else self.viewPanDown()
            case Qt.KeyboardModifier.ShiftModifier:   # pan left/right
                self.viewPanLeft() if n >= 0 else self.viewPanRight()
            case Qt.KeyboardModifier.ControlModifier: # zoom in/out
                self.viewZoomIn(n) if n >= 0 else self.viewZoomOut(-n)
