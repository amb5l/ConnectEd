from typing import Self

from PyQt6.QtCore    import QRectF, QXmlStreamWriter
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPainterPath, QMouseEvent

from ....app import logger

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import ItemMixin


class NullItem(QGraphicsItem):
    # instance attributes
    _brect  : QRectF        # bounding rect
    _hshape : QPainterPath  # shape for hit detection

    def __init__(self : Self, parent : "ItemMixin | None" = None) -> None:
        super().__init__(parent)
        self.setFlag( self.GraphicsItemFlag.ItemHasNoContents , True  )
        self.setFlag( self.GraphicsItemFlag.ItemIsMovable     , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsSelectable  , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsFocusable   , False )
        self._brect = QRectF()
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)

    def mousePressEvent(self : Self, event : QMouseEvent):
        event.ignore()
        return

    def mouseMoveEvent(self : Self, event : QMouseEvent):
        event.ignore()
        return

    def mouseReleaseEvent(self : Self, event : QMouseEvent):
        event.ignore()
        return

    def mouseDoubleClickEvent(self : Self, event : QMouseEvent):
        event.ignore()
        return

    def boundingRect(self : Self) -> QRectF:
        return self._brect

    def shape(self : Self) -> QPainterPath:
        return self._hshape

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        logger().error("Paint should never be called")

    def toXml(self : Self, xw : QXmlStreamWriter) -> None:
        """Dummy toXml method - NullPoints are not serialized."""
        pass
