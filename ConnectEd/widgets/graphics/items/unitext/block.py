from typing import Self, Any, overload

from PyQt6.QtCore    import QRectF
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsTextItem, \
                            QGraphicsSceneContextMenuEvent
from PyQt6.QtGui     import QColor, QPainterPath

from .. import AlignV

from ..mixin.bound  import ItemBoundMixin
from ..mixin.shape  import ItemShapeMixin
from ..mixin.rotate import ItemRotateMixin
from ..mixin.paint  import ItemPaintMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import UniTextItem


class UniTextBlockItem(
    ItemBoundMixin,
    ItemShapeMixin,
    ItemPaintMixin,
    QGraphicsTextItem
):
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
                parent : UniTextItem | None = self.parentItem()
                if parent is not None:
                    QGraphicsItem.setSelected(parent, value)
        return super().itemChange(change, value)

    def onSceneRotationChange(self : Self) -> None:
        """Rotation compensation."""
        a = ItemRotateMixin.sceneRotation(self)
        self.setRotation(180 if a > 135 and a <= 315 else 0)

    def text(self : Self) -> str:
        return self.toPlainText()

    def setText(self : Self, text : str) -> None:
        self.setPlainText(text)

    def onGeometryChange(self : Self) -> None:
        parent : UniTextItem = self.parentItem()
        align_h = parent._align_h
        align_v = parent._align_v
        width = parent._width
        height = parent._height
        # get underlying document
        doc = self.document()
        # apply horizontal alignment
        option = doc.defaultTextOption()
        option.setAlignment(align_h.value)
        doc.setDefaultTextOption(option)
        # apply width constraint
        self.setTextWidth(width if width else -1)
        # calculate unconstrained bounding rect (without margins)
        root_frame = doc.rootFrame()
        fmt = root_frame.frameFormat()
        fmt.setMargin(0)  # temporarily remove margins
        root_frame.setFrameFormat(fmt)
        urect = QGraphicsTextItem.boundingRect(self)  # unconstrained rect
        # update cached bounding rect, accounting for constraints
        w = width  if width  else urect.width()
        h = height if height else urect.height()
        self._brect = QRectF(0.0, 0.0, w, h)
        # if height constrained: apply vertical alignment via document top margin
        if height:
            match align_v:
                case AlignV.BOTTOM:
                    top_margin = height - urect.height()
                case AlignV.CENTER:
                    top_margin = (height - urect.height()) / 2
                case _:  # Top
                    top_margin = 0
            fmt.setTopMargin(top_margin)
            root_frame.setFrameFormat(fmt)
        # update cached hit detect shape
        self._hshape = QPainterPath()
        self._hshape.addRect(self._brect)
        # update
        self.update()

    def color(self : Self) -> QColor:
        return self.defaultTextColor()

    def setColor(self : Self, color : QColor) -> None:
        self.setDefaultTextColor(color)

    def contextMenuEvent(
        self  : Self,
        event : QGraphicsSceneContextMenuEvent
    ) -> None:
        """Bounce context menu event to parent."""
        parent: "UniTextItem" = self.parentItem()
        parent.contextMenuEvent(event)
