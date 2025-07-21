__all__ = ["DrawingSceneApiPlaceMixin"]

from typing import Any, Optional, Type, TypeVar

from PyQt6.QtCore    import QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsItem

from .....core import logger

from ... import Port,      cmdPlacePort, \
                Block,     cmdPlaceBlock, \
                Rectangle, cmdPlaceRectangle, \
                TextBlock, cmdPlaceTextBlock, \
                Text,      cmdPlaceText, \
                KP

from ...items.pin import BlockPin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .. import DrawingScene


T = TypeVar("T", bound=QGraphicsItem)

class DrawingSceneApiPlaceMixin:

    def placeElement(
        self  : "DrawingScene",
        etype : Type[T],
        *args : Any,
        inst  : Optional[T] = None
    ) -> T:
        CMD_DICT = {
            "Port"      : cmdPlacePort,
            "Block"     : cmdPlaceBlock,
            "Rectangle" : cmdPlaceRectangle,
            "TextBlock" : cmdPlaceTextBlock,
            "Text"      : cmdPlaceText
        }
        element = etype.createOrUpdate(*args, inst=inst)
        if etype.__name__ in CMD_DICT:
            cmd = CMD_DICT[etype.__name__]
            self.undo_stack.push(cmd(self, element))
        else:
            logger.error(f"No place command found for {etype.__name__}")
            return None
        return element

    def placePort(
        self  : "DrawingScene",
        *args : QPointF,
        inst  : Optional[Port] = None
    ) -> Port:
        return self.placeElement(Port, *args, inst=inst)

    def placeBlock(
        self  : "DrawingScene",
        *args : QPointF,
        inst  : Optional[Block] = None
    ) -> Block:
        return self.placeElement(Block, *args, inst=inst)

    def placeBlockPin(
        self  : "DrawingScene",
        *args : QPointF,
        inst  : Optional[BlockPin] = None
    ) -> BlockPin:
        return self.placeElement(BlockPin, *args, inst=inst)

    def placeRectangle(
        self  : "DrawingScene",
        *args : QRectF | QPointF | QSizeF | float | int,
        inst  : Optional[Rectangle] = None
    ) -> Rectangle:
        return self.placeElement(Rectangle, *args, inst=inst)

    def placeTextBlock(
        self  : "DrawingScene",
        *args : str | QPointF | KP,
        inst  : Optional[TextBlock] = None
    ) -> TextBlock:
        return self.placeElement(TextBlock, *args, inst=inst)

    def placeText(
        self  : "DrawingScene",
        *args : str | QPointF | KP,
        inst  : Optional[Text] = None
    ) -> Text:
        return self.placeElement(Text, *args, inst=inst)