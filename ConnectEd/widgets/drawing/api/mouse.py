from PyQt6.QtCore import Qt

from ...items import Rectangle, Grip

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import Drawing

qkm = Qt.KeyboardModifier

class DrawingApiMouseMixin:
    """Mixin class that provides mouse API for Drawing widgets."""

    def mouseLeftClick(self : 'Drawing') -> None:
        m = self.mouse.left.press.modifiers
        match self.state:
            case self.State.Idle:
                m = self.mouse.left.press.modifiers
                items = self._itemsAt(self.mouse.left.press.logical)
                for item in items:
                    if isinstance(item, Grip):
                        self.grip = item
                        print('grip')
                        break
                else:
                    self.grip = None
                if m == qkm.NoModifier and not self.grip:
                    self.scene.clearSelection()
                self._selectPoint(
                    self.mouse.current.logical,
                    m & qkm.ControlModifier,
                    m & qkm.AltModifier
                )
            case self.State.ViewPan1:
                self.prev_pos = self.mouse.left.release.physical
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.state = self.State.ViewPan2
            case self.State.ViewPan2:
                delta = self.mouse.left.release.physical - self.prev_pos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.prev_pos = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self.state = self.State.Idle
            case self.State.ViewZoomWindow1:
                self.marquis.begin(self.mouse.left.release.physical)
                self.state = self.State.ViewZoomWindow2
            case self.State.ViewZoomWindow2:
                self.marquis.end(self.mouse.left.release.physical)
                self._zoomRect(self.marquis.rect())
                self.state = self.State.Idle
            case self.State.EditSlide1:
                self._selectPoint(
                    self.mouse.current.logical,
                    m == qkm.ControlModifier
                )
                self.prev_pos = self._snap(self.mouse.left.release.logical)
                self.state = self.State.EditSlide2
            case self.State.EditSlide2:
                # TODO: DRY, stretch connections
                pos = self._snap(self.mouse.left.release.logical)
                for item in self.scene.selectedItems():
                    item.moveBy(
                        pos.x() - self.prev_pos.x(),
                        pos.y() - self.prev_pos.y()
                    )
                self.state = self.State.Idle
            case self.State.EditMove1:
                self._selectPoint(
                    self.mouse.current.logical,
                    m == qkm.ControlModifier
                )
                self.prev_pos = self._snap(self.mouse.left.release.logical)
                self.state = self.State.EditMove2
            case self.State.EditMove2:
                # TODO: DRY
                pos = self._snap(self.mouse.left.release.logical)
                for item in self.scene.selectedItems():
                    item.moveBy(
                        pos.x() - self.prev_pos.x(),
                        pos.y() - self.prev_pos.y()
                    )
                self.state = self.State.Idle
            case self.State.PlaceRectangle1:
                self._addWIP(Rectangle(
                    self._snap(self.mouse.left.release.logical)
                ))
                self.state = self.State.PlaceRectangle2
            case self.State.PlaceRectangle2:
                self.wip.setPoints(
                    self.prev_pos,
                    self._snap(self.mouse.left.release.logical)
                )
                self._completeWIP()
                self.state = self.State.Idle

    def mouseLeftDragBegin(self : 'Drawing') -> None:
        match self.state:
            case self.State.Idle:
                m = self.mouse.left.press.modifiers
                items = self._itemsAt(self.mouse.left.press.logical)
                for item in items:
                    if isinstance(item, Grip):
                        self.grip = item
                        break
                else:
                    self.grip = None
                if self.grip: # we've hit a grip
                    print('grip resize')
                    self.prev_pos = self.grip.parentPos()
                    self.state = self.State.EditResize2
                else:
                    if not (m & (qkm.ControlModifier | qkm.ShiftModifier)):
                        self.scene.clearSelection()
                    self._selectPoint(
                        self.mouse.left.press.logical,
                        m & qkm.ControlModifier
                    )
                    if len(self.scene.selectedItems()): # slide/move
                        self.prev_pos = self.mouse.left.press.logical
                        if m & qkm.AltModifier:
                            self.state = self.State.EditMove2
                        else:
                            self.state = self.State.EditSlide2
                    else: # start marquis selection
                        self.marquis.begin(self.mouse.left.press.physical)
                        self.state = self.State.SelectArea2
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
            case self.State.SelectArea2:
                self.marquis.resize(self.mouse.current.physical)
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.prev_pos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.prev_pos = self.mouse.current.physical
            case self.State.ViewZoomWindow2:
                self.marquis.resize(self.mouse.current.physical)
            case self.State.EditSlide2:
                # TODO: stretch connections
                pos = self._snap(self.mouse.current.logical)
                for item in self.scene.selectedItems():
                    item.moveBy(
                        pos.x() - self.prev_pos.x(),
                        pos.y() - self.prev_pos.y()
                    )
                self.prev_pos = pos
            case self.State.EditMove2:
                # TODO: DRY
                pos = self._snap(self.mouse.current.logical)
                for item in self.scene.selectedItems():
                    item.moveBy(
                        pos.x() - self.prev_pos.x(),
                        pos.y() - self.prev_pos.y()
                    )
                self.prev_pos = pos
            case self.State.EditResize2:
                print('resizing')
                self.grip.parentItem().gripResize(
                    self.grip.key_point,
                    self._snap(self.mouse.current.logical) - self.prev_pos
                )
                self.prev_pos = self._snap(self.mouse.current.logical)
            case self.State.PlaceRectangle2:
                self.wip.setPoints(
                    self.prev_pos,
                    self._snap(self.mouse.current.logical)
                )

    def mouseLeftDragEnd(self : 'Drawing') -> None:
        m = self.mouse.left.press.modifiers
        match self.state:
            case self.State.SelectArea2:
                self.marquis.end(self.mouse.left.release.physical)
                self._selectRect(
                    self.marquis.rect(),
                    m == qkm.ControlModifier
                )
            case self.State.ViewZoomWindow2:
                self.marquis.end(self.mouse.left.release.physical)
                self._zoomRect(self.marquis.rect())
            case self.State.EditSlide2:
                # TODO: DRY, stretch connections
                pos = self._snap(self.mouse.left.release.logical)
                for item in self.scene.selectedItems():
                    item.moveBy(
                        pos.x() - self.prev_pos.x(),
                        pos.y() - self.prev_pos.y()
                    )
            case self.State.EditMove2:
                # TODO: DRY
                pos = self._snap(self.mouse.left.release.logical)
                for item in self.scene.selectedItems():
                    item.moveBy(
                        pos.x() - self.prev_pos.x(),
                        pos.y() - self.prev_pos.y()
                    )
            case self.State.PlaceRectangle2:
                self.wip.setPoints(
                    self.prev_pos,
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
                    self.prev_pos = self.mouse.current.physical
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    self.state = self.State.ViewPan2
                case Qt.KeyboardModifier.ControlModifier:
                    self.marquis.begin(self.mouse.middle.press.physical)
                    self.state = self.State.ViewZoomWindow2

    def mouseMiddleDragContinue(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.prev_pos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.prev_pos = self.mouse.current.physical
            case self.State.ViewZoomWindow2:
                self.marquis.resize(self.mouse.current.physical)

    def mouseMiddleDragEnd(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.prev_pos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.prev_pos = None
                self.setCursor(Qt.CursorShape.ArrowCursor)
            case self.State.ViewZoomWindow2:
                self.marquis.end(self.mouse.middle.release.physical)
                self._zoomRect(self.marquis.rect())
        self.state = self.State.Idle

    def mouseMiddleDoubleClick(self : 'Drawing') -> None:
        pass

    def mouseMove(self : 'Drawing') -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.prev_pos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.prev_pos = self.mouse.current.physical
            case self.State.ViewZoomWindow2:
                self.marquis.resize(self.mouse.current.physical)
            case self.State.EditSlide2:
                # TODO: DRY, stretch connections
                pos = self._snap(self.mouse.current.logical)
                for item in self.scene.selectedItems():
                    item.moveBy(
                        pos.x() - self.prev_pos.x(),
                        pos.y() - self.prev_pos.y()
                    )
                self.prev_pos = pos
            case self.State.EditMove2:
                # TODO: DRY
                pos = self._snap(self.mouse.current.logical)
                for item in self.scene.selectedItems():
                    item.moveBy(
                        pos.x() - self.prev_pos.x(),
                        pos.y() - self.prev_pos.y()
                    )
                self.prev_pos = pos
            case self.State.PlaceRectangle2:
                self.wip.setPoints(
                    self.prev_pos,
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
