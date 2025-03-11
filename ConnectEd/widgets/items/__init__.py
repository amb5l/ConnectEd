__all__ = [
    'Extents',
    'Paper',
    'Border',
    'Rectangle',
    'Grid',
    'SelectBox'
]

from dataclasses import dataclass
from enum        import Enum
from typing      import Optional
from math        import copysign

from PyQt6.QtCore    import Qt, QPointF, QRectF, QSizeF
from PyQt6.QtGui     import QPainter, QPen, QBrush, QColor, QFont
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

class HAnchor(Enum):
    LEFT   = 0.0
    CENTER = 0.5
    RIGHT  = 1.0

class VAnchor(Enum):
    TOP    = 0.0
    CENTER = 0.5
    BOTTOM = 1.0

@dataclass
class Anchor:
    h : HAnchor = HAnchor.LEFT
    v : VAnchor = VAnchor.TOP

class ItemMixin:
    """Base mixin class for all items."""

    def __init__(self) -> None:
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
        self.setCacheMode(QGraphicsItem.CacheMode.NoCache)

class ItemWIPMixin:
    """WIP flag support."""

    wip : bool

    def __init__(self, wip : bool = False) -> None:
        self.setWIP(wip)

    def setWIP(self, wip : bool = True) -> None:
        self.wip = wip

class ItemAnchorMixin:
    """Anchor support."""

    anchor : Anchor

    def __init__(self, anchor : Anchor = Anchor()) -> None:
        self.anchor = anchor

    def setAnchor(self, h : HAnchor = None, v : VAnchor = None) -> None:
        if h is not None:
            self.anchor.h = h
        if v is not None:
            self.anchor.v = v

    def getAnchorOffsetBoundingRect(self) -> QRectF:
        rect = super().boundingRect()
        return QRectF(
            -rect.width() * self.anchor.h,
            -rect.height() * self.anchor.v,
            rect.width(), rect.height()
        )

class ItemRect2Mixin:
    """2 point rectangle support."""

    MIN_SIZE = QSizeF(1.0, 1.0)

    p1 : QPointF
    p2 : QPointF

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

class ItemPenMixin:
    """Pen support."""

    pen_spec : PenSpec
    pen      : QPen

    def __init__(self) -> None:
        self.pen_spec = PenSpec()
        self.pen      = QPen()

    def setPenSpec(
        self,
        color : Optional[QColor]      = None,
        width : Optional[float]       = None,
        style : Optional[Qt.PenStyle] = None
    ) -> None:
        self.pen_spec.color = color
        self.pen_spec.width = width
        self.pen_spec.style = style

    def updatePen(self) -> None:
        item_name = self.__class__.__name__.lower()
        prefs = getattr(settings.prefs.display.items, item_name).line
        theme = getattr(settings.theme, item_name).line
        self.pen.setColor(
            theme.color if self.pen_spec.color is None else
                self.pen_spec.color
        )
        self.pen.setWidth(
            prefs.width if self.pen_spec.width is None else
                self.pen_spec.width
        )
        self.pen.setStyle(
            prefs.style if self.pen_spec.style is None else
                self.pen_spec.style
        )

class ItemBrushMixin:
    """Brush support."""

    brush_spec : BrushSpec
    brush      : QBrush

    def __init__(self) -> None:
        self.brush_spec = BrushSpec()
        self.brush      = QBrush()

    def setBrushSpec(
        self,
        color : Optional[QColor]        = None,
        style : Optional[Qt.BrushStyle] = None
    ) -> None:
        self.brush_spec.color = color
        self.brush_spec.style = style

    def updateBrush(self) -> None:
        item_name = self.__class__.__name__.lower()
        prefs = getattr(settings.prefs.display.items, item_name).fill
        theme = getattr(settings.theme, item_name).fill
        self.brush.setColor(
            theme.color if self.brush_spec.color is None else
                self.brush_spec.color
        )
        self.brush.setStyle(
            prefs.style if self.brush_spec.style is None else
                self.brush_spec.style
        )

class ItemTextMixin:
    """Text/font support."""

    text_spec : TextSpec
    font      : QFont

    def __init__(self) -> None:
        self.text_spec = TextSpec()
        self.font      = QFont()

    def setTextSpec(
        self,
        color : Optional[QColor] = None,
        family : Optional[str] = None,
        size : Optional[float] = None,
        weight : Optional[int] = None,
        italic : Optional[bool] = None,
        underline : Optional[bool] = None
    ) -> None:
        self.text_spec.color     = color
        self.text_spec.family    = family
        self.text_spec.size      = size
        self.text_spec.weight    = weight
        self.text_spec.italic    = italic
        self.text_spec.underline = underline

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

class ItemPenOnlyMixin(ItemPenMixin):
    def __init__(self) -> None:
        super().__init__()

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        self.updatePen()
        self.setPen(self.pen)
        self.setBrush(Qt.BrushStyle.NoBrush)
        super().paint(painter, option, widget)

class ItemBrushOnlyMixin(ItemBrushMixin):
    def __init__(self) -> None:
        super().__init__()

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        self.updateBrush()
        self.setPen(Qt.PenStyle.NoPen)
        self.setBrush(self.brush)
        super().paint(painter, option, widget)

class ItemPenBrushMixin(ItemPenMixin, ItemBrushMixin):
    def __init__(self) -> None:
        super().__init__()

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        self.updatePen()
        self.updateBrush()
        self.setPen(self.pen)
        self.setBrush(self.brush)
        super().paint(painter, option, widget)

class RectBaseItem(
    QGraphicsRectItem,
    ItemMixin,
    ItemAnchorMixin,
    ItemRect2Mixin
):
    """Base class for rectangle items."""

    def __init__(
        self,
        p1     : QPointF,
        p2     : Optional[QPointF] = None,
        anchor : Optional[Anchor] = None
    ) -> None:
        ItemMixin.__init__(self)
        ItemAnchorMixin.__init__(self, anchor)
        ItemRect2Mixin.__init__(self, p1, p2)
        super().__init__(
            self.p1.x(),
            self.p1.y(),
            self.p2.x() - self.p1.x(),
            self.p2.y() - self.p1.y()
        )

    def setPoint2(self, p2 : QPointF) -> None:
        ItemRect2Mixin.setPoint2(self, p2)
        self.setRect(QRectF(self.p1, self.p2))

class RectPenOnlyItem(RectBaseItem, ItemPenOnlyMixin):
    """Base class for unfilled rectangle items."""

    def __init__(
        self,
        p1     : QPointF,
        p2     : Optional[QPointF] = None,
        anchor : Optional[Anchor] = None
    ) -> None:
        super().__init__(p1, p2, anchor)
        ItemPenOnlyMixin.__init__(self)

    def boundingRect(self) -> QRectF:
        item_name = self.__class__.__name__.lower()
        default = getattr(settings.prefs.display.items, item_name).line
        w = default.width if self.pen_spec.width is None else \
            self.pen_spec.width
        margin = w / 2
        return self.rect.adjusted(-margin, -margin, margin, margin)

class RectBrushOnlyItem(RectBaseItem, ItemBrushOnlyMixin):
    """Base class for filled rectangle items with no outline."""

    def __init__(
        self,
        p1     : QPointF,
        p2     : Optional[QPointF] = None,
        anchor : Optional[Anchor] = None
    ) -> None:
        super().__init__(p1, p2, anchor)
        ItemBrushMixin.__init__(self)

    def boundingRect(self) -> QRectF:
        return self.rect

class RectPenBrushItem(RectPenOnlyItem, ItemPenBrushMixin):
    """Base class for rectangle items with pen and brush."""

    def __init__(
        self,
        p1     : QPointF,
        p2     : Optional[QPointF] = None,
        anchor : Optional[Anchor] = None
    ) -> None:
        super().__init__(p1, p2, anchor)
        ItemBrushMixin.__init__(self)

class TextItem(QGraphicsTextItem, ItemMixin, ItemAnchorMixin, ItemTextMixin):
    """Base class for text items."""

    text_spec : TextSpec
    font      : QFont

    def __init__(
        self,
        text : str = '',
        wip  : bool = False
    ) -> None:
        super().__init__(text)
        ItemMixin.__init__(self)
        ItemAnchorMixin.__init__(self)
        ItemTextMixin.__init__(self)

    def boundingRect(self) -> QRectF:
        return self.getAnchorOffsetBoundingRect()

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        self.updateFont()
        self.setFont(self.font)
        rect = self.getAnchorOffsetBoundingRect()
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
from .select_box import SelectBox
