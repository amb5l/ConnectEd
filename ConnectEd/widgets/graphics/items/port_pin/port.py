from ..mixin.pos import ElementPosMixin

from .node     import Node
from .port_pin import PortPinText, PortPinMixin, PortPinArrow


class PortNode(Node):
    pass


class PortName(PortPinText):
    pass


class PortComment(PortPinText):
    pass


class Port(ElementPosMixin, PortPinArrow):
    # class attributes
    _PATH_IN       = PortPinArrow._PATH_TOWARDS
    _PATH_OUT      = PortPinArrow._PATH_AWAY
    _NODE_CLASS    = PortNode
    _NAME_CLASS    = PortName
    _COMMENT_CLASS = PortComment
    _NAME_OFFSET   = 1.5
    _PROPERTY_SPECS = \
        ElementPosMixin._PROPERTY_SPECS_POS | \
        PortPinMixin._PROPERTY_SPECS
