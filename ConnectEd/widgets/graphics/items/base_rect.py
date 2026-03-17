from typing import Self, overload

from PyQt6.QtCore    import QPointF, QRectF, QSizeF
from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QMenu
from PyQt6.QtGui     import QAction

from ....core.defs  import PITCH
from ....core.types import RectHandleId, DataKind

from ..properties import PropertiesMixin, InherentProperty

from .mixin        import ItemMixin
from .mixin.origin import ItemOriginMixin
from .mixin.pos    import ItemPosMixin
from .mixin.rotate import ItemRotateMixin
from .mixin.paint  import ItemPaintMixin
from .mixin.handle import ItemRectHandlesMixin
from .mixin.line   import ItemLineMixin
from .mixin.fill   import ItemFillMixin
from .mixin.change import ItemChangeMixin
from .mixin.clone  import ItemCloneMixin
from .mixin.xml    import ItemXmlMixin
from .mixin.menu   import ItemMenuMixin

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..views.drawing  import DrawingView


class BaseRectangleMixin(
    ItemMixin,
    ItemOriginMixin,
    ItemPosMixin,
    ItemRotateMixin,
    ItemPaintMixin,
    ItemRectHandlesMixin,
    ItemLineMixin,
    ItemFillMixin,
    ItemChangeMixin,
    ItemCloneMixin,
    ItemXmlMixin,
    ItemMenuMixin,
    PropertiesMixin
):
    """Base mixin class for rectangle-like items."""

    # class attributes
    _ORIGIN = RectHandleId.MIDDLE_CENTER
    _PROPERTIES = \
        ItemOriginMixin._PROPERTIES_RECT_ORIGIN | \
        ItemPosMixin._PROPERTIES_POS | \
        ItemRotateMixin._PROPERTIES_ROTATE | \
        {
            "Width" : InherentProperty(
                kind   = DataKind.FLOAT,
                getter = lambda self: self.rect().width(),
                setter = lambda self, value: self.setWidth(value)
            ),
            "Height" : InherentProperty(
                kind   = DataKind.FLOAT,
                getter = lambda self: self.rect().height(),
                setter = lambda self, value: self.setHeight(value)
            )
        } | \
        ItemLineMixin._PROPERTIES_LINE | \
        ItemFillMixin._PROPERTIES_FILL
    _MIN_SIZE = QSizeF(1.0, 1.0)

    @overload
    def __init__(
        self  : Self,
        p1    : QPointF | None = None,
        p2    : QPointF | None = None,
        fresh : bool = True
    ) -> None:
        ...

    @overload
    def __init__(
        self  : Self,
        pos   : QPointF | None = None,
        size  : QSizeF | None = None,
        fresh : bool = True
    ) -> None:
        ...

    def __init__(
        self       : Self,
        p1_or_pos  : QPointF | None = None,
        p2_or_size : QPointF | QSizeF | None = None,
        fresh      : bool = True
    ) -> None:
        super().__init__()
        self.initItem(fresh)
        p1_or_pos = p1_or_pos or QPointF()
        p2_or_size = p2_or_size or QSizeF(0, 0)
        if isinstance(p2_or_size, QSizeF):
            p2_or_size = QPointF(
                p1_or_pos.x() + p2_or_size.width(),
                p1_or_pos.y() + p2_or_size.height()
            )
        self.setPoints(p1_or_pos, p2_or_size)
        self.onGeometryChange()

    def onGeometryChange(self : Self | QGraphicsRectItem) -> None:
        #self.prepareGeometryChange()
        #pen_width = self.pen().widthF()
        #tolerance = settings().get("display/select/tolerance")
        #stroke_width = pen_width + (2 * tolerance)
        #rect_path = QPainterPath()
        #rect_path.addRect(self.rect())
        #stroker = QPainterPathStroker()
        #stroker.setWidth(stroke_width)
        #stroker.setCapStyle(Qt.PenCapStyle.SquareCap)
        #stroker.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        #stroker_path = stroker.createStroke(rect_path)
        #self._brect = stroker_path.boundingRect()
        #if self.a.fill._brush.style() != Qt.BrushStyle.NoBrush:
        #    self._hshape = rect_path.united(stroker_path)
        #else:
        #    self._hshape = stroker_path
        self.updateHandlePositions()

    @overload
    def setRect(
        self : Self,
        ax : float | int,
        ay : float | int,
        w  : float | int,
        h  : float | int
    ) -> None:
        ...

    @overload
    def setRect(
        self : Self,
        rect : QRectF
    ) -> None:
        ...

    def setRect(self, *args, **kwargs) -> None:
        proxy : QGraphicsRectItem | QGraphicsEllipseItem = super()
        proxy.setRect(*args, **kwargs)
        self.onGeometryChange()

    def setWidth(self : Self | QGraphicsRectItem, width : float | int) -> None:
        rect = self.rect()
        rect.setWidth(width)
        self.setRect(rect)

    def setHeight(self : Self | QGraphicsRectItem, height : float | int) -> None:
        rect = self.rect()
        rect.setHeight(height)
        self.setRect(rect)

    @overload
    def setPoints(
        self : Self,
        p1   : QPointF,
        p2   : QPointF
    ) -> None:
        ...

    @overload
    def setPoints(
        self : Self,
        x1   : float | int,
        y1   : float | int,
        x2   : float | int,
        y2   : float | int
    ) -> None:
        ...

    def setPoints(
        self : Self | QGraphicsRectItem,
        p1_x1 : QPointF | float | int,
        p2_y1 : QPointF | float | int,
        x2    : float | int | None = None,
        y2    : float | int | None = None
    ) -> None:
        if x2 is None or y2 is None:
            x1 = p1_x1.x()
            y1 = p1_x1.y()
            x2 = p2_y1.x()
            y2 = p2_y1.y()
        else:
            x1 = p1_x1
            y1 = p2_y1
        w = max(abs(x2-x1), PITCH)
        h = max(abs(y2-y1), PITCH)
        rect = self.rect()
        rect.setSize(QSizeF(w, h))
        self.setRect(rect)
        origin_offset = self.transformOriginPoint()
        target_pos = QPointF(min(x1, x2), min(y1, y2)) + origin_offset
        self.setPos(target_pos)

    def handleRect(self : Self | QGraphicsRectItem | QGraphicsEllipseItem) -> QRectF:
        return self.rect()

    def ctxMenuItems(self : Self, view : "DrawingView") -> list[QAction | QMenu]:
        return [
            view.action("Appearance...", lambda: view.ui.editAppearance(self)),
            view.action("Properties...", lambda: view.ui.editItemProperties(self))
        ]


class BaseRectangleItem(BaseRectangleMixin, QGraphicsRectItem):
    """Base class for rectangle items."""
    pass
