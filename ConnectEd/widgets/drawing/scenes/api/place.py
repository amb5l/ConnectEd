__all__ = ["DrawingSceneApiPlaceMixin"]

from typing import Optional, TypeVar

from PyQt6.QtCore    import QPointF
from PyQt6.QtWidgets import QGraphicsItem

from ... import SignalDirection, VectorRange, EdgeLoc, \
                Port,      \
                PinRect,   \
                Block,     \
                BlockPin,  \
                Rectangle, \
                Text,      \
                TextBlock

from .cmd import cmdPlaceElement

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


T = TypeVar("T", bound=QGraphicsItem)

class cmdPlacePort(cmdPlaceElement):
    pass

class cmdPlacePinRect(cmdPlaceElement):
    element : PinRect

class cmdPlaceBlock(cmdPlacePinRect):
    element : Block

class cmdPlaceBlockPin(cmdPlaceElement):
    element : BlockPin

class cmdPlaceRectangle(cmdPlaceElement):
    element : Rectangle

class cmdPlaceText(cmdPlaceElement):
    element : Text

class cmdPlaceTextBlock(cmdPlaceElement):
    element : TextBlock

class DrawingSceneApiPlaceMixin:

    def placePort(
        self      : "DrawingScene",
        *,
        name      : Optional[str]             = None,
        direction : Optional[SignalDirection] = None,
        range     : Optional[VectorRange]     = None,
        pos       : Optional[QPointF]         = None,
        inst      : Optional[Port]            = None
    ) -> Port:
        element = Port.createOrUpdate(
            name      = name,
            direction = direction,
            range     = range,
            pos       = pos,
            inst      = inst
        )
        self.undo_stack.push(cmdPlacePort(self, element))
        return element

    def placeBlock(
        self : "DrawingScene",
        *,
        p1   : Optional[QPointF] = None,
        p2   : Optional[QPointF] = None,
        inst : Optional[Block] = None
    ) -> Block:
        element = Block.createOrUpdate(p1=p1, p2=p2, inst=inst)
        self.undo_stack.push(cmdPlaceBlock(self, element))
        return element

    def placeBlockPin(
        self      : "DrawingScene",
        name      : Optional[str]             = None,
        direction : Optional[SignalDirection] = None,
        range     : Optional[VectorRange]     = None,
        loc       : Optional[EdgeLoc]         = None,
        parent    : Optional[Block]           = None,
        inst      : Optional[BlockPin]        = None
    ) -> BlockPin:
        element = BlockPin.createOrUpdate(
            name      = name,
            direction = direction,
            range     = range,
            loc       = loc,
            parent    = parent,
            inst      = inst
        )
        self.undo_stack.push(cmdPlaceBlockPin(self, element))
        return element

    def placeText(
        self  : "DrawingScene",
        *,
        text  : Optional[str]     = None,
        pos   : Optional[QPointF] = None,
        inst  : Optional[Text]    = None
    ) -> Text:
        element = Text.createOrUpdate(text=text, pos=pos, inst=inst)
        self.undo_stack.push(cmdPlaceText(self, element))
        return element

    def placeTextBlock(
        self  : "DrawingScene",
        *,
        text  : Optional[str]     = None,
        pos   : Optional[QPointF] = None,
        inst  : Optional[TextBlock] = None
    ) -> TextBlock:
        element = TextBlock.createOrUpdate(text=text, pos=pos, inst=inst)
        self.undo_stack.push(cmdPlaceTextBlock(self, element))
        return element
