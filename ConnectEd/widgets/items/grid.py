from math import ceil

from PyQt6.QtCore    import Qt, QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPen

from ...core import Z_GRID, settings
from ..items import Extents


class Grid(QGraphicsItem):
    Z = Z_GRID

    extents    : 'Extents'
    snap       : bool
    pitch      : QPointF
    dots       : bool
    alpha      : int
    min_pixels : int

    def __init__(self : 'Grid', extents : Extents) -> None:
        super().__init__()
        f = QGraphicsItem.GraphicsItemFlag
        self.setFlag( f.ItemIsMovable                        , False )
        self.setFlag( f.ItemIsSelectable                     , False )
        self.setFlag( f.ItemIsFocusable                      , False )
        self.setFlag( f.ItemClipsToShape                     , False )
        self.setFlag( f.ItemClipsChildrenToShape             , False )
        self.setFlag( f.ItemIgnoresTransformations           , False )
        self.setFlag( f.ItemIgnoresParentOpacity             , False )
        self.setFlag( f.ItemDoesntPropagateOpacityToChildren , False )
        self.setFlag( f.ItemStacksBehindParent               , False )
        self.setFlag( f.ItemUsesExtendedStyleOption          , False )
        self.setFlag( f.ItemHasNoContents                    , False )
        self.setFlag( f.ItemSendsGeometryChanges             , False )
        self.setFlag( f.ItemAcceptsInputMethod               , False )
        self.setFlag( f.ItemNegativeZStacksBehindParent      , False )
        self.setFlag( f.ItemIsPanel                          , False )
        self.setFlag( f.ItemSendsScenePositionChanges        , False )
        self.setFlag( f.ItemContainsChildrenInShape          , False )
        self.setZValue(self.Z)
        self.extents = extents
        self.setVisibile(settings.defaults.grid.display)
        self.snap       = settings.defaults.grid.snap
        self.pitch      = settings.defaults.grid.pitch
        self.dots       = settings.defaults.grid.dots
        self.alpha      = settings.defaults.grid.alpha
        self.min_pixels = settings.defaults.grid.min_pixels

    def boundingRect(self) -> QRectF:
        return self.sheet.boundingRect()

    def paint(
        self    : 'Grid',
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        def align(x : float, px : float) -> float:
            return px * int(x / px)
        view = widget.parent()  # The QGraphicsView
        viewport_rect = view.mapToScene(view.viewport().rect()).boundingRect()
        rect = self.mapFromScene(viewport_rect).boundingRect()
        if self.display:
            pp = view.transform().map(QPointF(self.pitch.x(), self.pitch.y()))
            px = self.pitch.x()
            if pp.x() < self.min_pixels:
                px *= ceil(self.min_pixels / pp.x())
            py = self.pitch.y()
            if pp.y() < self.min_pixels:
                py *= ceil(self.min_pixels / pp.y())
            grect = QRectF(
                rect.topLeft()     - QPointF(px, py),
                rect.bottomRight() + QPointF(px, py)
            ).toRect()
            painter.setPen(QPen(settings.theme.grid, 0, Qt.PenStyle.SolidLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            if self.dots:
                x = align(grect.left(), px)
                while x <= grect.right():
                    y = align(grect.top(), py)
                    while y <= grect.bottom():
                        painter.drawPoint(QPointF(x, y))
                        y += py
                    x += px
            else:
                x = align(grect.left(), px)
                while x <= grect.right():
                    painter.drawLine(
                        QPointF(x, grect.top()),
                        QPointF(x, grect.bottom())
                    )
                    x += px
                y = align(grect.top(), py)
                while y <= grect.bottom():
                    painter.drawLine(
                        QPointF(grect.left(), y),
                        QPointF(grect.right(), y)
                    )
                    y += py