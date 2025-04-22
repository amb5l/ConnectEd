from typing import Self, Optional

from PyQt6.QtCore    import Qt, QRectF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, \
                            QWidget, QGraphicsView
from PyQt6.QtGui     import QPainter, QPen, QBrush, QPainterPath

from ... import hub

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import KeyPoint


class Grip(QGraphicsItem):
    Z_DELTA = 1

    key_point : "KeyPoint"

    def __init__(
        self      : Self,
        parent    : QGraphicsItem,
        key_point : "KeyPoint"
    ) -> None:
        super().__init__(parent)
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsMovable            , True )
        self.setFlag( f.ItemSendsGeometryChanges , True )
        self.key_point = key_point

    def getViewScale(self, view: Optional[QGraphicsView] = None) -> float:
        views = self.scene().views() if self.scene() else []
        if not view:
            if not views:
                return 1.0
            view = views[0]
        scale = view.transform().m11()
        return scale if scale != 0 else 1.0

    def boundingRect(self, view: Optional[QGraphicsView] = None) -> QRectF:
        size_p = hub.settings.prefs.display.elements.selected.grip.size
        scale = self.getViewScale(view)
        size_l = size_p / scale
        return QRectF(-size_l / 2, -size_l / 2, size_l, size_l)

    def shape(self : Self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        view = None
        if widget and isinstance(widget.parent(), QGraphicsView):
            view = widget.parent()
        else:
            views = self.scene().views() if self.scene() else []
            if views:
                view = views[0]
        a = self == self.parentItem().grips[self.parentItem().anchor]
        theme = hub.settings.theme.anchor if a else hub.settings.theme.grip
        painter.setPen(QPen(theme.line, 0, Qt.PenStyle.SolidLine))
        painter.setBrush(QBrush(theme.fill, Qt.BrushStyle.SolidPattern))
        painter.drawRect(self.boundingRect(view))

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        pass
