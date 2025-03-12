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
from types       import SimpleNamespace
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

    def getPrefsTheme(self) -> SimpleNamespace:
        item_name = self.__class__.__name__.lower()
        if self.isSelected():
            prefs = settings.prefs.display.items.selected
            theme = settings.theme.selected
        elif self.wip:
            prefs = settings.prefs.display.items.wip
            theme = settings.theme.wip
        else:
            prefs = getattr(settings.prefs.display.items, item_name)
            theme = getattr(settings.theme, item_name)
        return prefs, theme

class ItemPenMixin:
    """Pen support."""

    pen_spec : PenSpec

    def setPenSpec(
        self,
        pen_spec : PenSpec = PenSpec()
    ) -> None:
        self.pen_spec = pen_spec

    def penFromSpec(self) -> None:
        if not hasattr(self, 'pen_spec'):
            return QPen(Qt.PenStyle.NoPen)
        prefs, theme = self.getPrefsTheme()
        s = self.pen_spec
        return QPen(
            theme.line       if s.color is None else s.color,
            prefs.line.width if s.width is None else s.width,
            prefs.line.style if s.style is None else s.style
        )

    def penWidth(self) -> float:
        if not hasattr(self, 'pen_spec'):
            return 0
        prefs, _ = self.getPrefsTheme()
        s = self.pen_spec
        return prefs.line.width if s.width is None else s.width

class ItemBrushMixin:
    """Brush support."""

    brush_spec : BrushSpec

    def setBrushSpec(
        self,
        brush_spec : BrushSpec = BrushSpec()
    ) -> None:
        self.brush_spec = brush_spec

    def brushFromSpec(self) -> None:
        if not hasattr(self, 'brush_spec'):
            return QBrush(Qt.BrushStyle.NoBrush)
        prefs, theme = self.getPrefsTheme()
        s = self.brush_spec
        return QBrush(
            theme.fill if s.color is None else s.color,
            prefs.fill if s.style is None else s.style
        )

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

class RectItem(
    QGraphicsRectItem,
    ItemBasicsMixin,
    ItemPenMixin,
    ItemBrushMixin
):
    """Base class for rectangle items."""

    MIN_SIZE = QSizeF(1.0, 1.0)

    anchor : Anchor

    def __init__(
        self,
        pos     : QPointF,
        size    : QSizeF = QSizeF(0, 0),
        anchor  : Anchor = Anchor.TOP_LEFT,
        wip     : bool = False,
        outline : bool = True,
        fill    : bool = True,
    ) -> None:
        super().__init__()
        self.setPosSize(pos, size)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))
        self.defaultSetup()
        self.setZValue(self.Z)
        self.setAnchor(anchor)
        self.setWIP(wip)
        if outline:
            self.setPenSpec()
        if fill:
            self.setBrushSpec()

    def setPosSize(self, pos : QPointF, size : QSizeF) -> None:
        self.setPos(pos)
        if size.width() < self.MIN_SIZE.width():
            size.setWidth(self.MIN_SIZE.width())
        if size.height() < self.MIN_SIZE.height():
            size.setHeight(self.MIN_SIZE.height())
        self.setRect(0, 0, size.width(), size.height())

    def setPoints(self, p1 : QPointF, p2 : QPointF) -> None:
        rect = QRectF(p1, p2).normalized()
        self.setPosSize(rect.topLeft(), rect.size())

    def setAnchor(self, anchor : Anchor = Anchor.TOP_LEFT) -> None:
        self.anchor = anchor

    def boundingRect(self) -> QRectF:
        w = self.penWidth()
        return super().boundingRect().adjusted(-w/2, -w/2, w/2, w/2)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(
        self,
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setPen(self.penFromSpec())
        painter.setBrush(self.brushFromSpec())
        painter.drawRect(QRectF(
            -self.rect().width() * self.anchor.value.h,
            -self.rect().height() * self.anchor.value.v,
            self.rect().width(),
            self.rect().height()
        ))

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
