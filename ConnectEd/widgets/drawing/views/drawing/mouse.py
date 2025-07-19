from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui  import QEnterEvent, QMouseEvent, QWheelEvent, QCursor

from .....core import logger

from ... import ElementMixin, KeyPoint

from .defs import DrawingViewMouseButtonState as MouseButtonState, \
                  DrawingViewState as State

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
            case MouseButtonState.Pressed:
                d = self._distance(self.mouse.left.press.physical, event.pos())
                if d >= hub.settings.get("prefs/mouse/drag"):
                    self.mouse.left.state = MouseButtonState.Dragging
                    self.mouseLeftDragBegin()
                    return
            case MouseButtonState.Dragging:
                self.mouseLeftDragContinue()
                return
        match self.mouse.middle.state:
            case MouseButtonState.Pressed:
                d = self._distance(self.mouse.middle.press.physical, event.pos())
                if d >= hub.settings.get("prefs/mouse/drag"):
                    self.mouse.middle.state = MouseButtonState.Dragging
                    self.mouseMiddleDragBegin()
                    return
            case MouseButtonState.Dragging:
                self.mouseMiddleDragContinue()
                return
        self.mouseMove()

    def mousePressEvent(self : "DrawingView", event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p); m = self._getModifiers(event)
        if (event.buttons() & Qt.MouseButton.RightButton) \
        or (event.buttons() & Qt.MouseButton.LeftButton and m == qkm.NoModifier):
            items = self._itemsAt(l)
            if items:
                if not isinstance(items[0], KeyPoint):
                    if not items[0].isSelected():
                        self.scene().clearSelection()
                        items[0].setSelected(True)
            else:
                self.scene().clearSelection()
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.mouse.left.press.setPL(p, l)
            self.mouse.left.press.modifiers = m
            self.mouse.left.state = MouseButtonState.Pressed
        if event.buttons() & Qt.MouseButton.MiddleButton:
            self.mouse.middle.press.setPL(p, l)
            self.mouse.middle.press.modifiers = m
            self.mouse.middle.state = MouseButtonState.Pressed

    def mouseReleaseEvent(self : "DrawingView", event : QMouseEvent) -> None:
        p = event.pos(); l = self.mapToScene(p)
        if event.button() & Qt.MouseButton.LeftButton:
            self.mouse.left.release.setPL(p, l)
            match self.mouse.left.state:
                case MouseButtonState.Pressed:
                    self.mouseLeftClick()
                    self.mouse.left.state = MouseButtonState.Idle
                case MouseButtonState.Dragging:
                    self.mouseLeftDragEnd()
                    self.mouse.left.state = MouseButtonState.Idle
                case _:
                    logger.warning(f"Mouse left button released when idle")
        if event.button() & Qt.MouseButton.MiddleButton:
            self.mouse.middle.release.setPL(p, l)
            match self.mouse.middle.state:
                case MouseButtonState.Pressed:
                    self.mouseMiddleClick()
                    self.mouse.middle.state = MouseButtonState.Idle
                case MouseButtonState.Dragging:
                    self.mouseMiddleDragEnd()
                    self.mouse.middle.state = MouseButtonState.Idle
                case _:
                    logger.warning(f"Mouse middle button released when idle")

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
            case State.Idle:
                m = self.mouse.left.press.modifiers
                items = self._itemsAt(self.mouse.left.press.logical)
                for item in items:
                    if isinstance(item, KeyPoint):
                        return
                if m == qkm.NoModifier:
                    if not items or not items[0].isSelected():
                        self.scene().clearSelection()
                self._selectPoint(
                    self.mouse.current.logical,
                    m & qkm.ControlModifier,
                    m & qkm.AltModifier
                )
            case State.EditPaste:
                self.editPasteComplete()
            case State.EditDuplicate1:
                self._selectPoint(
                    self.mouse.current.logical,
                    m == qkm.ControlModifier
                )
                items = self.scene().selectedItems()
                if items:
                    elements = \
                        [item for item in items if isinstance(item, ElementMixin)]
                    if elements:
                        self.editDuplicate()
            case State.EditDuplicate2:
                self.editDuplicateComplete()
            case State.EditMove1 | State.EditSlide1:
                self._selectPoint(
                    self.mouse.current.logical,
                    m == qkm.ControlModifier,
                    self.state == State.EditSlide1
                )
                self.editMoveBegin(
                    self.scene().selectedItems(),
                    self._snap(self.mouse.left.release.logical)
                )
                self._goState(
                    State.EditSlide2 if self.state == State.EditSlide1
                    else State.EditMove2
                )
            case State.EditMove2 | State.EditSlide2:
                self.editMoveComplete(
                    self._snap(self.mouse.left.release.logical),
                    self.state == State.EditSlide2
                )
                self._goState(State.Idle)
            case State.EditResize1:
                self._selectPoint(
                    self.mouse.current.logical,
                    m == qkm.ControlModifier
                )
                if len(self.scene().selectedItems()) == 1:
                    self._goState(State.EditResize2)
            case State.EditResize2:
                items = self._itemsAt(self.mouse.left.press.logical)
                for item in items:
                    if isinstance(item, KeyPoint) and item.isMoveable():
                        self.editMoveBegin(
                            [item], self._snap(self.mouse.left.press.logical)
                        )
                        self._goState(State.EditResize3)
            case State.EditResize3:
                self.editMoveComplete(
                    self._snap(self.mouse.left.release.logical)
                )
                self._goState(State.Idle)
            case State.EditAppearance1:
                self._selectPoint(
                    self.mouse.current.logical,
                    m == qkm.ControlModifier
                )
                self.editAppearance()
            case State.ViewPan1:
                self.wip.pos0 = self.mouse.left.release.physical
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self._goState(State.ViewPan2)
            case State.ViewPan2:
                delta = self.mouse.left.release.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.clear()
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self._goState(State.Idle)
            case State.ViewZoomWindow1:
                self.marquee.begin(self.mouse.left.release.physical)
                self._goState(State.ViewZoomWindow2)
            case State.ViewZoomWindow2:
                self.marquee.end(self.mouse.left.release.physical)
                self._zoomRect(self.marquee.rect())
                self._goState(State.Idle)
            case State.PlaceBlock1:
                self.placeBlockBegin(
                    self._snap(self.mouse.left.release.logical)
                )
            case State.PlaceBlock2:
                self.placeBlockComplete(
                    self._snap(self.mouse.left.release.logical)
                )
            case State.PlaceBlockPin1:
                self._selectPoint(
                    self.mouse.current.logical,
                    m & qkm.ControlModifier,
                    m & qkm.AltModifier
                )
                self.placeBlockPinBegin()
            case State.PlaceBlockPin3:
                self.placeBlockPinComplete(
                    self._snap(self.mouse.left.release.logical)
                )
            case State.PlaceRectangle1:
                self.placeRectangleBegin(
                    self._snap(self.mouse.left.release.logical)
                )
            case State.PlaceRectangle2:
                self.placeRectangleComplete(
                    self._snap(self.mouse.left.release.logical)
                )
            case State.PlaceTextBlock1:
                self.placeTextBlockBegin(
                    self._snap(self.mouse.left.release.logical)
                )
            case State.PlaceTextBlock2:
                self.placeTextBlockComplete()
            case State.PlaceText:
                self.placeTextComplete(
                    self._snap(self.mouse.left.release.logical)
                )

    def mouseLeftDragBegin(self : "DrawingView") -> None:
        match self.state:
            case State.Idle:
                items_at = self._itemsAt(self.mouse.left.press.logical)
                keypoints_at = [item for item in items_at if isinstance(item, KeyPoint)]
                # keypoint dragging
                if len(keypoints_at) == 1:
                    keypoint = keypoints_at[0]
                    self.editMoveBegin([keypoint], keypoint.scenePos())
                    self._goState(State.EditResize3)
                    return
                m = self.mouse.left.press.modifiers
                items = self.scene().selectedItems()
                # Check for CTRL+drag duplication when starting on an element
                if (m & qkm.ControlModifier) and items_at:
                    # Add element under cursor to selection if not already selected
                    elements_at = \
                        [item for item in items_at if isinstance(item, ElementMixin)]
                    if elements_at:
                        element = elements_at[0]  # Get first element under cursor
                        if not element.isSelected():
                            element.setSelected(True)
                        # Get all currently selected elements for duplication
                        items = self.scene().selectedItems()
                        elements = \
                            [item for item in items if isinstance(item, ElementMixin)]
                        if elements:
                            # Pass the press position for CTRL+drag duplication
                            pos = self._snap(self.mouse.left.press.logical)
                            self.editDuplicate(pos)
                            return
                if not items_at \
                    and not (m & (qkm.ControlModifier | qkm.ShiftModifier)):
                    self.scene().clearSelection()
                    items = []
                self._selectPoint(
                    self.mouse.left.press.logical,
                    m & qkm.ControlModifier
                )
                if items: # slide/move
                    self.editMoveBegin(
                        items,
                        self._snap(self.mouse.left.press.logical),
                        not(m & qkm.AltModifier)
                    )
                    self._goState(
                        State.EditSlide2 if not(m & qkm.AltModifier)
                        else State.EditMove2
                    )
                else: # start marquee selection
                    self.marquee.begin(self.mouse.left.press.physical)
                    self._goState(State.SelectArea2)
            case State.EditAppearance1:
                self.marquee.begin(self.mouse.left.press.physical)
                self._goState(State.SelectArea2)
            case State.EditDuplicate1:
                self.marquee.begin(self.mouse.left.press.physical)
                self._goState(State.SelectArea2)
            case State.ViewZoomWindow1:
                self.marquee.begin(self.mouse.left.press.physical)
                self._goState(State.ViewZoomWindow2)
            case State.PlaceBlock1:
                self.placeBlockBegin(
                    self._snap(self.mouse.left.press.logical)
                )
            case State.PlaceRectangle1:
                self.placeRectangleBegin(
                    self._snap(self.mouse.left.press.logical)
                )

    def mouseLeftDragContinue(self : "DrawingView") -> None:
        match self.state:
            case State.SelectArea2:
                self.marquee.resize(self.mouse.current.physical)
            case State.EditSlide2:
                self.editMoveContinue(
                    self._snap(self.mouse.current.logical), True
                )
            case State.EditDuplicate2:
                self.editDuplicateContinue()
            case State.EditMove2:
                self.editMoveContinue(
                    self._snap(self.mouse.current.logical)
                )
            case State.EditResize3:
                self.editMoveContinue(self._snap(self.mouse.current.logical))
            case State.ViewPan2:
                delta = self.mouse.current.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.pos0 = self.mouse.current.physical
            case State.ViewZoomWindow2:
                self.marquee.resize(self.mouse.current.physical)
            case State.PlaceBlock2:
                self.placeBlockContinue(
                    self._snap(self.mouse.current.logical)
                )
            case State.PlaceRectangle2:
                self.placeRectangleContinue(
                    self._snap(self.mouse.current.logical)
                )

    def mouseLeftDragEnd(self : "DrawingView") -> None:
        m = self.mouse.left.press.modifiers
        match self.state:
            case State.SelectArea2:
                self.marquee.end(self.mouse.left.release.physical)
                self._selectRect(
                    self.marquee.rect(),
                    m == qkm.ControlModifier
                )
                self._goState(State.Idle)
            case State.EditMove2 | State.EditSlide2 | State.EditResize3:
                self.editMoveComplete(
                    self._snap(self.mouse.left.release.logical),
                    self.state == State.EditSlide2
                )
                self._goState(State.Idle)
            case State.EditDuplicate2:
                self.editDuplicateComplete()
            case State.EditAppearance1:
                self.marquee.end(self.mouse.left.release.physical)
                self._selectRect(
                    self.marquee.rect(),
                    m == qkm.ControlModifier
                )
                self.editAppearance()
            case State.ViewZoomWindow2:
                self.marquee.end(self.mouse.left.release.physical)
                self._zoomRect(self.marquee.rect())
                self._goState(State.Idle)
            case State.ViewPan2:
                delta = self.mouse.left.release.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.clear()
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self._goState(State.Idle)
            case State.PlaceBlock2:
                self.placeBlockComplete(
                    self._snap(self.mouse.left.release.logical)
                )
            case State.PlaceRectangle2:
                self.placeRectangleComplete(
                    self._snap(self.mouse.left.release.logical)
                )

    def mouseMiddleClick(self : "DrawingView") -> None:
        pass

    def mouseMiddleDragBegin(self : "DrawingView") -> None:
        if self.state == State.Idle:
            match self.mouse.middle.press.modifiers:
                case Qt.KeyboardModifier.NoModifier:
                    self.wip.pos0 = self.mouse.current.physical
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                    self._goState(State.ViewPan2)
                case Qt.KeyboardModifier.ControlModifier:
                    self.marquee.begin(self.mouse.middle.press.physical)
                    self._goState(State.ViewZoomWindow2)

    def mouseMiddleDragContinue(self : "DrawingView") -> None:
        match self.state:
            case State.ViewPan2:
                delta = self.mouse.current.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.pos0 = self.mouse.current.physical
            case State.ViewZoomWindow2:
                self.marquee.resize(self.mouse.current.physical)

    def mouseMiddleDragEnd(self : "DrawingView") -> None:
        match self.state:
            case State.ViewPan2:
                delta = self.mouse.middle.release.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(
                    self.horizontalScrollBar().value() - delta.x()
                )
                self.verticalScrollBar().setValue(
                    self.verticalScrollBar().value() - delta.y()
                )
                self.wip.clear()
                self.setCursor(Qt.CursorShape.ArrowCursor)
                self._goState(State.Idle)
            case State.ViewZoomWindow2:
                self.marquee.end(self.mouse.middle.release.physical)
                self._zoomRect(self.marquee.rect())
                self._goState(State.Idle)

    def mouseMove(self : "DrawingView") -> None:
        match self.state:
            case State.EditPaste:
                self.editPasteContinue()
            case State.EditDuplicate2:
                self.editDuplicateContinue()
            case State.EditMove2 | State.EditSlide2 | State.EditResize3:
                self.editMoveContinue(
                    self._snap(self.mouse.current.logical),
                    self.state == State.EditSlide2
                )
            case State.ViewPan2:
                delta = self.mouse.current.physical - self.wip.pos0
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.wip.pos0 = self.mouse.current.physical
            case State.ViewZoomWindow2:
                self.marquee.resize(self.mouse.current.physical)
            case State.PlaceBlock2:
                self.placeBlockContinue(
                    self._snap(self.mouse.current.logical)
                )
            case State.PlaceBlockPin3:
                self.placeBlockPinContinue(
                    self._snap(self.mouse.current.logical)
                )
            case State.PlaceRectangle2:
                self.placeRectangleContinue(
                    self._snap(self.mouse.current.logical)
                )
            case State.PlaceText:
                self.placeTextContinue(
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