from typing import Self

from PyQt6.QtCore    import QLineF
from PyQt6.QtWidgets import QGraphicsLineItem

from .mixin        import ElementMixin
from .mixin.line   import ElementLineMixin
from .mixin.change import ElementChangeMixin
from .mixin.clone  import ElementCloneMixin
from .mixin.xml    import ElementXmlMixin
from .mixin.menu   import ElementMenuMixin

from .wire_vertex import WireVertex


class WireSegment(
    ElementMixin,
    ElementLineMixin,
    ElementChangeMixin,
    ElementCloneMixin,
    ElementXmlMixin,
    ElementMenuMixin,
    QGraphicsLineItem
):
    """Runs between two WireVertex instances."""

    # instance attributes
    _v1   : WireVertex
    _v2   : WireVertex
    _line : QLineF

    def __init__(
        self : Self,
        v1   : WireVertex,
        v2   : WireVertex
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self._v1 = v1
        self._v2 = v2
        self._line = QLineF()
        self.initElement()
        self.onGeometryChange()
        self.onSettingsChange()

    def onGeometryChange(self : Self) -> None:
        self._line.setP1(self._v1.pos())
        self._line.setP2(self._v2.pos())
        self.setLine(self._line)

    def v1(self : Self) -> WireVertex:
        return self._v1

    def setV1(self : Self, p1 : WireVertex) -> None:
        self._line.setP1(p1.pos())
        self.setLine(self._line)

    def v2(self : Self) -> WireVertex:
        return self._v2

    def setV2(self : Self, p2 : WireVertex) -> None:
        self._line.setP2(p2.pos())
        self.setLine(self._line)
