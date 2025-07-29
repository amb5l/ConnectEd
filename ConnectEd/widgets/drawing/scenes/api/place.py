__all__ = ["DrawingSceneApiPlaceMixin"]

from typing import Any, Optional, Type, TypeVar

from PyQt6.QtCore    import QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsItem

from .....core import logger

from ... import SignalDirection, VectorRange, EdgeLoc, \
                Port,      cmdPlacePort, \
                Block,     cmdPlaceBlock, \
                BlockPin,  cmdPlaceBlockPin, \
                Rectangle, cmdPlaceRectangle, \
                TextBlock, cmdPlaceTextBlock, \
                Text,      cmdPlaceText

from ...items.port_pin import BlockPin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


T = TypeVar("T", bound=QGraphicsItem)

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

    def placeRectangle(
        self : "DrawingScene",
        *,
        p1   : Optional[QPointF] = None,
        p2   : Optional[QPointF] = None,
        inst : Optional[Rectangle] = None
    ) -> Rectangle:
        element = Rectangle.createOrUpdate(p1=p1, p2=p2, inst=inst)
        self.undo_stack.push(cmdPlaceRectangle(self, element))
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
