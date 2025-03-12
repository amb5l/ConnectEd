__all__ = [
    'Extents',
    'Paper',
    'Border',
    'Rectangle',
    'Grid'
]

from dataclasses import dataclass
from enum        import Enum
from collections import namedtuple
from typing      import Optional
from math        import copysign

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtGui     import QPainter, QPen, QBrush, QColor, QPainterPath
from PyQt6.QtWidgets import \
    QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, \
    QStyleOptionGraphicsItem, QWidget

from ...core import settings


@dataclass
class PenSpec:
    color : Optional[QColor]      = None
    width : Optional[float]       = None
    style : Optional[Qt.PenStyle] = None

@dataclass
class BrushSpec:
    color : Optional[QColor]        = None
    style : Optional[Qt.BrushStyle] = None

@dataclass
class TextSpec:
    color     : Optional[QColor] = None
    family    : Optional[str]    = None
    size      : Optional[float]  = None # TODO: 0 = resize with parent boundary?
    weight    : Optional[int]    = None
    italic    : Optional[bool]   = None
    underline : Optional[bool]   = None

AnchorHV = namedtuple('AnchorHV', ['h', 'v'])

class Anchor(Enum):
    TOP_LEFT      = AnchorHV(0.0, 0.0)
    TOP_CENTER    = AnchorHV(0.5, 0.0)
    TOP_RIGHT     = AnchorHV(1.0, 0.0)
    CENTER_LEFT   = AnchorHV(0.0, 0.5)
    CENTER        = AnchorHV(0.5, 0.5)
    CENTER_RIGHT  = AnchorHV(1.0, 0.5)
    BOTTOM_LEFT   = AnchorHV(0.0, 1.0)
    BOTTOM_CENTER = AnchorHV(0.5, 1.0)
    BOTTOM_RIGHT  = AnchorHV(1.0, 1.0)

class ItemBasicsMixin:
    """Basics for all items."""

    wip : bool

    def defaultSetup(self) -> None:
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsMovable                        , True  )
        self.setFlag( f.ItemIsSelectable                     , False )
        self.setFlag( f.ItemIsFocusable                      , True  )
        self.setFlag( f.ItemClipsToShape                     , False )
        self.setFlag( f.ItemClipsChildrenToShape             , False )
        self.setFlag( f.ItemIgnoresTransformations           , False )
        self.setFlag( f.ItemIgnoresParentOpacity             , False )
        self.setFlag( f.ItemDoesntPropagateOpacityToChildren , False )
        self.setFlag( f.ItemStacksBehindParent               , False )
        self.setFlag( f.ItemUsesExtendedStyleOption          , False )
        self.setFlag( f.ItemHasNoContents                    , False )
        self.setFlag( f.ItemSendsGeometryChanges             , True  )
        self.setFlag( f.ItemAcceptsInputMethod               , True  )
        self.setFlag( f.ItemNegativeZStacksBehindParent      , False )
        self.setFlag( f.ItemIsPanel                          , False )
        self.setFlag( f.ItemSendsScenePositionChanges        , True  )
        self.setFlag( f.ItemContainsChildrenInShape          , True  )
        self.setCacheMode(QGraphicsItem.CacheMode.DeviceCoordinateCache)

    def setWIP(self, wip : bool = True) -> None:
        self.wip = wip

class ItemPenMixin:
    """Pen support."""

    pen_spec : PenSpec

    def initPenSpec(self) -> None:
        self.pen_spec = PenSpec()

    def setPenSpec(
        self,
        pen_spec : PenSpec = PenSpec()
    ) -> None:
        self.pen_spec = pen_spec

    def penFromSpec(self) -> None:
        # TODO handle WIP
        if self.isSelected():
            prefs = settings.prefs.display.items.selected.line
            theme = settings.theme.selected.line
        else:
            item_name = self.__class__.__name__.lower()
            prefs = getattr(settings.prefs.display.items, item_name).line
            theme = getattr(settings.theme, item_name).line
        pen = QPen()
        pen.setColor(
            theme if self.pen_spec.color is None else
                self.pen_spec.color
        )
        pen.setWidth(
            prefs.width if self.pen_spec.width is None else
                self.pen_spec.width
        )
        pen.setStyle(
            prefs.style if self.pen_spec.style is None else
                self.pen_spec.style
        )
        return pen

class ItemBrushMixin:
    """Brush support."""

    brush_spec : BrushSpec

    def initBrushSpec(self) -> None:
        self.brush_spec = BrushSpec()

    def setBrushSpec(
        self,
        brush_spec : BrushSpec = BrushSpec()
    ) -> None:
        self.brush_spec = brush_spec

    def brushFromSpec(self) -> None:
        if self.isSelected():
            prefs = settings.prefs.display.items.selected.fill
            theme = settings.theme.selected.fill
        else:
            item_name = self.__class__.__name__.lower()
            prefs = getattr(settings.prefs.display.items, item_name).fill
            theme = getattr(settings.theme, item_name).fill
        brush = QBrush()
        brush.setColor(
            theme if self.brush_spec.color is None else
                self.brush_spec.color
        )
        brush.setStyle(
            prefs if self.brush_spec.style is None else
                self.brush_spec.style
        )
        return brush

class ItemTextMixin:
    """Text/font support."""

    text_spec : TextSpec

    def setTextSpec(
        self,
        text_spec : TextSpec = TextSpec()
    ) -> None:
        self.text_spec = text_spec

    def updateFont(self) -> None:
        item_name = self.__class__.__name__.lower()
        prefs = getattr(settings.prefs.display.items, item_name).font
        theme = getattr(settings.theme, item_name).font
        self.setDefaultTextColor(
            theme.color if self.text_spec.color is None else
                self.text_spec.color
        )
        self.font.setFamily(
            prefs.family if self.text_spec.family is None else
                self.text_spec.family
        )
        self.font.setPointSizeF(
            prefs.size if self.text_spec.size is None else
                self.text_spec.size
        )
        self.font.setWeight(
            prefs.weight if self.text_spec.weight is None else
                self.text_spec.weight
        )
        self.font.setItalic(
            prefs.italic if self.text_spec.italic is None else
                self.text_spec.italic
        )

class RectBaseItem(
    QGraphicsRectItem,
    ItemBasicsMixin
):
    """Base class for rectangle items."""

    MIN_SIZE = QSizeF(1.0, 1.0)

    p1     : QPointF
    p2     : QPointF
    anchor : Anchor

    def __init__(
        self,
        p1     : QPointF,
        p2     : Optional[QPointF] = None,
        anchor : Anchor = Anchor.TOP_LEFT,
        wip    : bool = False
    ) -> None:
        super().__init__()
        self.defaultSetup()
        self.setZValue(self.Z)
        self.setPoints(p1, p2)
        self.setAnchor(anchor)
        self.setWIP(wip)

    def setPoints(self, p1 : QPointF, p2 : Optional[QPointF] = None) -> None:
        self.p1 = p1
        if p2 is None:
            p2 = p1 + QPointF(self.MIN_SIZE.width(), self.MIN_SIZE.height())
        self.setPoint2(p2)

    def setPoint2(self, p2 : QPointF) -> None:
        m = self.MIN_SIZE
        if abs(p2.x() - self.p1.x()) < m.width():
            p2.setX(self.p1.x() + copysign(m.width(), p2.x() - self.p1.x()))
        if abs(p2.y() - self.p1.y()) < m.height():
            p2.setY(self.p1.y() + copysign(m.height(), p2.y() - self.p1.y()))
        self.p2 = p2
        self.prepareGeometryChange()
        rect = QRectF(self.p1, self.p2).normalized()
        self.setPos(rect.topLeft())
        self.setRect(0, 0, rect.width(), rect.height())

    def setAnchor(self, anchor : Anchor = Anchor.TOP_LEFT) -> None:
        self.anchor = anchor

    def boundingRect(self) -> QRectF:
        rect = super().boundingRect()
        return QRectF(
            -rect.width() * self.anchor.value.h,
            -rect.height() * self.anchor.value.v,
            rect.width(), rect.height()
        )

    def shape(self) -> QPainterPath:
        path = super().shape()
        rect = path.boundingRect()
        path.translate(
            -rect.width()  * self.anchor.value.h,
            -rect.height() * self.anchor.value.v
        )
        return path

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        rect = self.rect()
        painter.translate(
            -rect.width() * self.anchor.value.h,
            -rect.height() * self.anchor.value.v
        )
        painter.drawRect(rect)

class RectPenOnlyItem(RectBaseItem, ItemPenMixin):
    """Base class for unfilled rectangle items."""

    def __init__(
        self,
        p1     : QPointF,
        p2     : Optional[QPointF] = None,
        anchor : Anchor = Anchor.TOP_LEFT,
        wip    : bool = False
    ) -> None:
        super().__init__(p1, p2, anchor, wip)
        self.initPenSpec()

    def boundingRect(self) -> QRectF:
        item_name = self.__class__.__name__.lower()
        default = getattr(settings.prefs.display.items, item_name).line
        w = default.width if self.pen_spec.width is None else \
            self.pen_spec.width
        margin = w / 2
        return super().boundingRect().adjusted(-margin, -margin, margin, margin)

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setPen(self.penFromSpec())
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        super().paint(painter, option, widget)

class RectBrushOnlyItem(RectBaseItem, ItemBrushMixin):
    """Base class for filled rectangle items with no outline."""

    def __init__(
        self,
        p1     : QPointF,
        p2     : Optional[QPointF] = None,
        anchor : Anchor = Anchor.TOP_LEFT,
        wip    : bool = False
    ) -> None:
        super().__init__(p1, p2, anchor, wip)
        self.initBrushSpec()

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(self.brushFromSpec())
        super().paint(painter, option, widget)

class RectPenBrushItem(RectPenOnlyItem, ItemBrushMixin):
    """Base class for rectangle items with pen and brush."""

    def __init__(
        self,
        p1     : QPointF,
        p2     : Optional[QPointF] = None,
        anchor : Anchor = Anchor.TOP_LEFT,
        wip    : bool = False
    ) -> None:
        super().__init__(p1, p2, anchor, wip)
        self.initBrushSpec()

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setPen(self.penFromSpec())
        painter.setBrush(self.brushFromSpec())
        RectBaseItem.paint(self, painter, option, widget)

class TextItem(
    QGraphicsTextItem,
    ItemBasicsMixin,
    ItemTextMixin
):
    """Base class for text items."""

    anchor : Anchor

    def __init__(
        self,
        text   : str = '',
        anchor : Anchor = Anchor.TOP_LEFT,
        wip    : bool = False
    ) -> None:
        super().__init__(self, text)
        self.setZValue(self.Z)
        self.defaultSetup()
        self.setAnchor(anchor)
        self.setWIP(wip)
        self.setTextSpec()

    def setAnchor(self, anchor : Anchor = Anchor.TOP_LEFT) -> None:
        self.anchor = anchor

    def boundingRect(self) -> QRectF:
        rect = super().boundingRect()
        return QRectF(
            -rect.width() * self.anchor.value.h,
            -rect.height() * self.anchor.value.v,
            rect.width(), rect.height()
        )

    def shape(self) -> QPainterPath:
        path = self.shape()
        return path.translate(
            -path.width() * self.anchor.value.h,
            -path.height() * self.anchor.value.v
        )

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        self.updateFont()
        self.setFont(self.font)
        rect = self.anchoredBoundingRect()
        painter.translate(rect.topLeft())
        painter.drawText(
            rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            self.toPlainText()
        )

from .extents    import Extents
from .paper      import Paper
from .border     import Border
from .rectangle  import Rectangle
from .grid       import Grid
