from typing import Self, Optional

from PyQt6.QtCore    import QLineF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsLineItem

from ..mixin.loc import ElementLocMixin

from .port_pin import PortPinMixin


class PinMixin(PortPinMixin, ElementLocMixin):
    # class attributes
    _PROPERTY_SPECS = \
        ElementLocMixin._PROPERTY_SPECS_LOC | \
        PortPinMixin._PROPERTY_SPECS


class Pin(PinMixin, QGraphicsLineItem):
    """Base QGraphicsItem class for symbol pins."""

    # class attributes
    _SIZE = 10

    def __init__(self : Self, parent : Optional[QGraphicsItem] = None) -> None:
        QGraphicsLineItem.__init__(self, parent)
        self.initPortPin()
        line = QLineF(0, 0, -self._SIZE, 0)
        self.setLine(line)
        self._node.setPos(-self._SIZE, 0)
