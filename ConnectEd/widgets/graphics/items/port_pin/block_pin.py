from .node     import Node
from .port_pin import PortPinText, PortPinArrow
from .pin      import PinMixin


class BlockPinNode(Node):
    pass


class BlockPinName(PortPinText):
    pass


class BlockPinComment(PortPinText):
    pass


class BlockPin(PinMixin, PortPinArrow):
    # class attributes
    _PATH_IN       = PortPinArrow._PATH_AWAY
    _PATH_OUT      = PortPinArrow._PATH_TOWARDS
    _NODE_CLASS    = BlockPinNode
    _NAME_CLASS    = BlockPinName
    _COMMENT_CLASS = BlockPinComment
