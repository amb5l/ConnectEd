from typing import Self

from .port_pin import PortPinText
from .pin      import PinArrow, PinNode, Pin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...views.drawing import DrawingView


class BlockPinArrow(PinArrow):
    pass


class BlockPinNode(PinNode):
    pass


class BlockPinName(PortPinText):
    pass


class BlockPinComment(PortPinText):
    pass


class BlockPin(Pin):
    @classmethod
    def _getArrowClass(cls) -> type[BlockPinArrow]:
        return BlockPinArrow

    @classmethod
    def _getNodeClass(cls) -> type[BlockPinNode]:
        return BlockPinNode

    @classmethod
    def _getNameClass(cls) -> type[BlockPinName]:
        return BlockPinName

    @classmethod
    def _getCommentClass(cls) -> type[BlockPinComment]:
        return BlockPinComment

    def getMenuItems(self : Self) -> list[str]:
        return ["Edit"]

    def ctxMenuEdit(
        self    : Self,
        _checked : bool,
        view    : "DrawingView"
    ) -> None:
        view.editBlockPin(self)
