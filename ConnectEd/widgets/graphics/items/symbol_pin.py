from .port_pin import PortPinText

from .node import Node
from .pin  import PinArrow, Pin


class SymbolPinArrow(PinArrow):
    pass


class SymbolPinNode(Node):
    pass


class SymbolPinName(PortPinText):
    pass


class SymbolPinComment(PortPinText):
    pass


class SymbolPin(Pin):
    @classmethod
    def _getArrowClass(cls) -> type[SymbolPinArrow]:
        return SymbolPinArrow

    @classmethod
    def _getNodeClass(cls) -> type[SymbolPinNode]:
        return SymbolPinNode

    @classmethod
    def _getNameClass(cls) -> type[SymbolPinName]:
        return SymbolPinName

    @classmethod
    def _getCommentClass(cls) -> type[SymbolPinComment]:
        return SymbolPinComment
