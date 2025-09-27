from typing import Self

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QStyleOptionGraphicsItem, QGraphicsPathItem, \
                            QWidget, QStyle
from PyQt6.QtGui     import QPainter, QPainterPath

from .mixin.line   import ElementLineMixin
from .mixin.fill   import ElementFillMixin
from .mixin.change import ElementChangeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .port_pin import PortPinMixin


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
        parent : "PortPinMixin"
    ) -> None:
        QGraphicsPathItem.__init__(self, parent)
        f = self.GraphicsItemFlag
        self.setFlag(f.ItemIsSelectable, True)
        self.initLine()
        self.initFill()
        s = self._SIZE / 2
        self._path_open = QPainterPath()
        self._path_nc = QPainterPath()
        self.onSettingsChange()

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

    def onSelectionChange(self : Self, selected : bool) -> None:
        parent = self.parentItem()
        if parent and parent.isSelected() != selected:
            parent.setSelected(selected)

    def moveBy(self : Self, delta : QPointF) -> None:
        parent : "PortPinMixin" = self.parentItem()
        parent.moveBy(delta)

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget | None = None
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        QGraphicsPathItem.paint(self, painter, option, widget)
