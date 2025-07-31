from typing import Self

from PyQt6.QtCore import Qt, QPoint, QPointF

from ...items import ElementMixin
from ...items.grip import Grip

from ..... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingView


qkm = Qt.KeyboardModifier

class DrawingViewStateBase:
    view : "DrawingView"

    def __init__(self : Self, view : "DrawingView") -> None:
        self.view = view

    def go(self : Self, state : "DrawingViewStateBase") -> None:
        """Opportunity to tidy up before changing state."""
        if hub.main_window is not None:
            hub.main_window.status_bar.tip.setText(state.TIP)
        self.view.state = state

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,  # view position
        spos      : QPointF, # scene position
        modifiers : Qt.KeyboardModifier
    ) -> None:
        pass

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        pass

    def mouseLeftDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        pass

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        pass

    def mouseMiddleClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        pass

    def mouseMiddleDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        pass

    def mouseMiddleDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        pass

    def mouseMiddleDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        pass

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        pass

class DrawingViewStateIdle(DrawingViewStateBase):
    TIP = "Idle"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        items = self.view._itemsAt(spos)
        for item in items:
            if isinstance(item, Grip):
                return
        if modifiers == qkm.NoModifier:
            if not items or not items[0].isSelected():
                self.view.scene().clearSelection()
        self.view._selectPoint(spos, modifiers)

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        items_at = self.view._itemsAt(spos)
        grips_at = [item for item in items_at if isinstance(item, Grip)]
        if len(grips_at) == 1:
            grip = grips_at[0]
            self.view.editMoveBegin([grip], grip.scenePos())
            self.view.state.go(self.view.stateEditResize3)
            return
        # Check for CTRL+drag duplication when starting on an element
        if (modifiers & qkm.ControlModifier) and items_at:
            # Add element under cursor to selection if not already selected
            elements_at = \
                [item for item in items_at if isinstance(item, ElementMixin)]
            if elements_at:
                element = elements_at[0]  # Get first element under cursor
                if not element.isSelected():
                    element.setSelected(True)
                # Get all currently selected elements for duplication
                items = self.view.scene().selectedItems()
                elements = \
                    [item for item in items if isinstance(item, ElementMixin)]
                if elements:
                    # Pass the press position for CTRL+drag duplication
                    self.view.editDuplicate(self.view._snap(spos))
                    return
        if not items_at \
            and not (modifiers & (qkm.ControlModifier | qkm.ShiftModifier)):
            self.view.scene().clearSelection()
            items = []
        self.view._selectPoint(spos, modifiers)
        items = self.view.scene().selectedItems()
        if items: # slide/move
            self.view.editMoveBegin(
                items,
                self.view._snap(spos),
                not(modifiers & qkm.AltModifier)
            )
            self.view.state.go(
                self.view.stateEditSlide2 if not(modifiers & qkm.AltModifier)
                else self.view.stateEditMove2
            )
        else: # start marquee selection
            self.view.marquee.begin(vpos)
            self.view.state.go(self.view.stateSelectArea2)

    def mouseMiddleDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        if modifiers == qkm.NoModifier:
            self.view.wip.pos = vpos
            self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.view.state.go(self.view.stateViewPan2)
        elif modifiers & qkm.ControlModifier:
            self.view.marquee.begin(vpos)
            self.view.state.go(self.view.stateViewZoomArea2)

class DrawingViewStateViewPan1(DrawingViewStateBase):
    TIP = "Pan: pick the first point"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.wip.pos = vpos
        self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.view.state.go(self.view.stateViewPan2)

class DrawingViewStateViewPan2(DrawingViewStateBase):
    TIP = "Pan: pick the second point"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        delta = vpos - self.view.wip.pos
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.wip.clear()
        self.view.setCursor(Qt.CursorShape.ArrowCursor)
        self.view.state.go(self.view.stateIdle)

    def mouseLeftDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        delta = vpos - self.view.wip.pos
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.wip.pos = vpos

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        delta = vpos - self.view.wip.pos
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.wip.clear()
        self.view.setCursor(Qt.CursorShape.ArrowCursor)
        self.view.state.go(self.view.stateIdle)

    def mouseMiddleDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        delta = vpos - self.view.wip.pos
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.wip.pos = vpos

    def mouseMiddleDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        delta = vpos - self.view.wip.pos
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.wip.clear()
        self.view.setCursor(Qt.CursorShape.ArrowCursor)
        self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        delta = vpos - self.view.wip.pos
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.wip.pos = vpos

class DrawingViewStateViewZoomArea1(DrawingViewStateBase):
    TIP = "Zoom Window: pick the first point"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.begin(vpos)
        self.view.state.go(self.view.stateViewZoomArea2)

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.begin(vpos)
        self.view.state.go(self.view.stateViewZoomArea2)

class DrawingViewStateViewZoomArea2(DrawingViewStateBase):
    TIP = "Zoom Window: pick the second point"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.end(vpos)
        self.view._zoomRect(self.view.marquee.rect())
        self.view.state.go(self.view.stateIdle)

    def mouseLeftDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.resize(vpos)

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.end(vpos)
        self.view._zoomRect(self.view.marquee.rect())
        self.view.state.go(self.view.stateIdle)

    def mouseMiddleDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.resize(vpos)

    def mouseMiddleDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.end(vpos)
        self.view._zoomRect(self.view.marquee.rect())
        self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.resize(vpos)

class DrawingViewStateSelectArea2(DrawingViewStateBase):
    TIP = "Select: complete the marquee selection"

    def mouseLeftDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.resize(vpos)

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.end(vpos)
        self.view._selectRect(self.view.marquee.rect(), modifiers & qkm.ControlModifier)
        self.view.state.go(self.view.stateIdle)

class DrawingViewStateEditPaste(DrawingViewStateBase):
    TIP = "Paste: select the paste position"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editPasteComplete()

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editPasteContinue()

class DrawingViewStateEditDuplicate1(DrawingViewStateBase):
    TIP = "Duplicate: select one or more items"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view._selectPoint(spos, modifiers)
        items = self.view.scene().selectedItems()
        if items:
            elements = \
                [item for item in items if isinstance(item, ElementMixin)]
            if elements:
                self.view.editDuplicate()

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.begin(vpos)
        self.view.state.go(self.view.stateSelectArea2)

class DrawingViewStateEditDuplicate2(DrawingViewStateBase):
    TIP = "Duplicate: place the duplicated item(s) as required"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editDuplicateComplete()

    def mouseLeftDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editDuplicateContinue()

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editDuplicateComplete()

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editDuplicateContinue()

class DrawingViewStateEditSlide1(DrawingViewStateBase):
    TIP = "Slide: select one or more items"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view._selectPoint(spos, modifiers)
        self.view.editMoveBegin(
            self.view.scene().selectedItems(),
            self.view._snap(spos)
        )
        self.view.state.go(self.view.stateEditSlide2)

class DrawingViewStateEditSlide2(DrawingViewStateBase):
    TIP = "Slide: place the selected item(s) as required"

    def mouseLeftDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:

        self.view.editMoveContinue(
            self.view._snap(spos),
            modifiers & qkm.ShiftModifier
        )

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editMoveComplete(
            self.view._snap(spos),
            modifiers & qkm.ShiftModifier
        )
        self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editMoveContinue(
            self.view._snap(spos),
            modifiers & qkm.ShiftModifier
        )

class DrawingViewStateEditMove1(DrawingViewStateBase):
    TIP = "Move: select one or more items"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view._selectPoint(spos, modifiers)
        self.view.editMoveBegin(
            self.view.scene().selectedItems(),
            self.view._snap(spos)
        )
        self.view.state.go(self.view.stateEditMove2)

class DrawingViewStateEditMove2(DrawingViewStateBase):
    TIP = "Move: place the selected item(s) as required"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editMoveComplete(
            self.view._snap(spos),
            modifiers & qkm.ShiftModifier
        )
        self.view.state.go(self.view.stateIdle)

    def mouseLeftDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editMoveContinue(
            self.view._snap(spos),
            modifiers & qkm.ShiftModifier
        )

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editMoveComplete(
            self.view._snap(spos),
            modifiers & qkm.ShiftModifier
        )
        self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editMoveContinue(
            self.view._snap(spos),
            modifiers & qkm.ShiftModifier
        )

class DrawingViewStateEditResize1(DrawingViewStateBase):
    TIP = "Resize: select a single resizeable item"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view._selectPoint(spos, modifiers)
        if len(self.view.scene().selectedItems()) == 1:
            self.view.state.go(self.view.stateEditResize2)

class DrawingViewStateEditResize2(DrawingViewStateBase):
    TIP = "Resize: select a grip to begin resizing"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        items = self.view._itemsAt(spos)
        for item in items:
            if isinstance(item, Grip):
                self.view.editMoveBegin(
                    [item], self.view._snap(spos)
                )
                self.view.state.go(self.view.stateEditResize3)

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editMoveComplete(
            self.view._snap(spos),
            modifiers & qkm.ShiftModifier
        )
        self.view.state.go(self.view.stateIdle)

class DrawingViewStateEditResize3(DrawingViewStateBase):
    TIP = "Resize: place the selected grip as required"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editMoveComplete(
            self.view._snap(spos),
            modifiers & qkm.ShiftModifier
        )
        self.view.state.go(self.view.stateIdle)

    def mouseLeftDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editMoveContinue(self.view._snap(spos), modifiers & qkm.ShiftModifier)

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editMoveComplete(
            self.view._snap(spos),
            modifiers & qkm.ShiftModifier
        )
        self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.editMoveContinue(
            self.view._snap(spos),
            modifiers & qkm.ShiftModifier
        )

class DrawingViewStateEditAppearance1(DrawingViewStateBase):
    TIP = "Appearance: select one or more items"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view._selectPoint(spos, modifiers)
        self.view.editAppearance()

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.begin(spos)
        self.view.state.go(self.view.stateEditAppearance2)

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.marquee.end(vpos)
        self.view._selectRect(self.view.marquee.rect(), modifiers)
        self.view.editAppearance()

class DrawingViewStateEditAppearance2(DrawingViewStateBase):
    TIP = "Appearance: specify changes"

class DrawingViewStateEditQuery(DrawingViewStateBase):
    TIP = "Query: pick an item"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view._selectPoint(spos, modifiers)
        self.view.editQuery()

class DrawingViewStatePlacePort1(DrawingViewStateBase):
    TIP = "Place Port: enter the port details"

class DrawingViewStatePlacePort2(DrawingViewStateBase):
    TIP = "Place Port: pick a location"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placePortComplete(self.view._snap(spos))
        self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placePortContinue(self.view._snap(spos))

class DrawingViewStatePlaceBlock1(DrawingViewStateBase):
    TIP = "Place Block: pick the first point"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeBlockBegin(self.view._snap(spos))
        self.view.state.go(self.view.statePlaceBlock2)

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeBlockBegin(self.view._snap(spos))

class DrawingViewStatePlaceBlock2(DrawingViewStateBase):
    TIP = "Place Block: pick the second point"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeBlockComplete(self.view._snap(spos))
        self.view.state.go(self.view.stateIdle)

    def mouseLeftDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeBlockContinue(self.view._snap(spos))

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeBlockComplete(self.view._snap(spos))

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeBlockContinue(self.view._snap(spos))

class DrawingViewStatePlaceBlockPin1(DrawingViewStateBase):
    TIP = "Place Block Pin: pick a block"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view._selectPoint(spos, modifiers)
        self.placeBlockPinBegin()

class DrawingViewStatePlaceBlockPin2(DrawingViewStateBase):
    TIP = "Place Block Pin: enter the pin details"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeBlockPinComplete(self.view._snap(spos))
        self.view.state.go(self.view.stateIdle)

class DrawingViewStatePlaceBlockPin3(DrawingViewStateBase):
    TIP = "Place Block Pin: pick a location"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeBlockPinComplete(self.view._snap(spos))
        self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeBlockPinContinue(self.view._snap(spos))

class DrawingViewStatePlaceRectangle1(DrawingViewStateBase):
    TIP = "Place Rectangle: pick the first point"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeRectangleBegin(self.view._snap(spos))
        self.view.state.go(self.view.statePlaceRectangle2)

    def mouseLeftDragBegin(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeRectangleBegin(self.view._snap(spos))

class DrawingViewStatePlaceRectangle2(DrawingViewStateBase):
    TIP = "Place Rectangle: pick the second point"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeRectangleComplete(self.view._snap(spos))
        self.view.state.go(self.view.stateIdle)

    def mouseLeftDragContinue(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeRectangleContinue(self.view._snap(spos))

    def mouseLeftDragEnd(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeRectangleComplete(self.view._snap(spos))

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeRectangleContinue(self.view._snap(spos))

class DrawingViewStatePlaceTextBlock1(DrawingViewStateBase):
    TIP = "Place Text Block: pick a position"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeTextBlockBegin(self.view._snap(spos))
        self.view.state.go(self.view.statePlaceTextBlock2)

class DrawingViewStatePlaceTextBlock2(DrawingViewStateBase):
    TIP = "Place Text Block: enter the text"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeTextBlockComplete()
        self.view.state.go(self.view.stateIdle)

class DrawingViewStatePlaceText1(DrawingViewStateBase):
    TIP = "Place Text: enter the text"

class DrawingViewStatePlaceText2(DrawingViewStateBase):
    TIP = "Place Text: pick a position"

    def mouseLeftClick(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeTextComplete(self.view._snap(spos))
        self.view.state.go(self.view.stateIdle)

    def mouseMove(
        self      : Self,
        vpos      : QPoint,
        spos      : QPointF,
        modifiers : Qt.KeyboardModifier
    ) -> None:
        self.view.placeTextContinue(self.view._snap(spos))

class DrawingViewStateMixin:
    state                : DrawingViewStateBase
    stateIdle            : DrawingViewStateIdle
    stateViewPan1        : DrawingViewStateViewPan1
    stateViewPan2        : DrawingViewStateViewPan2
    stateViewZoomArea1   : DrawingViewStateViewZoomArea1
    stateViewZoomArea2   : DrawingViewStateViewZoomArea2
    stateSelectArea2     : DrawingViewStateSelectArea2
    stateEditPaste       : DrawingViewStateEditPaste
    stateEditDuplicate1  : DrawingViewStateEditDuplicate1
    stateEditDuplicate2  : DrawingViewStateEditDuplicate2
    stateEditSlide1      : DrawingViewStateEditSlide1
    stateEditSlide2      : DrawingViewStateEditSlide2
    stateEditMove1       : DrawingViewStateEditMove1
    stateEditMove2       : DrawingViewStateEditMove2
    stateEditResize1     : DrawingViewStateEditResize1
    stateEditResize2     : DrawingViewStateEditResize2
    stateEditResize3     : DrawingViewStateEditResize3
    stateEditAppearance1 : DrawingViewStateEditAppearance1
    stateEditAppearance2 : DrawingViewStateEditAppearance2
    stateEditQuery       : DrawingViewStateEditQuery
    statePlacePort1      : DrawingViewStatePlacePort1
    statePlacePort2      : DrawingViewStatePlacePort2
    statePlaceBlock1     : DrawingViewStatePlaceBlock1
    statePlaceBlock2     : DrawingViewStatePlaceBlock2
    statePlaceBlockPin1  : DrawingViewStatePlaceBlockPin1
    statePlaceBlockPin2  : DrawingViewStatePlaceBlockPin2
    statePlaceBlockPin3  : DrawingViewStatePlaceBlockPin3
    statePlaceRectangle1 : DrawingViewStatePlaceRectangle1
    statePlaceRectangle2 : DrawingViewStatePlaceRectangle2
    statePlaceTextBlock1 : DrawingViewStatePlaceTextBlock1
    statePlaceTextBlock2 : DrawingViewStatePlaceTextBlock2
    statePlaceText1      : DrawingViewStatePlaceText1
    statePlaceText2      : DrawingViewStatePlaceText2

    def initStates(self : "DrawingView") -> None:
        self.stateIdle            = DrawingViewStateIdle            (self)
        self.stateViewPan1        = DrawingViewStateViewPan1        (self)
        self.stateViewPan2        = DrawingViewStateViewPan2        (self)
        self.stateViewZoomArea1   = DrawingViewStateViewZoomArea1   (self)
        self.stateViewZoomArea2   = DrawingViewStateViewZoomArea2   (self)
        self.stateSelectArea2     = DrawingViewStateSelectArea2     (self)
        self.stateEditPaste       = DrawingViewStateEditPaste       (self)
        self.stateEditDuplicate1  = DrawingViewStateEditDuplicate1  (self)
        self.stateEditDuplicate2  = DrawingViewStateEditDuplicate2  (self)
        self.stateEditSlide1      = DrawingViewStateEditSlide1      (self)
        self.stateEditSlide2      = DrawingViewStateEditSlide2      (self)
        self.stateEditMove1       = DrawingViewStateEditMove1       (self)
        self.stateEditMove2       = DrawingViewStateEditMove2       (self)
        self.stateEditResize1     = DrawingViewStateEditResize1     (self)
        self.stateEditResize2     = DrawingViewStateEditResize2     (self)
        self.stateEditResize3     = DrawingViewStateEditResize3     (self)
        self.stateEditAppearance1 = DrawingViewStateEditAppearance1 (self)
        self.stateEditAppearance2 = DrawingViewStateEditAppearance2 (self)
        self.stateEditQuery       = DrawingViewStateEditQuery       (self)
        self.statePlacePort1      = DrawingViewStatePlacePort1      (self)
        self.statePlacePort2      = DrawingViewStatePlacePort2      (self)
        self.statePlaceBlock1     = DrawingViewStatePlaceBlock1     (self)
        self.statePlaceBlock2     = DrawingViewStatePlaceBlock2     (self)
        self.statePlaceBlockPin1  = DrawingViewStatePlaceBlockPin1  (self)
        self.statePlaceBlockPin2  = DrawingViewStatePlaceBlockPin2  (self)
        self.statePlaceBlockPin3  = DrawingViewStatePlaceBlockPin3  (self)
        self.statePlaceRectangle1 = DrawingViewStatePlaceRectangle1 (self)
        self.statePlaceRectangle2 = DrawingViewStatePlaceRectangle2 (self)
        self.statePlaceTextBlock1 = DrawingViewStatePlaceTextBlock1 (self)
        self.statePlaceTextBlock2 = DrawingViewStatePlaceTextBlock2 (self)
        self.statePlaceText1      = DrawingViewStatePlaceText1      (self)
        self.statePlaceText2      = DrawingViewStatePlaceText2      (self)
