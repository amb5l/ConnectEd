__all__ = ["Node"]

from typing import Self, Optional

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QGraphicsPathItem, \
                            QWidget, QStyle
from PyQt6.QtGui     import QPainter, QPainterPath

from . import ElementLineMixin, \
              ElementFillMixin, \
              ElementChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .port_pin import BasePortPin


class Node(
    ElementLineMixin,
    ElementFillMixin,
    ElementChangeMixin,
    QGraphicsPathItem
):
    # class attributes
    _SIZE = 4

    # instance attributes
    _path_open : QPainterPath  # path when open
    _path_nc   : QPainterPath  # path when closed
    _brect     : QRectF        # cached bounding rect

    def __init__(
        self   : Self,
        parent : "BasePortPin"
    ) -> None:
        QGraphicsPathItem.__init__(self, parent)
        self.initLine()
        self.initFill()
        s = self._SIZE / 2
        self._path_open = QPainterPath()
        self._path_nc = QPainterPath()
        self.onSettingsChange()

    def onSelectionChange(self : Self, selected : bool) -> None:
        self.parentItem().setSelected(selected)

    def onSettingsChange(self : Self) -> None:
        s = self._SIZE / 2
        self._path_open.clear()
        self._path_open.addRect(QRectF(-s, -s, 2*s, 2*s))
        self._brect = self._path_open.boundingRect()
        self._path_nc.clear()
        self._path_nc.moveTo(-s, +s)
        self._path_nc.lineTo(+s, -s)
        self._path_nc.moveTo(+s, +s)
        self._path_nc.lineTo(-s, -s)
        self.setPath(self._path_open)
        # TODO change appearance with connectivity

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : Optional[QWidget] = None
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        QGraphicsPathItem.paint(self, painter, option, widget)
