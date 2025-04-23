__all__ = ["Grip", "ResizeGrip", "AnchorGrip"]

from typing import Self, Optional
from types  import SimpleNamespace

from PyQt6.QtCore    import Qt, QRectF, QXmlStreamWriter, QPointF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, \
                            QWidget, QGraphicsView, \
                            QMenu, QGraphicsSceneContextMenuEvent
from PyQt6.QtGui     import QPainter, QPen, QBrush, QPainterPath, QAction

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
        self.key_point = key_point
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsMovable            , True )
        self.setFlag( f.ItemSendsGeometryChanges , True )

    def getViewScale(
        self : Self,
        view: Optional[QGraphicsView] = None
    ) -> float:
        views = self.scene().views() if self.scene() else []
        if not view:
            if not views:
                return 1.0
            view = views[0]
        scale = view.transform().m11()
        return scale if scale != 0 else 1.0

    def getSize(self : Self, view : QGraphicsView) -> float:
        scale = self.getViewScale(view)
        return hub.settings.prefs.display.elements.selected.grip.size / scale

    def boundingRect(
        self : Self,
        view: Optional[QGraphicsView] = None
    ) -> QRectF:
        size = self.getSize(view)
        return QRectF(-size / 2, -size / 2, size, size)

    def shape(self : Self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def getView(self : Self, widget : QWidget) -> Optional[QGraphicsView]:
        view = None
        if widget and isinstance(widget.parent(), QGraphicsView):
            view = widget.parent()
        else:
            views = self.scene().views() if self.scene() else []
            if views:
                view = views[0]
        return view

    def getPenBrush(self : Self) -> tuple[QPen, QBrush]:
        theme = hub.settings.theme.grip
        return QPen(theme.line, 0, Qt.PenStyle.SolidLine), \
               QBrush(theme.fill, Qt.BrushStyle.SolidPattern)

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        pen, brush = self.getPenBrush()
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.boundingRect(self.getView(widget)))

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        pass # do not include grips in XML

class ResizeGrip(Grip):
    def moveBy(self : Self, dx : float, dy : float) -> None:
        self.parentItem().moveKeyPoint(self.key_point, QPointF(dx, dy))

class AnchorGrip(Grip):
    menu    : QMenu
    actions : SimpleNamespace

    def __init__(
        self      : Self,
        parent    : QGraphicsItem,
        key_point : "KeyPoint"
    ) -> None:
        super().__init__(parent, key_point)
        self.menu = QMenu()
        self.actions = SimpleNamespace()
        self.actions.setAnchor = QAction("Set Anchor", self.menu)
        self.actions.setAnchor.triggered.connect(self.setAnchor)
        self.menu.addAction(self.actions.setAnchor)

    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent) -> None:
        self.menu.exec(event.screenPos())
        event.widget().update()
        event.accept()

    def setAnchor(self : Self) -> None:
        self.parentItem().setAnchor(self.key_point)

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        pen, brush = self.getPenBrush()
        painter.setPen(pen)
        painter.setBrush(brush)
        size = self.getSize(self.getView(widget))
        if self.key_point == self.parentItem().anchor:
            painter.drawRect(QRectF(-size/2, -size/2, size, size))
        else:
            path = QPainterPath()
            path.moveTo(0, -size/2)
            path.lineTo(size/2, 0)
            path.lineTo(0, size/2)
            path.lineTo(-size/2, 0)
            path.closeSubpath()
            painter.drawPath(path)
