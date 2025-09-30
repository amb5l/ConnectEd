from typing import Self

from PyQt6.QtCore    import QPointF, QLineF
from PyQt6.QtWidgets import QGraphicsLineItem

from .mixin        import ElementMixin
from .mixin.line   import ElementLineMixin
from .mixin.change import ElementChangeMixin
from .mixin.clone  import ElementCloneMixin
from .mixin.xml    import ElementXmlMixin
from .mixin.menu   import ElementMenuMixin

from .conn_vtx import ConnVtx


class ConnSeg(
    ElementMixin,
    ElementLineMixin,
    ElementChangeMixin,
    ElementCloneMixin,
    ElementXmlMixin,
    ElementMenuMixin,
    QGraphicsLineItem
):
    """Runs between two ConnVtx instances."""

    # instance attributes
    _vtx1 : ConnVtx | None
    _vtx2 : ConnVtx | None
    _line : QLineF

    def __init__(
        self : Self,
        vtx1 : ConnVtx | None = None,
        vtx2 : ConnVtx | None = None
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self._line = QLineF()
        self._vtx1 = None
        self._vtx2 = None
        self.setVtx1(vtx1)
        self.setVtx2(vtx2)
        self.initElement()
        self.onGeometryChange()
        self.onSettingsChange()

    def onGeometryChange(self : Self) -> None:
        if self._vtx1 is None or self._vtx2 is None:
            return
        self._line.setP1(self._vtx1.pos())
        self._line.setP2(self._vtx2.pos())
        self.setLine(self._line)

    def vtx1(self : Self) -> ConnVtx:
        return self._vtx1

    def setVtx1(self : Self, vtx : ConnVtx | None) -> None:
        if self._vtx1 is not None:
            self._vtx1.detach(self)
        self._vtx1 = vtx
        if vtx is not None:
            vtx.attach(self)
            self._line.setP1(vtx.pos())
            self.setLine(self._line)

    def vtx2(self : Self) -> ConnVtx:
        return self._vtx2

    def setVtx2(self : Self, vtx : ConnVtx | None) -> None:
        if self._vtx2 is not None:
            self._vtx2.detach(self)
        self._vtx2 = vtx
        if vtx is not None:
            vtx.attach(self)
            self._line.setP2(vtx.pos())
            self.setLine(self._line)

    def reattach(self : Self, old : ConnVtx, new : ConnVtx) -> bool:
        if self._vtx1 is old:
            self.setVtx1(new)
            return True
        elif self._vtx2 is old:
            self.setVtx2(new)
            return True
        return False

    def toLine(self : Self) -> QLineF:
        """Return the line geometry as QLineF."""
        return self._line


class ConnSegPreview(ElementLineMixin, ElementChangeMixin, QGraphicsLineItem):
    def __init__(self : Self) -> None:
        QGraphicsLineItem.__init__(self)
        self.initLine()

    def p1(self : Self) -> QPointF:
        return QGraphicsLineItem.line(self).p1()

    def setP1(self : Self, pos: QPointF) -> None:
        line = QGraphicsLineItem.line(self)
        line.setP1(pos)
        QGraphicsLineItem.setLine(self, line)

    def p2(self : Self) -> QPointF:
        return QGraphicsLineItem.line(self).p2()

    def setP2(self : Self, pos: QPointF) -> None:
        line = QGraphicsLineItem.line(self)
        line.setP2(pos)
        QGraphicsLineItem.setLine(self, line)


class ConnSegPreview1(ConnSegPreview):
    pass


class ConnSegPreview2(ConnSegPreview):
    pass
