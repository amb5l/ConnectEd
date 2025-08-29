from typing import Self, Optional

from PyQt6.QtCore import Qt, QPoint, QPointF

from ..... import hub

from .....core.log import logger

from ....dialogs.properties    import PropertiesDialog
from ....dialogs.appearance    import AppearanceDialog
from ....dialogs.text          import TextDialog
from ....dialogs.text_block    import TextBlockDialog
from ....dialogs.property_text import PropertyTextDialog
from ....dialogs.port_pin      import PortPinDialog

from ...items import ElementMixin

from ...items.handle        import Handle
from ...items.pin_rect      import PinRect
from ...items.text          import Text
from ...items.text_block    import TextBlock
from ...items.property_text import PropertyText

from ...scenes.drawing import DrawingScene

from ...scenes.drawing.interaction import *

from ...scenes.drawing.cmd.edit import cmdEditPortPin,     \
                                       cmdEditText,        \
                                       cmdEditPropertyText


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import DrawingView


qkm = Qt.KeyboardModifier

class DrawingViewStateBase:
    # instance attributes
    view  : "DrawingView"
    scene : "DrawingScene"

    def __init__(self : Self, view : "DrawingView") -> None:
        self.view = view
        self.scene = view.scene()

    def go(
        self     : Self,
        state    : "DrawingViewStateBase",
        elements : Optional[list[ElementMixin]] = None
    ) -> None:
        self.view.state = state
        if hub.main_window is not None:
            hub.main_window.status_bar.tip.setText(state.TIP)
        state.entry(
            self.view.mouse.current.physical,
            self.view.mouse.current.logical,
            elements
        )

    def interact(
        self        : Self,
        interaction : Interaction,
        state       : Optional["DrawingViewStateBase"] = None
    ) -> None:
        if interaction.valid:
            self.view.interaction = interaction
            if state is not None:
                self.go(state)
        else:
            self.view.state.go(self.view.stateIdle)

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        pass

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMiddleDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        pass

    def _snap(self : Self, s : QPointF) -> QPointF:
        return self.view._snap(s)

class ClickMixin(DrawingViewStateBase):
    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.interaction.complete(self._snap(s))
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.interaction.update(self._snap(s))

class DragMixin(DrawingViewStateBase):
    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.interaction.update(self._snap(s))

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.interaction.complete(self._snap(s))
        self.view.state.go(self.view.stateIdle)

class DrawingViewStateIdle(DrawingViewStateBase):
    TIP = "Idle"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        self.view.interaction = None

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        items = self.view._itemsAt(s)
        for item in items:
            if isinstance(item, Handle):
                return
        if m == qkm.NoModifier:
            if not items or not items[0].isSelected():
                self.scene.clearSelection()
        self.view._selectPoint(s, m)

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        items_at = self.view._itemsAt(s)
        handles_at = [item for item in items_at if isinstance(item, Handle)]
        if len(handles_at) == 1:
            # handle dragging => resize
            handle = handles_at[0]
            self.interact(
                EditResizeInteraction(self.scene, handle, handle.scenePos()),
                self.view.stateEditResize
            )
            return
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
                elements = self.view._selectedElements(ElementMixin)
                if elements:
                    # Pass the press position for CTRL+drag duplication
                    self.interact(
                        EditDuplicateInteraction(self.scene, elements, self._snap(s)),
                        self.view.stateEditDuplicate
                    )
                    return
        if not items_at \
            and not (m & (qkm.ControlModifier | qkm.ShiftModifier)):
            self.scene.clearSelection()
            items = []
        self.view._selectPoint(s, m)
        items = self.scene.selectedItems()
        if items: # slide/move
            slide = not(m & qkm.AltModifier)
            self.interact(
                EditMoveInteraction(self.scene, items, self._snap(s), slide),
                self.view.stateEditSlide if slide else self.view.stateEditMove
            )
        else: # start marquee selection
            self.view.marquee.begin(v)
            self.view.state.go(self.view.stateEditSelectArea2)

    def mouseMiddleDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        if m == qkm.NoModifier:
            self.view.pan = v
            self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.view.state.go(self.view.stateViewPan2)
        elif m & qkm.ControlModifier:
            self.view.marquee.begin(v)
            self.view.state.go(self.view.stateViewZoomArea2)

class DrawingViewStateViewPan1(DrawingViewStateBase):
    TIP = "Pan: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.pan = v
        self.view.setCursor(Qt.CursorShape.ClosedHandCursor)
        self.view.state.go(self.view.stateViewPan2)

class DrawingViewStateViewPan2(DrawingViewStateBase):
    TIP = "Pan: pick the second point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        delta = v - self.view.pan
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.pan = None
        self.view.setCursor(Qt.CursorShape.ArrowCursor)
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        delta = v - self.view.pan
        self.view.horizontalScrollBar().setValue(
            self.view.horizontalScrollBar().value() - delta.x()
        )
        self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() - delta.y()
        )
        self.view.pan = v

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

    def mouseMiddleDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseMiddleDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

class DrawingViewStateViewZoomArea1(DrawingViewStateBase):
    TIP = "Zoom Window: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.begin(v)
        self.view.state.go(self.view.stateViewZoomArea2)

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

class DrawingViewStateViewZoomArea2(DrawingViewStateBase):
    TIP = "Zoom Window: pick the second point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.end(v)
        self.view._zoomRect(self.view.marquee.rect())
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.resize(v)

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

    def mouseMiddleDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseMiddleDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

class DrawingViewStateEditSelectArea1(DrawingViewStateBase):
    TIP = "Select: pick the first point of the marquee"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.begin(v)
        self.view.state.go(self.view.stateEditSelectArea2)

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

class DrawingViewStateEditSelectArea2(DrawingViewStateBase):
    TIP = "Select: complete the marquee selection"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.end(v)
        self.view._selectRect(self.view.marquee.rect(), m & qkm.ControlModifier)
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.marquee.resize(v)

    def mouseLeftDragCont(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseMove(v, s, m)

    def mouseLeftDragEnd(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

class DrawingViewStateEditPaste(ClickMixin):
    TIP = "Paste: select the paste position"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:        self.view.state.interact(EditPasteInteraction(self.scene, self._snap(s)))

class DrawingViewStateEditDuplicate(ClickMixin, DragMixin):
    TIP = "Duplicate: place the duplicated item(s) as required"

class DrawingViewStateEditSlide(DragMixin):
    TIP = "Slide: position the selected item(s) as required"
    SLIDE = True

class DrawingViewStateEditMove(DrawingViewStateEditSlide):
    TIP = "Move: position the selected item(s) as required"
    SLIDE = False

class DrawingViewStateEditResize(DragMixin):
    TIP = "Resize: position the selected handle as required"

class DrawingViewStateEditAppearance(DrawingViewStateBase):
    TIP = "Appearance: specify changes"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        elements = e or self.view._selectedElements(ElementMixin)
        if elements:
            dialog = AppearanceDialog(elements)
            if dialog.exec():
                self.scene.editAppearance(elements, dialog.getChoice())
        else:
            logger.warning("No elements selected")
        self.view.state.go(self.view.stateIdle)

class DrawingViewStateEditProperties(DrawingViewStateBase):
    TIP = "Properties: specify changes"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        element = e[0] if e else self.view._selectedElement(ElementMixin)
        if element:
            dialog = PropertiesDialog(element)
            if dialog.exec():
                self.scene.editProperties(element, dialog.getChanges())
        else:
            logger.warning("No elements selected")
        self.view.state.go(self.view.stateIdle)

class DrawingViewStateEditQuery(DrawingViewStateBase):
    TIP = "Query: pick an item"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view._selectPoint(s, m)
        self.view.editQuery()

class DrawingViewStateEditPort(DrawingViewStateBase):
    TIP = "Edit Port: specify changes"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        element = e[0] if e else self.view._selectedElement(Port)
        if element:
            dialog = PortPinDialog("Port", element)
            if dialog.exec():
                name = dialog.getName()
                direction = dialog.getDirection()
                range = dialog.getRange()
                self.scene.undo_stack.push(cmdEditPortPin(
                    self.scene, element, name, direction, range
                ))
        else:
            logger.warning("No port selected")
        self.view.state.go(self.view.stateIdle)

class DrawingViewStateEditBlockPin(DrawingViewStateBase):
    TIP = "Edit Block Pin: specify changes"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        element = e[0] if e else self.view._selectedElement(BlockPin)
        if element and isinstance(element, BlockPin):
            dialog = PortPinDialog("Block Pin", element)
            if dialog.exec():
                name = dialog.getName()
                direction = dialog.getDirection()
                range = dialog.getRange()
                self.scene.undo_stack.push(cmdEditPortPin(
                    self.scene, element, name, direction, range
                ))
        else:
            logger.warning("No block pin selected")
        self.view.state.go(self.view.stateIdle)

class DrawingViewStateEditText(DrawingViewStateBase):
    TIP = "Edit Text: specify changes"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        element = e[0] if e else self.view._selectedElement(Text)
        if element and isinstance(element, Text):
            dialog = TextDialog(element)
            if dialog.exec():
                text, appearance = dialog.getChoice()
                self.scene.undo_stack.push(cmdEditText(
                    self.scene, element, text, appearance
                ))
        else:
            logger.warning("No text selected")
        self.view.state.go(self.view.stateIdle)

class DrawingViewStateEditPropertyText(DrawingViewStateBase):
    TIP = "Edit Property Text: specify changes"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        element = e[0] if e else self.view._selectedElement(PropertyText)
        if element and isinstance(element, PropertyText):
            dialog = PropertyTextDialog(element)
            if dialog.exec():
                name = dialog.getName()
                value = dialog.getValue()
                display = dialog.getDisplay()
                appearance = dialog.getAppearanceChange()
                self.scene.undo_stack.push(cmdEditPropertyText(
                    self.scene, element, name, value, display, appearance
                ))
        else:
            logger.warning("No property text selected")
        self.view.state.go(self.view.stateIdle)

class DrawingViewStatePlacePort(ClickMixin):
    TIP = "Place Port: pick a location"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        element = Port(self._snap(s))
        dialog = PortPinDialog("Port", element)
        if dialog.exec():
            element.name = dialog.getName()
            element.direction = dialog.getDirection()
            element.range = dialog.getRange()
            self.interact(
                PlacePortInteraction(self.scene, self._snap(s), element)
            )
        else:
            self.view.state.go(self.view.stateIdle)

class DrawingViewStatePlaceBlock1(DrawingViewStateBase):
    TIP = "Place Block: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceBlockInteraction(self.scene, self._snap(s)),
            self.view.statePlaceBlock2
        )

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

class DrawingViewStatePlaceBlock2(ClickMixin, DragMixin):
    TIP = "Place Block: pick the second point"

class DrawingViewStatePlaceBlockPin(DrawingViewStateBase):
    TIP = "Place Block Pin: pick a location"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        block = e[0] if e else self.view._selectedElement(PinRect)
        if block and isinstance(block, PinRect):
            pin = BlockPin() # don't parent to block yet
            dialog = PortPinDialog("Block Pin", pin)
            if dialog.exec():
                pin.name = dialog.getName()
                pin.direction = dialog.getDirection()
                pin.range = dialog.getRange()
                self.interact(PlaceBlockPinInteraction(
                    self.scene, block, pin, self._snap(s),
                    self.view.grid.pitch if self.view.grid.snap else None
                ))
        else:
            logger.warning("No pin rect selected")
            self.view.state.go(self.view.stateIdle)

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.interaction.complete(
            self._snap(s),
            self.view.grid.pitch if self.view.grid.snap else None
        )
        self.view.state.go(self.view.stateIdle)

    def mouseMove(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.view.interaction.update(
            self._snap(s),
            self.view.grid.pitch if self.view.grid.snap else None
        )

class DrawingViewStatePlaceRectangle1(DrawingViewStateBase):
    TIP = "Place Rectangle: pick the first point"

    def mouseLeftClick(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.interact(
            PlaceRectangleInteraction(self.scene, self._snap(s)),
            self.view.statePlaceRectangle2
        )

    def mouseLeftDragBegin(self : Self, v : QPoint, s : QPointF, m : qkm) -> None:
        self.mouseLeftClick(v, s, m)

class DrawingViewStatePlaceRectangle2(ClickMixin, DragMixin):
    TIP = "Place Rectangle: pick the second point"

class DrawingViewStatePlaceText(ClickMixin):
    TIP = "Place Text: pick a position"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        element = Text(self._snap(s))
        dialog = TextDialog(element)
        if dialog.exec():
            text, appearance = dialog.getChoice()
            element.setText(text)
            element.quill.setPref(appearance)
            self.interact(PlaceTextInteraction(
                self.scene, self._snap(s), element)
            )
        else:
            self.view.state.go(self.view.stateIdle)

class DrawingViewStatePlaceTextBlock(ClickMixin):
    TIP = "Place Text Block: pick a position"

    def entry(
        self : Self,
        v :    QPoint,
        s :    QPointF,
        e :    Optional[list[ElementMixin]] = None
    ) -> None:
        element = TextBlock(self._snap(s))
        dialog = TextBlockDialog(element)
        if dialog.exec():
            text, appearance = dialog.getChoice()
            element.setPlainText(text)
            element.quill.setPref(appearance)
            self.interact(PlaceTextBlockInteraction(
                self.scene, self._snap(s), element)
            )
        else:
            self.view.state.go(self.view.stateIdle)

class DrawingViewStateMixin:
    state                 : DrawingViewStateBase
    stateIdle             : DrawingViewStateIdle
    stateViewPan1         : DrawingViewStateViewPan1
    stateViewPan2         : DrawingViewStateViewPan2
    stateViewZoomArea1    : DrawingViewStateViewZoomArea1
    stateViewZoomArea2    : DrawingViewStateViewZoomArea2
    stateEditSelectArea1  : DrawingViewStateEditSelectArea1
    stateEditSelectArea2  : DrawingViewStateEditSelectArea2
    stateEditPaste        : DrawingViewStateEditPaste
    stateEditDuplicate    : DrawingViewStateEditDuplicate
    stateEditSlide        : DrawingViewStateEditSlide
    stateEditMove         : DrawingViewStateEditMove
    stateEditResize       : DrawingViewStateEditResize
    stateEditAppearance   : DrawingViewStateEditAppearance
    stateEditProperties   : DrawingViewStateEditProperties
    stateEditQuery        : DrawingViewStateEditQuery
    stateEditPort         : DrawingViewStateEditPort
    stateEditBlockPin     : DrawingViewStateEditBlockPin
    stateEditText         : DrawingViewStateEditText
    stateEditPropertyText : DrawingViewStateEditPropertyText
    statePlacePort        : DrawingViewStatePlacePort
    statePlaceBlock1      : DrawingViewStatePlaceBlock1
    statePlaceBlock2      : DrawingViewStatePlaceBlock2
    statePlaceBlockPin    : DrawingViewStatePlaceBlockPin
    statePlaceRectangle1  : DrawingViewStatePlaceRectangle1
    statePlaceRectangle2  : DrawingViewStatePlaceRectangle2
    statePlaceText        : DrawingViewStatePlaceText
    statePlaceTextBlock   : DrawingViewStatePlaceTextBlock

    def initStates(self : "DrawingView") -> None:
        self.stateIdle             = DrawingViewStateIdle             (self)
        self.stateViewPan1         = DrawingViewStateViewPan1         (self)
        self.stateViewPan2         = DrawingViewStateViewPan2         (self)
        self.stateViewZoomArea1    = DrawingViewStateViewZoomArea1    (self)
        self.stateViewZoomArea2    = DrawingViewStateViewZoomArea2    (self)
        self.stateEditSelectArea1  = DrawingViewStateEditSelectArea1  (self)
        self.stateEditSelectArea2  = DrawingViewStateEditSelectArea2  (self)
        self.stateEditPaste        = DrawingViewStateEditPaste        (self)
        self.stateEditDuplicate    = DrawingViewStateEditDuplicate    (self)
        self.stateEditSlide        = DrawingViewStateEditSlide        (self)
        self.stateEditMove         = DrawingViewStateEditMove         (self)
        self.stateEditResize       = DrawingViewStateEditResize       (self)
        self.stateEditAppearance   = DrawingViewStateEditAppearance   (self)
        self.stateEditProperties   = DrawingViewStateEditProperties   (self)
        self.stateEditQuery        = DrawingViewStateEditQuery        (self)
        self.stateEditPort         = DrawingViewStateEditPort         (self)
        self.stateEditBlockPin     = DrawingViewStateEditBlockPin     (self)
        self.stateEditText         = DrawingViewStateEditText         (self)
        self.stateEditPropertyText = DrawingViewStateEditPropertyText (self)
        self.statePlacePort        = DrawingViewStatePlacePort        (self)
        self.statePlaceBlock1      = DrawingViewStatePlaceBlock1      (self)
        self.statePlaceBlock2      = DrawingViewStatePlaceBlock2      (self)
        self.statePlaceBlockPin    = DrawingViewStatePlaceBlockPin    (self)
        self.statePlaceRectangle1  = DrawingViewStatePlaceRectangle1  (self)
        self.statePlaceRectangle2  = DrawingViewStatePlaceRectangle2  (self)
        self.statePlaceText        = DrawingViewStatePlaceText        (self)
        self.statePlaceTextBlock   = DrawingViewStatePlaceTextBlock   (self)
