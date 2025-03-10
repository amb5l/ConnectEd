from typing import ClassVar

from PyQt6.QtCore    import Qt, QRectF
from PyQt6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PyQt6.QtGui     import QPainter, QPen, QColor

from ...core import Z_TOP, Rect2

class SelectBox(QGraphicsItem):
    Z    : ClassVar[int] = Z_TOP
    z    : int
    rect : Rect2

    def __init__(self : 'SelectBox', visible : bool = False) -> None:
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
        self.setZValue(Z_TOP)
        self.rect = Rect2()
        self.setVisible(visible)

    def boundingRect(self) -> QRectF:
        return self.rect

    def paint(
        self    : 'SelectBox',
        painter : QPainter,
        option  : QStyleOptionGraphicsItem,
        widget  : QWidget
    ) -> None:
        painter.setCompositionMode(
            QPainter.CompositionMode.RasterOp_SourceXorDestination
        )
        painter.setPen(QPen(QColor(255, 255, 255), 0, Qt.PenStyle.DotLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.drawRect(self.rect)
