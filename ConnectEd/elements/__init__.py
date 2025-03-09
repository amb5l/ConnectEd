__all__ = [
    'LineSpec',
    'FillSpec',
    'PainterContext',
    'Element',
    'Sheet',
    'Border',
    'Rectangle',
    'Grid',
    'SelectBox'
]

from dataclasses import dataclass
from typing      import ClassVar, Optional
from types       import SimpleNamespace

from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QPainter, QPen, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsView

from ..core import Z_DEFAULT, Z_TOP, settings


@dataclass
class LineSpec:
    color : Optional[QColor]      = None
    width : Optional[float]       = None
    style : Optional[Qt.PenStyle] = None

@dataclass
class FillSpec:
    color : Optional[QColor]        = None
    style : Optional[Qt.BrushStyle] = None

class Element(QGraphicsItem):
    Z        : ClassVar[int] = Z_DEFAULT
    wip      : bool
    selected : bool

    def __init__(self, selected : bool = False, wip : bool = False) -> None:
        super().__init__()
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsMovable                        , True  )
        self.setFlag( f.ItemIsSelectable                     , True  )
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

        self.wip      = wip
        self.selected = selected
        self.setZValue(Z_TOP if self.wip or self.selected else self.Z)

    def setWIP(self, wip : bool) -> None:
        self.wip = wip
        self.setZValue(Z_TOP if self.wip else self.Z)

    def setPenBrush(
        self    : 'Element',
        painter : QPainter,
        prefs   : SimpleNamespace,
        theme   : SimpleNamespace
    ) -> None:
        if self.wip:
            prefs = settings.prefs.display.elements.wip
            theme = settings.theme.elements.wip
        elif self.isSelected():
            prefs = settings.prefs.display.elements.selected
            theme = settings.theme.elements.selected
        w = self.line.width if self.line is not None else prefs.line.width
        painter.setPen(QPen(
            self.line.color if self.line is not None else theme.line,
            w,
            self.line.style if self.line is not None else prefs.line.style
        ))
        painter.setBrush(QBrush(
            self.fill.color if self.fill is not None else theme.fill,
            self.fill.style if self.fill is not None else prefs.fill
        ))

    def setPenOnly(
        self    : 'Element',
        painter : QPainter,
        prefs   : SimpleNamespace,
        theme   : SimpleNamespace
    ) -> None:
        if self.wip:
            prefs = settings.prefs.display.elements.wip
            theme = settings.theme.elements.wip
        elif self.isSelected():
            prefs = settings.prefs.display.elements.selected
            theme = settings.theme.elements.selected
        painter.setPen(QPen(
            self.line.color if self.line is not None else theme.line,
            self.line.width if self.line is not None else prefs.line.width,
            self.line.style if self.line is not None else prefs.line.style
        ))
        painter.setBrush(QBrush(Qt.BrushStyle.NoBrush))

    def setBrushOnly(
        self    : 'Element',
        painter : QPainter,
        prefs   : SimpleNamespace,
        theme   : SimpleNamespace
    ) -> None:
        if self.wip:
            prefs = settings.prefs.display.elements.wip
            theme = settings.theme.elements.wip
        elif self.isSelected():
            prefs = settings.prefs.display.elements.selected
            theme = settings.theme.elements.selected
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.setBrush(QBrush(
            self.fill.color if self.fill.color else theme.fill,
            self.fill.style if self.fill.style else prefs.fill
        ))

from .sheet      import Sheet
from .border     import Border
from .rectangle  import Rectangle
from .grid       import Grid
from .select_box import SelectBox
