from .node     import Node
from .port_pin import PortPinText
from .pin      import PinMixin, Pin


class SymbolPinNode(Node):
    pass


class SymbolPinName(PortPinText):
    pass


class SymbolPinComment(PortPinText):
    pass


class SymbolPin(Pin):
    # class attributes
    _NODE_CLASS    = SymbolPinNode
    _NAME_CLASS    = SymbolPinName
    _COMMENT_CLASS = SymbolPinComment
