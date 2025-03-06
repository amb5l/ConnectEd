from PyQt6.QtCore import Qt, QRect

from ....core  import settings

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
            case self.State.ViewPan1:
                self.state = self.State.ViewPan2
            case self.State.ViewZoomWindow1:
                self.sel_rect = self.PLRect(
                    self,
                    QRect(self.mouse.left.press.physical, self.mouse.current.physical)
                )
                self._viewUpdate()
                self.state = self.State.ViewZoomWindow2
            case self.State.ViewZoomWindow2:
                self.sel_rect.setPhysical(self._normMinRect(
                    self.mouse.left.prev.physical,
                    self.mouse.left.release.physical
                ))
                self._zoomPRect(self.sel_rect.physical)
                self.sel_rect = None
                self.state = self.State.Idle

    def mouseLeftDragBegin(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewZoomWindow1:
                self.sel_rect = self.PLRect(
                    self,
                    QRect(self.mouse.left.press.physical, self.mouse.current.physical)
                )
                self._viewUpdate()
                self.state = self.State.ViewZoomWindow2

    def mouseLeftDragContinue(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                pass
            case self.State.ViewZoomWindow2:
                self.sel_rect.setPhysical(self._normMinRect(
                    self.mouse.left.press.physical,
                    self.mouse.current.physical
                ))
                self._viewUpdate()

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

    def mouseLeftDoubleClick(self : 'Drawing') -> None:
        pass

    def mouseMiddleClick(self : 'Drawing') -> None:
        pass

    def mouseMiddleDragBegin(self : 'Drawing') -> None:
        if self.state == self.State.Idle:
            match self.mouse.middle.press.modifiers:
                case Qt.KeyboardModifier.NoModifier:
                    self.state = self.State.ViewPan2
                case Qt.KeyboardModifier.ControlModifier:
                    self.state = self.State.ViewZoomWindow1

    def mouseMiddleDragContinue(self : 'Drawing') -> None:
        pass

    def mouseMiddleDragEnd(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan1:
                self.state = self.State.ViewPan2
            case self.State.ViewZoomWindow1:
                self.state = self.State.ViewZoomWindow2

    def mouseMiddleDoubleClick(self : 'Drawing') -> None:
        pass

    def mouseMove(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewZoomWindow2:
                self.sel_rect.setPhysical(self._normMinRect(
                    self.mouse.left.press.physical,
                    self.mouse.current.physical
                ))
                self._viewUpdate()
           #case self.State.PlaceRectangle1:
           #    self.wip.setOffset(self._snap(self.mouse.current.logical))
           #    self._viewUpdate()
           #case self.State.PlaceRectangle2:
           #    norm_rect = self._normMinRect(
           #        self.mouse.left.prev.logical,
           #        self._snap(self.mouse.current.logical)
           #    )
           #    self.wip.setOffset(norm_rect.topLeft())
           #    self.wip.setSize(norm_rect.size())
           #    self._viewUpdate()

    def mouseWheel(self : 'Drawing', n: int, modifiers: Qt.KeyboardModifier) -> None:
        if modifiers == Qt.KeyboardModifier.NoModifier:
            if n >= 0:
                self.viewZoomIn(n)
            else:
                self.viewZoomOut(-n)
