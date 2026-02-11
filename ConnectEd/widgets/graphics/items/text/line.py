from typing import Self, Any, overload

from PyQt6.QtCore    import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsSimpleTextItem, \
                            QGraphicsSceneContextMenuEvent, \
                            QStyleOptionGraphicsItem, QStyle, QWidget
from PyQt6.QtGui     import QColor, QPainterPath, QPainter

from .....core.types import AlignH, AlignV

from ..mixin.bound  import ItemBoundMixin
from ..mixin.shape  import ItemShapeMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import TextItem


class TextLineRenderer(
    ItemBoundMixin,
    ItemShapeMixin,
    QGraphicsSimpleTextItem
):
    # instance attributes
    _clip_rect : QRectF | None = None

    @overload
    def __init__(self, parent: QGraphicsItem | None = None) -> None:
        ...

    @overload
    def __init__(self, text: str, parent: QGraphicsItem | None = None) -> None:
        ...

    def __init__(
        self           : Self,
        text_or_parent : str | QGraphicsItem | None = None,
        parent         : QGraphicsItem | None = None
    ) -> None:
        if isinstance(text_or_parent, str):
            super().__init__(text_or_parent, parent)
        else:
            super().__init__(parent=parent)
        self._clip_rect = None
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.initBound()  # initialize cached bounding rect
        self.initShape()  # initialize cached hit detect shape

    def itemChange(
        self   : Self,
        change : QGraphicsItem.GraphicsItemChange,
        value  : Any
    ) -> Any:
        """Propagate selection state to parent."""
        match change:
            case self.GraphicsItemChange.ItemSelectedHasChanged:
                parent : TextItem | None = self.parentItem()
                if parent is not None:
                    QGraphicsItem.setSelected(parent, value)
        return super().itemChange(change, value)

    def onGeometryChange(self : Self) -> None:
        parent : TextItem = self.parentItem()
        align_h = parent._align_h
        align_v = parent._align_v
        width   = parent._width
        height  = parent._height
        # update cached bounding rect, accounting for constraints
        urect = QGraphicsSimpleTextItem.boundingRect(self)  # unconstrained rect
        w = width  if width  >= 0.0 else urect.width()
        h = height if height >= 0.0 else urect.height()
        self._brect = QRectF(0.0, 0.0, w, h)
        # apply clipping if constraints are smaller than unconstrained rect
        if w < urect.width() or h < urect.height():
            self._clip_rect = self._brect
        else:
            self._clip_rect = None
        # position to apply alignment
        match align_h:
            case AlignH.LEFT:
                x = 0
            case AlignH.CENTER:
                x = (w - urect.width()) / 2
            case AlignH.RIGHT:
                x = w - urect.width()
        match align_v:
            case AlignV.TOP:
                y = 0
            case AlignV.MIDDLE:
                y = (h - urect.height()) / 2
            case AlignV.BOTTOM:
                y = h - urect.height()
        self.setPos(x, y)
        # update transform origin
        self.setTransformOriginPoint(QPointF(urect.width() / 2, urect.height() / 2))
        # update cached hit detect shape
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)
        # update transform origin
        self.setTransformOriginPoint(self._brect.center())
        # update
        self.update()

    def color(self : Self) -> QColor:
        return self.brush().color()

    def setColor(self : Self, color : QColor) -> None:
        brush = self.brush()
        brush.setColor(color)
        self.setBrush(brush)

    def paint(
        self    : Self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        option.state &= ~QStyle.StateFlag.State_Selected
        if self._clip_rect is not None:
            painter.save()
            painter.setClipRect(self._clip_rect)
        super().paint(painter, option, widget)
        if self._clip_rect is not None:
            painter.restore()

    def contextMenuEvent(
        self  : Self,
        event : QGraphicsSceneContextMenuEvent
    ) -> None:
        """Bounce context menu event to parent."""
        parent: "TextItem" = self.parentItem()
        parent.contextMenuEvent(event)
