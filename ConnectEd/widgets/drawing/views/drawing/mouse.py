from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui  import QEnterEvent, QMouseEvent, QWheelEvent, QCursor

from .....core import logger

from ... import KeyPoint

from ..... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingView

qkm = Qt.KeyboardModifier

class DrawingViewMouseMixin:
    def enterEvent(self : "DrawingView", event : QEnterEvent) -> None:
        p = self.mapFromGlobal(QCursor.pos())
        l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        hub.main_window.status_bar.xy.setText(
            str(int(round(l.x()))) + "," + str(int(round(l.y())))
        )

    def leaveEvent(self : "DrawingView", _ : QEvent) -> None:
        rect = self.viewport().rect()
        p = QPoint(rect.width() // 2, rect.height() // 2)
        l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        hub.main_window.status_bar.xy.setText("-,-")

    def mouseMoveEvent(self : "DrawingView", event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        hub.main_window.status_bar.xy.setText(
            str(int(round(l.x()))) + "," + str(int(round(l.y())))
        )
        match self.mouse.left.state:
            case self.MouseButtonState.Pressed:
                d = self._distance(self.mouse.left.press.physical, event.pos())
                if d >= hub.settings.get("prefs/mouse/drag"):
                    self.mouse.left.state = self.MouseButtonState.Dragging
                    self.mouseLeftDragBegin()
                    return
            case self.MouseButtonState.Dragging:
                self.mouseLeftDragContinue()
                return
        match self.mouse.middle.state:
            case self.MouseButtonState.Pressed:
                d = self._distance(self.mouse.middle.press.physical, event.pos())
                if d >= hub.settings.get("prefs/mouse/drag"):
                    self.mouse.middle.state = self.MouseButtonState.Dragging
                    self.mouseMiddleDragBegin()
                    return
            case self.MouseButtonState.Dragging:
                self.mouseMiddleDragContinue()
                return
        self.mouseMove()

    def mousePressEvent(self : "DrawingView", event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p)
        items = self.scene().items(
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

    def mouseReleaseEvent(self : "DrawingView", event : QMouseEvent) -> None:
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
                    logger.warning(f"Mouse left button released when idle")
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
                    logger.warning(f"Mouse middle button released when idle")

    def mouseDoubleClickEvent(self : "DrawingView", event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p)
        self.mouse.left.double.setPL(p, l)
        self.mouse.left.double.modifiers = self._getModifiers(event)
        if event.button() & Qt.MouseButton.LeftButton:
            self.mouseLeftDoubleClick()
        if event.button() & Qt.MouseButton.MiddleButton:
            self.mouseMiddleDoubleClick()

    def wheelEvent(self : "DrawingView", event : QWheelEvent) -> None:
        p = event.position().toPoint(); l = self.mapToScene(p)
        self.mouse.current.setPL(p, l)
        self.mouseWheel(
            event.angleDelta().y() / hub.settings.get("prefs/mouse/wheel"),
            self._getModifiers(event)
        )

    ############################################################################
    # intermediate mouse methods

    def mouseLeftClick(self : "DrawingView") -> None:
        m = self.mouse.left.press.modifiers
        match self.state:
            case self.State.Idle:
                m = self.mouse.left.press.modifiers
                items = self._itemsAt(self.mouse.left.press.logical)
                for item in items:
                    if isinstance(item, KeyPoint):
                        return
                if m == qkm.NoModifier:
                    self.scene().clearSelection()
                self._selectPoint(
                    self.mouse.current.logical,
                    m & qkm.ControlModifier,
                    m & qkm.AltModifier
                )
            case self.State.ViewPan1:
                self.wip.pos0 = self.mouse.left.release.physical
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self._goState(self.State.ViewPan2)
            case self.State.ViewPan2:
                delta = self.mouse.left.release.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.clear()
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self._goState(self.State.Idle)
            case self.State.ViewZoomWindow1:
                self.marquee.begin(self.mouse.left.release.physical)
                self._goState(self.State.ViewZoomWindow2)
            case self.State.ViewZoomWindow2:
                self.marquee.end(self.mouse.left.release.physical)
                self._zoomRect(self.marquee.rect())
                self._goState(self.State.Idle)
            case self.State.EditMove1 | self.State.EditSlide1:
                self._selectPoint(
                    self.mouse.current.logical,
                    m == qkm.ControlModifier,
                    self.state == self.State.EditSlide1
                )
                self.moveBegin(
                    self.scene().selectedItems(),
                    self._snap(self.mouse.left.release.logical)
                )
                self._goState(
                    self.state.EditSlide2 if self.state == self.state.EditSlide1
                    else self.state.EditMove2
                )
            case self.State.EditMove2 | self.State.EditSlide2:
                self.moveComplete(
                    self._snap(self.mouse.left.release.logical),
                    self.state == self.State.EditSlide2
                )
                self._goState(self.State.Idle)
            case self.State.EditResize1:
                self._selectPoint(
                    self.mouse.current.logical,
                    m == qkm.ControlModifier
                )
                if len(self.scene().selectedItems()) == 1:
                    self._goState(self.State.EditResize2)
            case self.State.EditResize2:
                items = self._itemsAt(self.mouse.left.press.logical)
                for item in items:
                    if isinstance(item, KeyPoint) and item.isMoveable():
                        self.moveBegin(
                            [item], self._snap(self.mouse.left.press.logical)
                        )
                        self._goState(self.State.EditResize3)
            case self.State.EditResize3:
                self.moveComplete(
                    self._snap(self.mouse.left.release.logical)
                )
                self._goState(self.State.Idle)
            case self.State.PlaceRectangle1:
                self.placeRectangleBegin(
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.PlaceRectangle2:
                self.placeRectangleComplete(
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.PlaceTextBlock1:
                self.placeTextBlockBegin(
                    self._snap(self.mouse.left.release.logical)
                )
            case self.State.PlaceTextBlock2:
                self.placeTextBlockComplete()

    def mouseLeftDragBegin(self : "DrawingView") -> None:
        match self.state:
            case self.State.Idle:
                m = self.mouse.left.press.modifiers
                items = self._itemsAt(self.mouse.left.press.logical)
                for item in items:
                    if isinstance(item, KeyPoint) and item.isMoveable():
                        self.moveBegin(
                            [item], self._snap(self.mouse.left.press.logical)
                        )
                        self._goState(self.state.EditResize3)
                        return
                if not (m & (qkm.ControlModifier | qkm.ShiftModifier)):
                    self.scene().clearSelection()
                self._selectPoint(
                    self.mouse.left.press.logical,
                    m & qkm.ControlModifier
                )
                items = self.scene().selectedItems()
                if len(items): # slide/move
                    self.moveBegin(
                        items,
                        self._snap(self.mouse.left.press.logical),
                        not(m & qkm.AltModifier)
                    )
                    self._goState(
                        self.state.EditSlide2 if not(m & qkm.AltModifier)
                        else self.state.EditMove2
                    )
                else: # start marquee selection
                    self.marquee.begin(self.mouse.left.press.physical)
                    self._goState(self.State.SelectArea2)
            case self.State.ViewZoomWindow1:
                self.marquee.begin(self.mouse.left.press.physical)
                self._goState(self.State.ViewZoomWindow2)
            case self.State.PlaceRectangle1:
                self.placeRectangleBegin(
                    self._snap(self.mouse.left.press.logical)
                )

    def mouseLeftDragContinue(self : "DrawingView") -> None:
        match self.state:
            case self.State.SelectArea2:
                self.marquee.resize(self.mouse.current.physical)
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.pos0 = self.mouse.current.physical
            case self.State.ViewZoomWindow2:
                self.marquee.resize(self.mouse.current.physical)
            case self.State.EditSlide2:
                self.moveContinue(
                    self._snap(self.mouse.current.logical), True
                )
            case self.State.EditMove2:
                self.moveContinue(
                    self._snap(self.mouse.current.logical)
                )
            case self.State.EditResize3:
                self.moveContinue(self._snap(self.mouse.current.logical))
            case self.State.PlaceRectangle2:
                self.placeRectangleContinue(
                    self._snap(self.mouse.current.logical)
                )

    def mouseLeftDragEnd(self : "DrawingView") -> None:
        m = self.mouse.left.press.modifiers
        match self.state:
            case self.State.SelectArea2:
                self.marquee.end(self.mouse.left.release.physical)
                self._selectRect(
                    self.marquee.rect(),
                    m == qkm.ControlModifier
                )
                self._goState(self.State.Idle)
            case self.State.ViewZoomWindow2:
                self.marquee.end(self.mouse.left.release.physical)
                self._zoomRect(self.marquee.rect())
                self._goState(self.State.Idle)
            case self.State.ViewPan2:
                delta = self.mouse.left.release.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.clear()
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self._goState(self.State.Idle)
            case self.State.EditMove2 | self.State.EditSlide2 | self.State.EditResize3:
                self.moveComplete(
                    self._snap(self.mouse.left.release.logical),
                    self.state == self.State.EditSlide2
                )
                self._goState(self.State.Idle)
            case self.State.PlaceRectangle2:
                self.placeRectangleComplete(
                    self._snap(self.mouse.left.release.logical)
                )

    def mouseLeftDoubleClick(self : "DrawingView") -> None:
        pass

    def mouseMiddleClick(self : "DrawingView") -> None:
        pass

    def mouseMiddleDragBegin(self : "DrawingView") -> None:
        if self.state == self.State.Idle:
            match self.mouse.middle.press.modifiers:
                case Qt.KeyboardModifier.NoModifier:
                    self.wip.pos0 = self.mouse.current.physical
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    self._goState(self.State.ViewPan2)
                case Qt.KeyboardModifier.ControlModifier:
                    self.marquee.begin(self.mouse.middle.press.physical)
                    self._goState(self.State.ViewZoomWindow2)

    def mouseMiddleDragContinue(self : "DrawingView") -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.pos0 = self.mouse.current.physical
            case self.State.ViewZoomWindow2:
                self.marquee.resize(self.mouse.current.physical)

    def mouseMiddleDragEnd(self : "DrawingView") -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.middle.release.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.clear()
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self._goState(self.State.Idle)
            case self.State.ViewZoomWindow2:
                self.marquee.end(self.mouse.middle.release.physical)
                self._zoomRect(self.marquee.rect())
                self._goState(self.State.Idle)

    def mouseMiddleDoubleClick(self : "DrawingView") -> None:
        pass

    def mouseMove(self : "DrawingView") -> None:
        match self.state:
            case self.State.ViewPan2:
                delta = self.mouse.current.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.wip.pos0 = self.mouse.current.physical
            case self.State.ViewZoomWindow2:
                self.marquee.resize(self.mouse.current.physical)
            case self.State.EditMove2 | self.State.EditSlide2 | self.State.EditResize3:
                self.moveContinue(
                    self._snap(self.mouse.current.logical),
                    self.state == self.State.EditSlide2
                )
            case self.State.PlaceRectangle2:
                self.placeRectangleContinue(
                    self._snap(self.mouse.current.logical)
                )

    def mouseWheel(self : "DrawingView", n: int, modifiers: Qt.KeyboardModifier) -> None:
        match modifiers:
            case Qt.KeyboardModifier.NoModifier:      # pan up/down
                self.viewPanUp(n) if n >= 0 else self.viewPanDown(-n)
            case Qt.KeyboardModifier.ShiftModifier:   # pan left/right
                self.viewPanLeft(n) if n >= 0 else self.viewPanRight(-n)
            case Qt.KeyboardModifier.ControlModifier: # zoom in/out
                self.viewZoomIn(n) if n >= 0 else self.viewZoomOut(-n)