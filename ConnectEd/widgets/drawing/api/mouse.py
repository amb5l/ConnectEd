from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui  import QCursor

from ....core  import settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing


class DrawingApiMouseMixin:
    """Mixin class that provides mouse API for Drawing widgets."""

    def mouseEnter(self : 'Drawing') -> None:
        self.mouse.setPos(self.mapFromGlobal(QCursor.pos()))
        self._viewUpdate()

    def mouseLeave(self : 'Drawing') -> None:
        self.mouse.setPos(QPoint(self.width() // 2, self.height() // 2))
        self.main_window.status_bar.xy.setText('-,-')
        self._viewUpdate()

    def mouseMove(self : 'Drawing', pos: QPoint) -> None:
        self.mouse.setPos(pos)
        self.main_window.status_bar.xy.setText(
            str(int(self.mouse.current.logical.x())) + ',' +
            str(int(self.mouse.current.logical.y()))
        )
        # left button drag detection
        if  self.mouse.left.state == self.MouseState.Pressed \
        and self._scalarDistance(self.mouse.left.press.physical, pos) > settings.prefs.edit.drag:
            self.mouse.left.state = self.MouseState.Dragging
            # state transitions as we start dragging
            match self.state:
                case self.State.ViewZoomWindow1:
                    self.state = self.State.ViewZoomWindow2
                case self.State.PlaceBlock1:
                    self.state = self.State.PlaceBlock2
        # middle button drag detection
        if  self.mouse.middle.state == self.MouseState.Pressed \
        and self._scalarDistance(self.mouse.middle.press.physical, pos) > settings.prefs.edit.drag:
            self.mouse.middle.state = self.MouseState.Dragging
            self.mouse_press_prev.physical = self.mouse.middle.press.physical
            self.sel_rect = self._normMinRect(self.mouse_press_prev.physical, self.mouse.current.physical, 1)
            self.state = self.State.ViewZoomWindow2
        # state dependent movement responses
        match self.state:
            case self.State.ViewZoomWindow1:
                self._viewUpdate()
            case self.State.ViewZoomWindow2:
                self.sel_rect = self._normMinRect(self.mouse_press_prev.physical, self.mouse.current.physical, 1)
                self._viewUpdate()
            case self.State.PlaceBlock1:
                self.wip.setOffset(self._snap(self.mouse.current.logical)) # TODO: snap
                self._viewUpdate()
            case self.State.PlaceBlock2:
                norm_rect = self._normMinRect(self.mouse_press_prev.logical, self._snap(self.mouse.current.logical))
                self.wip.setOffset(norm_rect.topLeft())
                self.wip.setSize(norm_rect.size())
                self._viewUpdate()
            case self.State.PlaceText:
                self.wip.setOffset(self._snap(self.mouse.current.logical))
                self._viewUpdate()

    def mouseLeftPress(self : 'Drawing', physical: QPoint, modifiers: Qt.KeyboardModifier) -> None:
        self.mouse.left.press.physical = physical
        self.mouse.left.press.logical = self._cp2dp(physical)
        self.mouse.left.release.physical = None
        self.mouse.left.release.logical = None
        self.mouse.left.state = self.MouseState.Pressed
        match self.state:
            case self.State.Idle:
                self._selectPoint(self.mouse.current.logical)
            case self.State.ViewZoomWindow1:
                self.mouse_press_prev.physical = None
                self.mouse_press_prev.logical = self.mouse.left.press.logical
                self.sel_rect = QRect(self.mouse.left.press.logical, QSize(1, 1))
                self._viewUpdate()
            case self.State.PlaceBlock1:
                assert isinstance(self.wip, DrawingItemBlock)
                self.mouse_press_prev.physical = None
                self.mouse_press_prev.logical = self._snap(self.mouse.left.press.logical)
                self.wip.setOffset(self._snap(self.mouse.left.press.logical))
                self._viewUpdate()
            case self.State.PlaceText:
                assert isinstance(self.wip, DrawingItemText)
                self.wip.setOffset(self._snap(self.mouse.current.logical))
                self.contents.append(self.wip)
                self.wip = None
                self.state = self.State.Idle
                self._viewUpdate()

    def mouseLeftRelease(self : 'Drawing', physical: QPoint) -> None:
        self.mouse.left.release.physical = physical
        self.mouse.left.release.logical = self._cp2dp(physical)
        self.mouse.left.state = self.MouseState.Idle
        match self.state:
            case self.State.ViewZoomWindow1:
                self.state = self.State.ViewZoomWindow2
                self._viewUpdate()
            case self.State.ViewZoomWindow2:
                self.sel_rect = self._normMinRect(self.mouse_press_prev.physical, self.mouse.left.release.physical)
                self._zoomCRect(self.sel_rect)
                self.sel_rect = None
                self.state = self.State.Idle
            case self.State.PlaceBlock1:
                self.state = self.State.PlaceBlock2
                self._viewUpdate()
            case self.State.PlaceBlock2:
                assert isinstance(self.wip, DrawingItemBlock)
                norm_rect = self._normMinRect(self.mouse_press_prev.logical, self._snap(self.mouse.current.logical))
                self.wip.setOffset(norm_rect.topLeft())
                self.wip.setSize(norm_rect.size())
                self.contents.append(self.wip)
                self.wip = None
                self.state = self.State.Idle
                self._viewUpdate()

    def mouseMiddlePress(self : 'Drawing', physical: QPoint, modifiers: Qt.KeyboardModifier) -> None:
        self.mouse.middle.press.physical = physical
        self.mouse.middle.press.logical = self._cp2dp(physical)
        self.mouse.middle.release.physical = None
        self.mouse.middle.release.logical = None
        self.mouse.middle.state = self.MouseState.Pressed

    def mouseMiddleRelease(self : 'Drawing', physical: QPoint) -> None:
        self.mouse.middle.release.physical = physical
        self.mouse.middle.release.logical = self._cp2dp(physical)
        if self.state == self.State.ViewZoomWindow2:
            self.sel_rect = self._normMinRect(self.mouse.middle.press.physical, self.mouse.middle.release.physical)
            self._zoomCRect(self.sel_rect)
            self.sel_rect = None
            self.state = self.State.Idle
        else:
            self._pan(self.mouse.middle.release.logical)
        self.mouse.middle.state = self.MouseState.Idle

    def mouseLeftDoubleClick(self : 'Drawing', modifiers: Qt.KeyboardModifier) -> None:
        match self.state:
            case self.State.PlaceBlock2:
                assert isinstance(self.wip, DrawingItemBlock)
                self.contents.append(self.wip)
                self.wip = None
                self.state = self.State.Idle
                self._viewUpdate()

    def mouseWheel(self : 'Drawing', n: int, modifiers: Qt.KeyboardModifier) -> None:
        if modifiers == Qt.KeyboardModifier.NoModifier:
            if n >= 0:
                self.viewZoomIn(n)
            else:
                self.viewZoomOut(-n)
