from typing import Self

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPainterPath

from ....app import logger

from ....core.check import checked


class NullItem(QGraphicsItem):
    # instance attributes
    _brect  : QRectF        # bounding rect
    _hshape : QPainterPath  # shape for hit detection

    @checked
    def __init__(self : Self, parent : QGraphicsItem | None = None) -> None:
        super().__init__(parent)
        self.setFlag( self.GraphicsItemFlag.ItemHasNoContents , True  )
        self.setFlag( self.GraphicsItemFlag.ItemIsMovable     , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsSelectable  , False )
        self.setFlag( self.GraphicsItemFlag.ItemIsFocusable   , False )
        self._brect = QRectF()
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)

    def boundingRect(self : Self) -> QRectF:
        return self._brect

    def shape(self : Self) -> QPainterPath:
        return self._hshape

    def paint(
        self    : Self,
        painter : QPainter | None,
        option  : QStyleOptionGraphicsItem | None,
        widget  : QWidget | None = None
    ) -> None:
        logger().error("Paint should never be called")
