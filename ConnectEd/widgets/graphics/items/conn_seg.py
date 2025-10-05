from typing import Self

from PyQt6.QtCore    import QPointF, QLineF, QXmlStreamReader, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsLineItem

from ....app import logger

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
    _vtx1 : ConnVtx | QPointF | None
    _vtx2 : ConnVtx | QPointF | None
    _line : QLineF

    def __init__(
        self : Self,
        vtx1 : ConnVtx | QPointF | None = None,
        vtx2 : ConnVtx | QPointF | None = None
    ) -> None:
        QGraphicsLineItem.__init__(self)
        self._line = QLineF()
        self._vtx1 = None
        self._vtx2 = None
        self.initElement()
        self.setVtx1(vtx1)
        self.setVtx2(vtx2)
        self.onGeometryChange()

    def onGeometryChange(self : Self) -> None:
        v1 = self._vtx1
        v2 = self._vtx2
        if v1 is None or v2 is None:
            return
        self._line.setP1(v1.scenePos() if isinstance(v1, ConnVtx) else v1)
        self._line.setP2(v2.scenePos() if isinstance(v2, ConnVtx) else v2)
        self.setLine(self._line)

    def vtx1(self : Self) -> ConnVtx | QPointF | None:
        return self._vtx1

    def setVtx1(self : Self, vtx : ConnVtx | QPointF | None) -> None:
        if isinstance(self._vtx1, ConnVtx):
            self._vtx1.detach(self)
        self._vtx1 = vtx
        if isinstance(vtx, ConnVtx):
            vtx.attach(self)
        self.onGeometryChange()

    def vtx2(self : Self) -> ConnVtx | QPointF | None:
        return self._vtx2

    def setVtx2(self : Self, vtx : ConnVtx | QPointF | None) -> None:
        if isinstance(self._vtx2, ConnVtx):
            self._vtx2.detach(self)
        self._vtx2 = vtx
        if isinstance(vtx, ConnVtx):
            vtx.attach(self)
        self.onGeometryChange()

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

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        def getVal(s : str) -> float:
            a = s[0]; n = int(s[1:])
            attr_val = getattr(self, f"_vtx{n}")  # value of self._vtx{n}
            p = attr_val.scenePos() if isinstance(attr_val, ConnVtx) else \
                attr_val if isinstance(attr_val, QPointF) else \
                None
            return None if p is None else getattr(p, a)()
        xw.writeStartElement(self.__class__.__name__)
        xw.writeAttribute("x1", str(getVal("x1")))
        xw.writeAttribute("y1", str(getVal("y1")))
        xw.writeAttribute("x2", str(getVal("x2")))
        xw.writeAttribute("y2", str(getVal("y2")))
        xw.writeEndElement()

    @classmethod
    def fromXml(cls : Self, xr : QXmlStreamReader) -> Self:
        xml_attrs = {a.name(): a.value() for a in xr.attributes()}
        def getVal(attr_name : str) -> float:
            value = 0
            if attr_name in xml_attrs:
                value = float(xml_attrs[attr_name])
                xml_attrs.pop(attr_name)
            return value
        x1 = getVal("x1")
        y1 = getVal("y1")
        x2 = getVal("x2")
        y2 = getVal("y2")
        if xml_attrs.keys():
            logger().warning(f"Unexpected attributes: {xml_attrs.keys()}")
        instance = cls(QPointF(x1, y1), QPointF(x2, y2))
        xr.readNext()
        return instance


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
