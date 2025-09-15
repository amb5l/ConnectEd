from .port_pin import PortPinText
from .pin      import PinArrow, PinNode, Pin


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
